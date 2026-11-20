#!/usr/bin/env python3
"""Construit l'entrepôt « feux de forêt » à partir des silos bronze.

Couches (voir docs/modele/modele-cible.md) :
  bronze  data/bronze/<source>/<extraction>/   fichiers tels que collectés (hors Git)
  raw     schéma raw            contenu des fichiers, en texte, + traçabilité
  staging schéma staging        une source à la fois : typer, renommer, dédoublonner, minimiser
  interm. schéma intermediate   correspondances, consolidation, règles métier
  qualité schéma qualite        résultats des règles de qualité à chaque exécution

Usage :
  python pipeline/construire_entrepot.py                 # construit / met à jour
  python pipeline/construire_entrepot.py --idempotence   # recharge tout une 2e fois et compare (Q-PIP-01)

Le script est rejouable : un fichier déjà chargé (même empreinte SHA-256) est ignoré,
un fichier rechargé remplace ses propres lignes, jamais celles des autres.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import shutil
import sys
import time
import uuid
import zipfile
from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
BRONZE = RACINE / "data" / "bronze"
TMP = RACINE / "data" / "tmp"
BASE = RACINE / "data" / "entrepot" / "feux_de_foret.duckdb"

TECH = ["_id_chargement", "_fichier_source", "_fichier_logique", "_empreinte_fichier",
        "_ligne_source", "_date_chargement"]


BINAIRES = {"geometrie_wkb"}  # géométries telles que livrées, en WKB (Lambert 93, EPSG:2154)


class Bloquant(Exception):
    """Une règle de qualité « bloquer » a échoué : on n'alimente pas la couche suivante."""


# --------------------------------------------------------------------------- utilitaires

def log(msg: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def sha256(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def dernier_silo(source: str) -> Path:
    """Dossier d'extraction le plus récent d'une source (les dossiers sont datés)."""
    dossiers = sorted(p for p in (BRONZE / source).iterdir() if p.is_dir())
    if not dossiers:
        raise FileNotFoundError(f"Aucun silo pour {source} dans {BRONZE}")
    return dossiers[-1]


def ident(nom: str) -> str:
    return '"' + nom.replace('"', '""') + '"'


# --------------------------------------------------------------------------- raw

def initialiser(con: duckdb.DuckDBPyConnection) -> None:
    for s in ("raw", "staging", "intermediate", "marts", "qualite"):
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {s}")
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw._journal_chargement (
            id_chargement VARCHAR, source VARCHAR, fichier VARCHAR, membre VARCHAR,
            table_cible VARCHAR, empreinte_sha256 VARCHAR, taille_octets BIGINT,
            lignes_annoncees BIGINT, lignes_lues BIGINT, lignes_inserees BIGINT,
            lignes_rejetees BIGINT, debut TIMESTAMP, fin TIMESTAMP, statut VARCHAR,
            message VARCHAR)""")
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw._rejets_chargement (
            id_chargement VARCHAR, fichier VARCHAR, ligne_source BIGINT,
            contenu VARCHAR, motif VARCHAR)""")
    con.execute("""
        CREATE TABLE IF NOT EXISTS qualite.resultats_tests (
            id_execution VARCHAR, execute_le TIMESTAMP, couche VARCHAR, id_regle VARCHAR,
            dimension VARCHAR, enonce VARCHAR, decision VARCHAR, nb_en_faute BIGINT,
            seuil VARCHAR, statut VARCHAR)""")


class Chargeur:
    """Charge un fichier (ou un membre d'archive) dans une table raw, de façon idempotente."""

    def __init__(self, con, forcer: bool = False):
        self.con = con
        self.forcer = forcer

    def deja_charge(self, empreinte: str, membre: str, table: str) -> bool:
        n = self.con.execute(
            "SELECT count(*) FROM raw._journal_chargement WHERE empreinte_sha256=? "
            "AND coalesce(membre,'')=? AND table_cible=? AND statut='succès'",
            [empreinte, membre or "", table]).fetchone()[0]
        return n > 0

    def charger(self, source: str, table: str, fichier: Path, lignes: list[dict],
                lignes_num: list[int], membre: str | None = None,
                rejets: list[tuple[int, str, str]] | None = None,
                annoncees: int | None = None, message: str | None = None,
                empreinte: str | None = None) -> None:
        rejets = rejets or []
        debut = datetime.now()
        id_ch = uuid.uuid4().hex[:12]
        empreinte = empreinte or sha256(fichier)
        rel = fichier.relative_to(BRONZE).as_posix()
        logique = f"{source}/{fichier.name}" + (f"!{membre}" if membre else "")
        cible = f"raw.{table}"
        journal = [id_ch, source, rel, membre, cible, empreinte, fichier.stat().st_size,
                   annoncees, len(lignes) + len(rejets)]

        if not self.forcer and self.deja_charge(empreinte, membre, cible):
            self.con.execute("INSERT INTO raw._journal_chargement VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                             journal + [0, 0, debut, datetime.now(), "ignoré",
                                        "empreinte déjà chargée"])
            return

        if isinstance(lignes, pd.DataFrame):
            colonnes = list(lignes.columns)
            df = lignes.astype(object).copy()
        else:
            colonnes = list(dict.fromkeys(k for l in lignes for k in l)) if lignes else []
            df = pd.DataFrame(lignes, columns=colonnes, dtype=object)
        texte = [c for c in colonnes if c not in BINAIRES]
        df[texte] = df[texte].where(df[texte].notna() & (df[texte] != ""), None)
        df["_id_chargement"] = id_ch
        df["_fichier_source"] = rel
        df["_fichier_logique"] = logique
        df["_empreinte_fichier"] = empreinte
        df["_ligne_source"] = lignes_num
        df["_date_chargement"] = debut

        self.con.execute("BEGIN TRANSACTION")
        try:
            existe = self.con.execute(
                "SELECT count(*) FROM information_schema.tables WHERE table_schema='raw' AND table_name=?",
                [table]).fetchone()[0]
            if not existe:
                defs = ", ".join(f"{ident(c)} {'BLOB' if c in BINAIRES else 'VARCHAR'}" for c in colonnes)
                defs += (", " if defs else "") + (
                    '"_id_chargement" VARCHAR, "_fichier_source" VARCHAR, "_fichier_logique" VARCHAR, '
                    '"_empreinte_fichier" VARCHAR, "_ligne_source" BIGINT, "_date_chargement" TIMESTAMP')
                self.con.execute(f"CREATE TABLE {cible} ({defs})")
            else:
                presentes = {r[0] for r in self.con.execute(
                    "SELECT column_name FROM information_schema.columns WHERE table_schema='raw' AND table_name=?",
                    [table]).fetchall()}
                for c in colonnes:
                    if c not in presentes:  # schéma qui évolue (ex. nom_dep → dep_nom) : on ajoute, on ne perd rien
                        self.con.execute(f"ALTER TABLE {cible} ADD COLUMN {ident(c)} {'BLOB' if c in BINAIRES else 'VARCHAR'}")
            self.con.execute(f"DELETE FROM {cible} WHERE _fichier_logique = ?", [logique])
            if len(df):
                self.con.register("_df", df)
                self.con.execute(f"INSERT INTO {cible} BY NAME SELECT * FROM _df")
                self.con.unregister("_df")
            if rejets:
                self.con.executemany("INSERT INTO raw._rejets_chargement VALUES (?,?,?,?,?)",
                                     [[id_ch, rel, n, c, m] for n, c, m in rejets])
            statut = "succès"
            self.con.execute("INSERT INTO raw._journal_chargement VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                             journal + [len(df), len(rejets), debut, datetime.now(), statut, message])
            self.con.execute("COMMIT")
        except Exception as e:
            self.con.execute("ROLLBACK")
            self.con.execute("INSERT INTO raw._journal_chargement VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                             journal + [0, 0, debut, datetime.now(), "échec", str(e)[:500]])
            raise


# --- lecteurs par source ---------------------------------------------------------

def lire_csv(texte: str, debut_ligne: int, sep: str):
    lecteur = csv.reader(io.StringIO(texte), delimiter=sep)
    entete = next(lecteur)
    lignes, nums, rejets = [], [], []
    for i, ligne in enumerate(lecteur):
        n = debut_ligne + 1 + i
        if len(ligne) != len(entete):
            rejets.append((n, sep.join(ligne)[:500], f"{len(ligne)} champs au lieu de {len(entete)}"))
            continue
        lignes.append(dict(zip(entete, ligne)))
        nums.append(n)
    return lignes, nums, rejets


def charger_meteo_des_forets(ch: Chargeur) -> None:
    silo = dernier_silo("meteo_des_forets")
    for f in sorted(silo.glob("mdf_*.csv.gz")):
        texte = gzip.decompress(f.read_bytes()).decode("utf-8")
        sep = ";" if ";" in texte.splitlines()[0] else ","
        lignes, nums, rejets = lire_csv(texte, 1, sep)
        ch.charger("meteo_des_forets", "mdf_bulletins", f, lignes, nums, rejets=rejets,
                   message=f"séparateur '{sep}'")
    for f in sorted(silo.glob("*departements*.geojson")):
        g = json.loads(f.read_text(encoding="utf-8"))
        lignes = [{**{k: (None if v is None else str(v)) for k, v in ft["properties"].items()},
                   "geometrie_geojson": json.dumps(ft["geometry"])} for ft in g["features"]]
        ch.charger("meteo_des_forets", "mdf_departements_geo", f, lignes, list(range(1, len(lignes) + 1)))


def charger_bdiff(ch: Chargeur) -> None:
    silo = dernier_silo("bdiff")
    for f in sorted(silo.glob("bdiff_*.zip")):
        brut = zipfile.ZipFile(f).read("Incendies.csv").decode("utf-8")
        L = brut.splitlines()
        h = next(i for i, l in enumerate(L) if l.startswith("Année;"))
        entete = L[:h]
        annoncees = int(re.search(r": (\d+)", next(l for l in entete if "Nombre" in l)).group(1))
        criteres = next((l for l in entete if l.startswith('"Critères')), "")
        notes = [l for l in entete if l.startswith('"') and " - " in l.split(";")[0]]
        lignes, nums, rejets = lire_csv("\n".join(L[h:]), h + 1, ";")
        ch.charger("bdiff", "bdiff_incendies", f, lignes, nums, membre="Incendies.csv", rejets=rejets,
                   annoncees=annoncees, message=criteres.replace('"', "")[:500])
        # « A noter » : campagnes sans données signalées par la source (complétude de population)
        ln = []
        for l in notes:
            cle, _, txt = l.partition(";")
            m = re.match(r'"?(\d{4}) - (\w+)', cle)
            ln.append({"annee": m.group(1) if m else None, "departement": m.group(2) if m else None,
                       "note": txt.strip('"'), "texte_brut": l})
        ch.charger("bdiff", "bdiff_notes_campagnes", f, ln,
                   [L.index(l) + 1 for l in notes], membre="Incendies.csv#notes")


def charger_cog(ch: Chargeur) -> None:
    silo = dernier_silo("cog")
    for f in sorted(silo.glob("cog_ensemble_*_csv.zip")):
        z = zipfile.ZipFile(f)
        empreinte = sha256(f)
        for membre in sorted(z.namelist()):
            if not membre.endswith(".csv"):
                continue
            table = "cog_" + re.sub(r"^v_|_\d{4}$", "", Path(membre).stem)
            lignes, nums, rejets = lire_csv(z.read(membre).decode("utf-8"), 1, ",")
            ch.charger("cog", table, f, lignes, nums, membre=membre, rejets=rejets, empreinte=empreinte)


def extraire_7z(archive: Path) -> Path:
    import py7zr
    cible = TMP / archive.stem
    if not cible.exists():
        with py7zr.SevenZipFile(archive) as z:
            z.extractall(cible)
    return cible


def lire_couche(chemin: Path, couche: str | None = None):
    """Attributs (texte) et géométrie (WKB, telle que livrée) d'une couche vectorielle."""
    from pyogrio.raw import read
    meta, _, geom, champs = read(str(chemin), layer=couche)
    noms = list(meta["fields"])
    n = len(geom) if geom is not None else (len(champs[0]) if champs else 0)
    lignes = [{**{noms[j]: (None if champs[j][i] is None else str(champs[j][i])) for j in range(len(noms))},
               "geometrie_wkb": None if geom is None or geom[i] is None else bytes(geom[i])}
              for i in range(n)]
    return lignes, meta.get("crs")


def charger_bd_foret(ch: Chargeur) -> None:
    silo = dernier_silo("bd_foret_v2")
    for f in sorted(silo.glob("BDFORET_2-0__SHP_*.7z")):
        d = extraire_7z(f)
        shp = next(d.rglob("FORMATION_VEGETALE.shp"))
        dep = re.search(r"_D0?(\w{2,3})_", f.name).group(1)
        edition = re.search(r"_(\d{4}-\d{2}-\d{2})\.7z$", f.name).group(1)
        couche, crs = lire_couche(shp)
        lignes = [{**l, "departement_livraison": dep, "edition": edition} for l in couche]
        ch.charger("bd_foret_v2", "bd_foret_formations", f, lignes, list(range(1, len(lignes) + 1)),
                   membre="FORMATION_VEGETALE.shp", message=f"{len(lignes)} polygones, {crs}")
        xml = next(d.rglob("IGNF_BDF_*.xml")).read_text(encoding="utf-8", errors="replace")
        meta = {"departement_livraison": dep, "edition": edition,
                "debut_realite": (re.findall(r"beginPosition>([^<]*)", xml) or [None])[0],
                "fin_realite": (re.findall(r"endPosition>([^<]*)", xml) or [None])[0]}
        ch.charger("bd_foret_v2", "bd_foret_metadonnees", f, [meta], [1], membre="metadonnees.xml")


def gpkg_admin_express() -> tuple[Path, Path]:
    silo = dernier_silo("admin_express_cog")
    archive = next(silo.glob("ADMIN-EXPRESS-COG_*.7z"))
    return archive, next(extraire_7z(archive).rglob("*.gpkg"))


def charger_admin_express(ch: Chargeur) -> None:
    archive, gpkg = gpkg_admin_express()
    empreinte = sha256(archive)
    for couche in ("commune", "departement", "region", "arrondissement_municipal"):
        lignes, crs = lire_couche(gpkg, couche)
        ch.charger("admin_express_cog", f"admin_express_{couche}", archive, lignes,
                   list(range(1, len(lignes) + 1)), membre=couche, empreinte=empreinte, message=str(crs))


def charger_dgscgc(ch: Chargeur) -> None:
    """Statistiques annuelles des interventions des SIS (DGSCGC), une ligne par SIS et par an."""
    for f in sorted(dernier_silo("dgscgc_interventions_sis").glob("dgscgc_interventions_SIS_*.csv")):
        lignes, nums, rejets = lire_csv(f.read_bytes().decode("cp1252"), 1, ";")
        ch.charger("dgscgc_interventions_sis", "dgscgc_interventions_sis", f, lignes, nums, rejets=rejets,
                   message="encodage cp1252 ; le schéma change selon les années")


METEO_COLONNES = ["NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI", "AAAAMMJJ", "RR", "QRR", "TN", "QTN",
                  "TX", "QTX", "FFM", "QFFM", "FXI", "QFXI"]


def charger_meteo_quotidien(ch: Chargeur) -> None:
    """Données climatologiques quotidiennes (Météo-France), toutes les stations du département.
    Seules les 16 colonnes utiles sont chargées (température, pluie, vent et leurs codes qualité)."""
    for f in sorted(dernier_silo("meteo_france_quotidien").glob("Q_*_RR-T-Vent.csv.gz")):
        df = pd.read_csv(f, sep=";", dtype=str, usecols=METEO_COLONNES, keep_default_na=False)
        ch.charger("meteo_france_quotidien", "meteo_quotidien", f, df[METEO_COLONNES],
                   list(range(2, len(df) + 2)), message="16 colonnes sur 60 (minimisation)")


def charger_gaspar(ch: Chargeur) -> None:
    """GASPAR (Géorisques) : seul le fichier des risques par commune (DDRM) sert le projet."""
    f = next(dernier_silo("gaspar").glob("gaspar.zip"))
    z = zipfile.ZipFile(f)
    m = next(n for n in sorted(z.namelist()) if n.startswith("ddrm_risq"))
    lignes, nums, rejets = lire_csv(z.read(m).decode("utf-8"), 1, ";")
    ch.charger("gaspar", "gaspar_ddrm_risques", f, lignes, nums, membre=m, rejets=rejets)


def charger_geojson(ch: Chargeur, source: str, table: str) -> None:
    for f in sorted(dernier_silo(source).glob("*.geojson")):
        g = json.loads(f.read_text(encoding="utf-8"))
        lignes = [{**{k: (None if v is None else str(v)) for k, v in ft["properties"].items()},
                   "geometrie_geojson": json.dumps(ft["geometry"])} for ft in g["features"]]
        ch.charger(source, table, f, lignes, list(range(1, len(lignes) + 1)))


def charger_presse(ch: Chargeur) -> None:
    """Chiffres 2026 du SDMIS relayés par la presse : proxy temporaire, confiance faible (manque M-2)."""
    for f in sorted(dernier_silo("presse").glob("*.csv")):
        lignes, nums, rejets = lire_csv(f.read_text(encoding="utf-8"), 1, ";")
        ch.charger("presse", "presse_chiffres_2026", f, lignes, nums, rejets=rejets)


def charger_raw(con, forcer=False) -> None:
    ch = Chargeur(con, forcer)
    for nom, fn in [("Météo des forêts", charger_meteo_des_forets), ("BDIFF", charger_bdiff),
                    ("COG", charger_cog), ("BD Forêt V2", charger_bd_foret),
                    ("ADMIN EXPRESS COG", charger_admin_express),
                    ("Interventions des SIS (DGSCGC)", charger_dgscgc),
                    ("Météo-France quotidien", charger_meteo_quotidien),
                    ("GASPAR", charger_gaspar),
                    ("Casernes SDMIS", lambda c: charger_geojson(c, "sdmis_casernes", "sdmis_casernes")),
                    ("Presse 2026", charger_presse)]:
        log(f"raw : {nom}")
        fn(ch)


# --------------------------------------------------------------------------- staging

STAGING = {
"stg_mdf__bulletins": r"""
WITH src AS (
  SELECT *, row_number() OVER (PARTITION BY lpad(trim(num_dep),2,'0'), "date" ORDER BY _date_chargement DESC) AS rn
  FROM raw.mdf_bulletins)
SELECT lpad(trim(num_dep),2,'0')                                 AS code_departement,
       CAST("date" AS TIMESTAMPTZ)                               AS horodatage_emission_utc,
       CAST(timezone('Europe/Paris', CAST("date" AS TIMESTAMPTZ)) AS DATE) AS date_emission,
       CAST(niveau_j1 AS INTEGER)                                AS niveau_j1,
       CAST(niveau_j2 AS INTEGER)                                AS niveau_j2,
       CAST(regexp_extract(_fichier_source, 'mdf_(\d{4})', 1) AS INTEGER) AS millesime_fichier,
       _fichier_source, _ligne_source
FROM src WHERE rn = 1""",

"stg_bdiff__feux": r"""
WITH src AS (
  SELECT *, row_number() OVER (PARTITION BY "Année", "Numéro" ORDER BY _date_chargement DESC) AS rn
  FROM raw.bdiff_incendies)
SELECT "Année" || '-' || "Numéro"                         AS id_feu_bdiff,
       CAST("Année" AS INTEGER)                           AS annee,
       CAST("Numéro" AS BIGINT)                           AS numero_fiche,
       "Département"                                      AS code_departement,
       "Code INSEE"                                       AS code_commune_origine,
       CAST("Date de première alerte" AS TIMESTAMP)       AS horodatage_alerte,
       CAST("Date de première alerte" AS DATE)            AS date_alerte,
       CAST("Surface parcourue (m2)" AS BIGINT)           AS surface_parcourue_m2,
       CAST("Surface forêt (m2)" AS BIGINT)               AS surface_foret_m2,
       "Précision des surfaces"                           AS precision_surfaces,
       "Type de peuplement"                               AS type_peuplement_code,
       CASE "Type de peuplement" WHEN '1' THEN 'Landes, garrigues, maquis' WHEN '2' THEN 'Taillis'
            WHEN '3' THEN 'Futaies feuillues' WHEN '4' THEN 'Futaies résineuses'
            WHEN '5' THEN 'Futaies mélangées' WHEN '6' THEN 'Régénération et reboisement' END
                                                          AS type_peuplement_libelle,
       "Nature"                                           AS cause_nature,
       "Précision de la donnée"                           AS precision_donnee,
       _fichier_source, _ligne_source
FROM src WHERE rn = 1""",

"stg_bdiff__notes_campagnes": r"""
SELECT DISTINCT CAST(annee AS INTEGER) AS annee, departement AS code_departement, note,
       _fichier_source
FROM raw.bdiff_notes_campagnes""",

"stg_cog__codes_commune": r"""
SELECT COM AS code, TYPECOM AS typecom, DEP AS code_departement, REG AS code_region,
       CTCD AS code_ctcd, LIBELLE AS libelle, nullif(COMPARENT,'') AS code_commune_parent,
       2026 AS millesime_cog
FROM raw.cog_commune""",

"stg_cog__communes": r"""
SELECT code AS code_commune, code_departement, code_region, code_ctcd, libelle AS libelle_commune,
       millesime_cog
FROM staging.stg_cog__codes_commune WHERE typecom = 'COM'""",

"stg_cog__departements": r"""
SELECT DEP AS code_departement, REG AS code_region, LIBELLE AS libelle_departement,
       CHEFLIEU AS code_commune_cheflieu
FROM raw.cog_departement""",

"stg_cog__regions": r"""
SELECT REG AS code_region, LIBELLE AS libelle_region FROM raw.cog_region""",

"stg_cog__mouvements": r"""
SELECT CAST(MOD AS INTEGER) AS mod, CAST(DATE_EFF AS DATE) AS date_effet,
       TYPECOM_AV AS typecom_avant, COM_AV AS code_commune_avant,
       TYPECOM_AP AS typecom_apres, COM_AP AS code_commune_apres
FROM raw.cog_mvt_commune""",

"stg_admin_express__communes": r"""
SELECT code_insee AS code_commune, CAST(population AS BIGINT) AS population,
       CAST(substr(date_du_recensement,1,10) AS DATE) AS date_recensement,
       code_insee_du_departement AS code_departement
FROM raw.admin_express_commune""",

"stg_bd_foret__formations": r"""
SELECT "ID" AS id_formation, departement_livraison AS code_departement, "CODE_TFV" AS code_tfv,
       "TFV" AS libelle_tfv, "TFV_G11" AS groupe_tfv, "ESSENCE" AS essence,
       CASE WHEN "CODE_TFV" LIKE 'FF%' OR "CODE_TFV" LIKE 'FO%' OR "CODE_TFV" LIKE 'FP%' THEN 'forêt'
            WHEN "TFV_G11" = 'Lande' THEN 'lande'
            WHEN "TFV_G11" = 'Formation herbacée' THEN 'formation herbacée' END AS categorie,
       CAST(edition AS DATE) AS edition, _fichier_source
FROM raw.bd_foret_formations""",

"stg_bd_foret__geometries": r"""
SELECT "ID" AS id_formation, departement_livraison AS code_departement, geometrie_wkb, _fichier_source
FROM raw.bd_foret_formations""",

"stg_admin_express__geometries_communes": r"""
SELECT code_insee AS code_commune, code_insee_du_departement AS code_departement, geometrie_wkb
FROM raw.admin_express_commune""",

"stg_dgscgc__interventions_sis": r"""
WITH src AS (
  SELECT *, row_number() OVER (PARTITION BY "Année", "Numéro" ORDER BY _date_chargement DESC) AS rn
  FROM raw.dgscgc_interventions_sis)
SELECT CAST("Année" AS INTEGER)                                         AS annee,
       "Numéro"                                                         AS code_sis,
       CASE WHEN "Numéro" = 'BSPP' THEN '75' WHEN "Numéro" = 'BMPM' THEN '13'
            WHEN regexp_matches("Numéro", '^[0-9]$') THEN lpad("Numéro", 2, '0') ELSE "Numéro" END AS code_departement,
       ("Numéro" IN ('BSPP', 'BMPM'))                                   AS sis_hors_sdis,
       "Département"                                                    AS libelle_departement_source,
       TRY_CAST(nullif(regexp_replace("Feux de végétations", '[^0-9]', '', 'g'), '') AS INTEGER) AS feux_vegetation,
       TRY_CAST(nullif(regexp_replace("Incendies", '[^0-9]', '', 'g'), '') AS INTEGER)           AS incendies,
       TRY_CAST(nullif(regexp_replace("Total interventions", '[^0-9]', '', 'g'), '') AS INTEGER) AS total_interventions,
       _fichier_source
FROM src WHERE rn = 1""",

"stg_meteo__quotidien": r"""
WITH src AS (
  SELECT *, row_number() OVER (PARTITION BY NUM_POSTE, AAAAMMJJ ORDER BY _date_chargement DESC) AS rn
  FROM raw.meteo_quotidien)
SELECT NUM_POSTE AS code_station, NOM_USUEL AS nom_station,
       TRY_CAST(LAT AS DOUBLE) AS lat, TRY_CAST(LON AS DOUBLE) AS lon, TRY_CAST(ALTI AS INTEGER) AS altitude_m,
       CAST(strptime(AAAAMMJJ, '%Y%m%d') AS DATE) AS date,
       TRY_CAST(RR AS DOUBLE) AS pluie_mm, QRR AS qualite_pluie,
       TRY_CAST(TN AS DOUBLE) AS tmin_c, TRY_CAST(TX AS DOUBLE) AS tmax_c, QTX AS qualite_tmax,
       TRY_CAST(FFM AS DOUBLE) AS vent_moyen_ms, TRY_CAST(FXI AS DOUBLE) AS rafale_max_ms,
       _fichier_source
FROM src WHERE rn = 1""",

"stg_gaspar__risques_communes": r"""
SELECT DISTINCT cod_commune AS code_commune, lib_risque AS risque, num_risque AS code_risque
FROM raw.gaspar_ddrm_risques""",

"stg_sdmis__casernes": r"""
SELECT CAST(numero_identification AS INTEGER) AS id_site, nom_officiel_site AS nom_site, cis, groupement,
       commune, referencement AS territoire,
       CAST(json_extract(geometrie_geojson, '$.coordinates[0]') AS DOUBLE) AS lon,
       CAST(json_extract(geometrie_geojson, '$.coordinates[1]') AS DOUBLE) AS lat
FROM raw.sdmis_casernes""",

"stg_presse__chiffres_2026": r"""
SELECT CAST(date_publication AS DATE) AS date_publication, CAST(date_reference AS DATE) AS date_reference,
       perimetre, indicateur, CAST(valeur AS DOUBLE) AS valeur, unite, source_citee, media, url
FROM raw.presse_chiffres_2026""",

"stg_bd_foret__metadonnees": r"""
SELECT DISTINCT departement_livraison AS code_departement, CAST(edition AS DATE) AS edition,
       CAST(debut_realite AS DATE) AS debut_realite, CAST(fin_realite AS DATE) AS fin_realite
FROM raw.bd_foret_metadonnees""",
}


def construire_staging(con) -> None:
    for nom, sql in STAGING.items():
        # les géométries ne sont pas recopiées : vue sur raw (évite de doubler 1,5 Go)
        genre = "VIEW" if nom.endswith("geometries") or "geometries_" in nom else "TABLE"
        existant = con.execute("SELECT table_type FROM information_schema.tables "
                               "WHERE table_schema='staging' AND table_name=?", [nom]).fetchone()
        if existant:
            con.execute(f"DROP {'VIEW' if existant[0] == 'VIEW' else 'TABLE'} staging.{nom}")
        con.execute(f"CREATE {genre} staging.{nom} AS {sql}")
    log(f"staging : {len(STAGING)} tables")


# --------------------------------------------------------------------------- intermédiaire

def table_de_passage(con) -> None:
    """Code commune d'origine (année du feu) -> code COG 2026, généré depuis le COG (jamais à la main)."""
    codes = con.execute("SELECT code, typecom, code_commune_parent FROM staging.stg_cog__codes_commune").fetchall()
    com = {c for c, t, _ in codes if t == "COM"}
    arm = {c: p for c, t, p in codes if t == "ARM"}
    mvt = {}
    for av, ap, mod in con.execute("""SELECT code_commune_avant, code_commune_apres, mod
                                      FROM staging.stg_cog__mouvements
                                      WHERE typecom_apres='COM' AND code_commune_apres<>code_commune_avant""").fetchall():
        mvt.setdefault(av, set()).add((ap, mod))
    origines = [r[0] for r in con.execute(
        "SELECT DISTINCT code_commune_origine FROM staging.stg_bdiff__feux WHERE code_commune_origine IS NOT NULL").fetchall()]

    def suivre(code, vus=frozenset()):
        if code in com:
            return {code}, set()
        if code in vus:
            return set(), set()
        dest, mods = set(), set()
        for ap, mod in mvt.get(code, ()):
            d, m = suivre(ap, vus | {code})
            dest |= d
            mods |= m | {mod}
        return dest, mods

    lignes = []
    for o in origines:
        if o in com:
            lignes.append((o, o, "identique", None, None))
        elif o in arm:
            lignes.append((o, arm[o], "arrondissement municipal", None, None))
        else:
            dest, mods = suivre(o)
            m = ",".join(str(x) for x in sorted(mods)) or None
            if len(dest) == 1:
                lignes.append((o, dest.pop(), "mouvement", m, None))
            elif len(dest) > 1:
                lignes.append((o, None, "ambigu", m, f"{len(dest)} communes 2026 possibles"))
            elif o.endswith("999"):
                lignes.append((o, None, "introuvable", m, "code « commune inconnue » (xx999) saisi dans la source"))
            else:
                lignes.append((o, None, "introuvable", m, "code absent du COG 2026 et des mouvements"))
    df = pd.DataFrame(lignes, columns=["code_commune_origine", "code_commune_cog2026", "regle",
                                       "mods_appliques", "motif_rejet"])
    con.register("_passage", df)
    con.execute("CREATE OR REPLACE TABLE intermediate.int_territoire__passage_communes AS "
                "SELECT *, 2026 AS millesime_cog FROM _passage")
    con.unregister("_passage")


INTERMEDIATE = {
"int_territoire__communes": r"""
SELECT c.code_commune, c.libelle_commune, c.code_departement, d.libelle_departement,
       c.code_region, r.libelle_region, c.code_ctcd,
       (c.code_departement = '69') AS perimetre_sdmis,
       ae.population, ae.date_recensement, c.millesime_cog
FROM staging.stg_cog__communes c
LEFT JOIN staging.stg_cog__departements d USING (code_departement)
LEFT JOIN staging.stg_cog__regions r ON r.code_region = c.code_region
LEFT JOIN staging.stg_admin_express__communes ae USING (code_commune)""",

"int_bdiff__feux_rattaches": r"""
SELECT md5('BDIFF|' || f.id_feu_bdiff) AS feu_sk, 'BDIFF' AS source, f.*,
       p.code_commune_cog2026, p.regle AS regle_rattachement, t.code_ctcd, t.code_region
FROM staging.stg_bdiff__feux f
JOIN intermediate.int_territoire__passage_communes p USING (code_commune_origine)
JOIN staging.stg_cog__communes t ON t.code_commune = p.code_commune_cog2026""",

"int_bdiff__feux_rejets": r"""
SELECT f.*, coalesce(p.motif_rejet, 'code commune sans correspondance') AS motif_rejet
FROM staging.stg_bdiff__feux f
LEFT JOIN intermediate.int_territoire__passage_communes p USING (code_commune_origine)
WHERE p.code_commune_cog2026 IS NULL""",

"int_mdf__danger_jour": r"""
WITH j1 AS (SELECT code_departement, date_emission + 1 AS jour_cible, niveau_j1, date_emission AS date_emission_j1
            FROM staging.stg_mdf__bulletins),
     j2 AS (SELECT code_departement, date_emission + 2 AS jour_cible, niveau_j2, date_emission AS date_emission_j2
            FROM staging.stg_mdf__bulletins)
SELECT code_departement, jour_cible, niveau_j1, date_emission_j1, niveau_j2, date_emission_j2,
       niveau_j1 AS niveau_reference, 'J+1 de la veille, sans comblement' AS regle
FROM j1 FULL OUTER JOIN j2 USING (code_departement, jour_cible)""",

"int_feux__danger": r"""
SELECT md5('BDIFF|' || f.id_feu_bdiff) AS feu_sk, f.id_feu_bdiff, f.code_departement,
       r.code_commune_cog2026, (r.feu_sk IS NOT NULL) AS rattache_commune, f.date_alerte,
       f.surface_parcourue_m2, d.niveau_reference, d.niveau_j1, d.niveau_j2,
       CASE WHEN d.niveau_reference IS NOT NULL THEN 'niveau disponible'
            WHEN year(f.date_alerte) < 2024 THEN 'année sans bulletin'
            WHEN f.code_departement NOT IN (SELECT DISTINCT code_departement FROM staging.stg_mdf__bulletins)
                 THEN 'département hors Météo des forêts'
            ELSE 'hors saison du bulletin' END AS statut_bulletin
FROM staging.stg_bdiff__feux f
LEFT JOIN intermediate.int_bdiff__feux_rattaches r USING (id_feu_bdiff)
LEFT JOIN intermediate.int_mdf__danger_jour d
       ON d.code_departement = f.code_departement AND d.jour_cible = f.date_alerte""",
}


INTERMEDIATE_SUITE = {
# Jour de chaleur sèche à Lyon-Bron : TX >= 30 °C et moins de 1 mm de pluie sur les 10 derniers jours.
# Contexte de long terme seulement : la Météo des forêts tient aussi compte de l'état de la végétation.
"int_meteo__jours_lyon_bron": r"""
WITH b AS (
  SELECT date, tmax_c, pluie_mm, vent_moyen_ms,
         sum(pluie_mm) OVER (ORDER BY date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW)  AS pluie_10j_mm,
         count(pluie_mm) OVER (ORDER BY date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS nb_pluie_10j
  FROM staging.stg_meteo__quotidien WHERE code_station = '69029001')
SELECT b.*, (tmax_c >= 30 AND nb_pluie_10j = 10 AND pluie_10j_mm < 1) AS chaleur_seche,
       (tmax_c >= 30) AS jour_tx30, d.niveau_j1 AS niveau_mdf_69
FROM b LEFT JOIN intermediate.int_mdf__danger_jour d ON d.code_departement = '69' AND d.jour_cible = b.date""",

"int_sdis__feux_vegetation": r"""
WITH bdiff AS (SELECT code_departement, annee, count(*) AS feux_bdiff,
                      count(*) FILTER (WHERE surface_parcourue_m2 >= 10000) AS feux_bdiff_1ha
               FROM staging.stg_bdiff__feux GROUP BY ALL)
SELECT s.annee, s.code_sis, s.code_departement, s.sis_hors_sdis, s.feux_vegetation, s.incendies,
       s.total_interventions, coalesce(b.feux_bdiff, 0) AS feux_bdiff, coalesce(b.feux_bdiff_1ha, 0) AS feux_bdiff_1ha
FROM staging.stg_dgscgc__interventions_sis s
LEFT JOIN bdiff b ON b.code_departement = s.code_departement AND b.annee = s.annee AND NOT s.sis_hors_sdis""",

"int_territoire__risque_feu_communes": r"""
SELECT c.code_commune, (g.code_commune IS NOT NULL) AS risque_feu_ddrm
FROM staging.stg_cog__communes c
LEFT JOIN (SELECT DISTINCT code_commune FROM staging.stg_gaspar__risques_communes WHERE risque = 'Feu de forêt') g
       USING (code_commune)""",
}


def geotraitement_vegetation(con) -> None:
    """Surface de forêt, de lande et de formation herbacée par commune (BD Forêt × ADMIN EXPRESS).

    Lit les géométries depuis les vues staging (stockées une seule fois, en raw).
    """
    import numpy as np
    import shapely

    deps = [r[0] for r in con.execute(
        "SELECT DISTINCT code_departement FROM staging.stg_bd_foret__formations ORDER BY 1").fetchall()]
    comm = con.execute("SELECT code_commune, code_departement, geometrie_wkb "
                       "FROM staging.stg_admin_express__geometries_communes").fetchall()
    code_c = np.array([r[0] for r in comm])
    garder = np.isin(np.array([r[1] for r in comm]), deps)
    # toutes les communes de métropole : un polygone peut déborder sur un département voisin
    geoms_c = shapely.from_wkb(np.array([r[2] for r in comm], dtype=object))
    arbre = shapely.STRtree(geoms_c)
    resultats, controle = [], []
    for (fichier,) in con.execute("SELECT DISTINCT _fichier_source FROM staging.stg_bd_foret__geometries ORDER BY 1").fetchall():
        rows = con.execute("SELECT id_formation, geometrie_wkb FROM staging.stg_bd_foret__geometries "
                           "WHERE _fichier_source = ?", [fichier]).fetchall()
        ids = np.array([r[0] for r in rows])
        formes = shapely.make_valid(shapely.from_wkb(np.array([r[1] for r in rows], dtype=object)))
        controle.append((Path(fichier).name, len(ids), float(shapely.area(formes).sum())))
        i_f, i_c = arbre.query(formes, predicate="intersects")
        dedans = shapely.contains_properly(geoms_c[i_c], formes[i_f])
        aires = np.where(dedans, shapely.area(formes[i_f]),
                         shapely.area(shapely.intersection(formes[i_f], geoms_c[i_c])))
        df = pd.DataFrame({"id_formation": ids[i_f], "code_commune": code_c[i_c], "surface_m2": aires,
                           "_fichier_source": fichier})
        df = df[df.surface_m2 > 0]
        resultats.append(df)
        controle[-1] += (float(df.surface_m2.sum()),)
        log(f"  géotraitement {Path(fichier).name[23:28]} : {len(ids)} polygones, {len(df)} morceaux")
    con.register("_morceaux", pd.concat(resultats, ignore_index=True))
    con.execute("CREATE OR REPLACE TABLE intermediate.int_bd_foret__formation_commune AS SELECT * FROM _morceaux")
    con.unregister("_morceaux")
    con.register("_ctrl", pd.DataFrame(controle, columns=["fichier", "nb_formations", "surface_formations_m2",
                                                          "surface_morceaux_m2"]))
    con.execute("CREATE OR REPLACE TABLE intermediate.int_bd_foret__controle_geotraitement AS SELECT * FROM _ctrl")
    con.unregister("_ctrl")
    # surface de chaque commune des départements couverts
    sel = np.where(garder)[0]
    con.register("_communes", pd.DataFrame({"code_commune": code_c[sel],
                                             "surface_commune_m2": shapely.area(geoms_c[sel])}))
    con.execute("""
        CREATE OR REPLACE TABLE intermediate.int_territoire__vegetation_commune AS
        WITH m AS (
            SELECT m.code_commune,
                   sum(m.surface_m2) FILTER (WHERE s.categorie='forêt')              AS foret,
                   sum(m.surface_m2) FILTER (WHERE s.categorie='lande')              AS lande,
                   sum(m.surface_m2) FILTER (WHERE s.categorie='formation herbacée') AS herbacee
            FROM intermediate.int_bd_foret__formation_commune m
            JOIN staging.stg_bd_foret__formations s USING (id_formation)
            GROUP BY 1)
        SELECT c.code_commune, t.code_departement, c.surface_commune_m2,
               coalesce(m.foret, 0)    AS surface_foret_m2,
               coalesce(m.lande, 0)    AS surface_lande_m2,
               coalesce(m.herbacee, 0) AS surface_formation_herbacee_m2,
               coalesce(m.foret, 0) / c.surface_commune_m2 AS taux_boisement,
               md.edition AS edition_bd_foret, md.debut_realite, md.fin_realite
        FROM _communes c
        JOIN staging.stg_cog__communes t USING (code_commune)
        LEFT JOIN m USING (code_commune)
        LEFT JOIN staging.stg_bd_foret__metadonnees md ON md.code_departement = t.code_departement""")
    con.unregister("_communes")


def construire_intermediate(con, geo: bool = True) -> None:
    table_de_passage(con)
    for nom, sql in {**INTERMEDIATE, **INTERMEDIATE_SUITE}.items():
        con.execute(f"CREATE OR REPLACE TABLE intermediate.{nom} AS {sql}")
    if geo:
        geotraitement_vegetation(con)
    log("intermédiaire : construit")


# --------------------------------------------------------------------------- qualité

# (id, couche, dimension, énoncé, décision, seuil, requête qui renvoie les lignes en faute)
REGLES = [
("Q-PIP-03", "raw", "Complétude", "lues = insérées + rejetées ; insérées = annoncées (BDIFF)", "bloquer", "0",
 """SELECT * FROM raw._journal_chargement WHERE statut='succès' AND debut >= (SELECT debut FROM qualite._execution) AND
    (lignes_lues <> lignes_inserees + lignes_rejetees OR (lignes_annoncees IS NOT NULL AND lignes_inserees <> lignes_annoncees))"""),
("Q-PIP-04", "raw", "Complétude", "succès sans aucune ligne insérée", "alerter", "0",
 "SELECT * FROM raw._journal_chargement WHERE statut='succès' AND debut >= (SELECT debut FROM qualite._execution) AND lignes_inserees=0 AND table_cible<>'raw.bdiff_notes_campagnes'"),
("Q-BDF-00", "raw", "Unicité", "(Année, Numéro) livré plusieurs fois par la source (dédoublonné en staging)", "alerter", "0",
 'SELECT "Année", "Numéro" FROM raw.bdiff_incendies GROUP BY ALL HAVING count(*) > 1'),
("Q-MDF-01", "staging", "Unicité", "(département, date d'émission) en double", "bloquer", "0",
 "SELECT code_departement, date_emission FROM staging.stg_mdf__bulletins GROUP BY ALL HAVING count(*)>1"),
("Q-MDF-02", "staging", "Validité", "niveau J+1 ou J+2 hors de 1 à 4", "bloquer", "0",
 "SELECT * FROM staging.stg_mdf__bulletins WHERE niveau_j1 NOT BETWEEN 1 AND 4 OR niveau_j2 NOT BETWEEN 1 AND 4"),
("Q-MDF-03", "staging", "Complétude des valeurs", "niveau vide", "bloquer", "0",
 "SELECT * FROM staging.stg_mdf__bulletins WHERE niveau_j1 IS NULL OR niveau_j2 IS NULL"),
("Q-MDF-04", "staging", "Complétude de la population", "bulletin × département métropolitain absent", "alerter", "0",
 """SELECT b.date_emission, d.code_departement FROM (SELECT DISTINCT date_emission FROM staging.stg_mdf__bulletins) b
    CROSS JOIN (SELECT code_departement FROM staging.stg_cog__departements WHERE length(code_departement)=2) d
    ANTI JOIN staging.stg_mdf__bulletins s USING (date_emission, code_departement)"""),
("Q-MDF-05", "staging", "Complétude de la population", "jour sans bulletin à l'intérieur d'une saison", "alerter", "0",
 """WITH s AS (SELECT millesime_fichier, min(date_emission) a, max(date_emission) b FROM staging.stg_mdf__bulletins GROUP BY 1)
    SELECT CAST(d AS DATE) jour FROM s, generate_series(CAST(a AS TIMESTAMP), CAST(b AS TIMESTAMP), INTERVAL 1 DAY) g(d)
    WHERE CAST(d AS DATE) NOT IN (SELECT date_emission FROM staging.stg_mdf__bulletins)"""),
("Q-MDF-06", "staging", "Cohérence", "code département absent du COG", "bloquer", "0",
 "SELECT * FROM staging.stg_mdf__bulletins ANTI JOIN staging.stg_cog__departements USING (code_departement)"),
("Q-BDF-01", "staging", "Unicité", "id_feu_bdiff en double", "bloquer", "0",
 "SELECT id_feu_bdiff FROM staging.stg_bdiff__feux GROUP BY 1 HAVING count(*)>1"),
("Q-BDF-02", "staging", "Validité", "date d'alerte hors de l'année ou future", "bloquer", "0",
 "SELECT * FROM staging.stg_bdiff__feux WHERE year(date_alerte)<>annee OR date_alerte > current_date"),
("Q-BDF-03", "staging", "Validité", "surface parcourue vide ou ≤ 0", "alerter", "0",
 "SELECT * FROM staging.stg_bdiff__feux WHERE coalesce(surface_parcourue_m2,0) <= 0"),
("Q-BDF-04", "staging", "Cohérence", "surface forêt > surface parcourue", "alerter", "0",
 "SELECT * FROM staging.stg_bdiff__feux WHERE surface_foret_m2 > surface_parcourue_m2"),
("Q-BDF-05", "staging", "Cohérence", "département ≠ début du code commune", "alerter", "0",
 "SELECT * FROM staging.stg_bdiff__feux WHERE NOT starts_with(code_commune_origine, code_departement)"),
("Q-BDF-06", "staging", "Validité", "valeur hors liste (précision, cause, peuplement)", "alerter", "0",
 """SELECT * FROM staging.stg_bdiff__feux WHERE precision_surfaces NOT IN ('Estimées','Mesurées')
    OR cause_nature NOT IN ('Naturelle','Accidentelle','Malveillance','Involontaire (travaux)','Involontaire (particulier)')
    OR type_peuplement_code NOT IN ('1','2','3','4','5','6')"""),
("Q-BDF-07", "staging", "Validité", "heure d'alerte à 00:00 (probablement non saisie)", "tolérer", "< 1 %",
 "SELECT * FROM staging.stg_bdiff__feux WHERE strftime(horodatage_alerte,'%H:%M')='00:00'"),
("Q-BDF-08", "staging", "Complétude des valeurs", "cause non renseignée", "tolérer", "suivi",
 "SELECT * FROM staging.stg_bdiff__feux WHERE cause_nature IS NULL"),
("Q-BDF-09", "staging", "Complétude des valeurs", "surface forêt vide", "tolérer", "suivi",
 "SELECT * FROM staging.stg_bdiff__feux WHERE surface_foret_m2 IS NULL"),
("Q-BDF-10", "staging", "Complétude de la population", "département × année sans aucun feu (départements présents)", "alerter", "suivi",
 """SELECT d.code_departement, y.annee FROM (SELECT DISTINCT code_departement FROM staging.stg_bdiff__feux) d
    CROSS JOIN (SELECT range AS annee FROM range(2006, 2026)) y
    ANTI JOIN staging.stg_bdiff__feux f ON f.code_departement=d.code_departement AND f.annee=y.annee"""),
("Q-BDF-11", "staging", "Actualité", "dernière année présente antérieure à N-1", "alerter", "1 an",
 "SELECT max(annee) FROM staging.stg_bdiff__feux HAVING max(annee) < year(current_date)-1"),
("Q-BDF-12", "staging", "Exactitude (source)", "fiches signalées partielles ou non valides", "tolérer", "suivi",
 "SELECT * FROM staging.stg_bdiff__feux WHERE precision_donnee IS NOT NULL"),
("Q-COG-01", "staging", "Unicité", "code commune en double", "bloquer", "0",
 "SELECT code_commune FROM staging.stg_cog__communes GROUP BY 1 HAVING count(*)>1"),
("Q-COG-02", "staging", "Complétude de la population", "le 69 ≠ 208 communes 69D + 58 communes 69M", "bloquer", "0",
 """SELECT code_ctcd, count(*) n FROM staging.stg_cog__communes WHERE code_departement='69' GROUP BY 1
    HAVING NOT ((code_ctcd='69D' AND n=208) OR (code_ctcd='69M' AND n=58))"""),
("Q-COG-03", "staging", "Cohérence", "plus d'un millésime COG", "bloquer", "0",
 "SELECT DISTINCT millesime_cog FROM staging.stg_cog__communes OFFSET 1"),
("Q-BDF-13", "staging", "Cohérence", "métadonnées BD Forêt : fin de la réalité décrite avant son début", "tolérer", "suivi",
 "SELECT * FROM staging.stg_bd_foret__metadonnees WHERE fin_realite < debut_realite"),
("Q-BDF-14", "staging", "Validité", "formation BD Forêt sans catégorie (forêt, lande, herbacée)", "alerter", "0",
 "SELECT * FROM staging.stg_bd_foret__formations WHERE categorie IS NULL"),
("Q-CONS-01", "intermediate", "Unicité", "code d'origine menant à plusieurs communes 2026", "bloquer", "0",
 "SELECT code_commune_origine FROM intermediate.int_territoire__passage_communes GROUP BY 1 HAVING count(*)>1"),
("Q-CONS-02", "intermediate", "Complétude (non-perte)", "feu ni rattaché ni rejeté", "bloquer", "0",
 """SELECT id_feu_bdiff FROM staging.stg_bdiff__feux
    ANTI JOIN (SELECT id_feu_bdiff FROM intermediate.int_bdiff__feux_rattaches
               UNION ALL SELECT id_feu_bdiff FROM intermediate.int_bdiff__feux_rejets) USING (id_feu_bdiff)"""),
("Q-CONS-03", "intermediate", "Cohérence", "feux en table de rejet", "alerter", "0",
 "SELECT * FROM intermediate.int_bdiff__feux_rejets"),
("Q-CONS-04", "intermediate", "Complétude (non-perte)", "écart de surface staging ≠ rattachés + rejets", "bloquer", "0 m²",
 """SELECT 1 WHERE (SELECT sum(surface_parcourue_m2) FROM staging.stg_bdiff__feux) <>
    (SELECT coalesce(sum(surface_parcourue_m2),0) FROM intermediate.int_bdiff__feux_rattaches)
  + (SELECT coalesce(sum(surface_parcourue_m2),0) FROM intermediate.int_bdiff__feux_rejets)"""),
("Q-CONS-05", "intermediate", "Unicité (non-multiplication)", "feu dupliqué dans int_feux__danger", "bloquer", "0",
 """SELECT feu_sk FROM intermediate.int_feux__danger GROUP BY 1 HAVING count(*)>1
    UNION ALL SELECT NULL WHERE (SELECT count(*) FROM intermediate.int_feux__danger)
                         <> (SELECT count(*) FROM staging.stg_bdiff__feux)"""),
("Q-CONS-06", "intermediate", "Unicité", "(département, jour cible) en double", "bloquer", "0",
 "SELECT code_departement, jour_cible FROM intermediate.int_mdf__danger_jour GROUP BY ALL HAVING count(*)>1"),
("Q-CONS-07", "intermediate", "Complétude (non-perte)", "niveaux J+1/J+2 perdus entre staging et danger_jour", "bloquer", "0",
 """SELECT 1 WHERE (SELECT count(niveau_j1) FROM intermediate.int_mdf__danger_jour) <> (SELECT count(*) FROM staging.stg_mdf__bulletins)
    OR (SELECT count(niveau_j2) FROM intermediate.int_mdf__danger_jour) <> (SELECT count(*) FROM staging.stg_mdf__bulletins)"""),
("Q-CONS-08", "intermediate", "Cohérence (jointure)", "feu dans la fenêtre J+1 sans niveau", "bloquer", "0",
 """SELECT f.* FROM intermediate.int_feux__danger f
    JOIN (SELECT code_departement, year(jour_cible) y, min(jour_cible) a, max(jour_cible) b
          FROM intermediate.int_mdf__danger_jour WHERE niveau_j1 IS NOT NULL GROUP BY ALL) w
      ON w.code_departement=f.code_departement AND f.date_alerte BETWEEN w.a AND w.b
    WHERE f.niveau_reference IS NULL"""),
("Q-CONS-09", "intermediate", "Complétude de la population", "feux 2024-2025 sans bulletin (indicateur)", "tolérer", "suivi",
 "SELECT * FROM intermediate.int_feux__danger WHERE year(date_alerte) IN (2024,2025) AND niveau_reference IS NULL"),
("Q-CONS-10", "intermediate", "Complétude (non-perte)", "surface des formations ≠ somme des morceaux par commune (écart > 0,1 %)", "alerter", "0,1 %",
 "SELECT * FROM intermediate.int_bd_foret__controle_geotraitement WHERE abs(surface_morceaux_m2 / surface_formations_m2 - 1) > 0.001"),
("Q-SIS-01", "staging", "Unicité", "(année, SIS) en double", "bloquer", "0",
 "SELECT annee, code_sis FROM staging.stg_dgscgc__interventions_sis GROUP BY ALL HAVING count(*) > 1"),
("Q-SIS-02", "staging", "Complétude de la population", "année 2008-2024 sans ligne pour le SDMIS (69)", "alerter", "0",
 "SELECT range AS annee FROM range(2008, 2025) ANTI JOIN (SELECT annee FROM staging.stg_dgscgc__interventions_sis WHERE code_sis = '69') s ON s.annee = range"),
("Q-SIS-03", "staging", "Complétude des valeurs", "SIS × année sans détail « feux de végétations » (schéma 2010-2013)", "tolérer", "suivi",
 "SELECT * FROM staging.stg_dgscgc__interventions_sis WHERE feux_vegetation IS NULL"),
("Q-MET-01", "staging", "Unicité", "(station, date) en double", "bloquer", "0",
 "SELECT code_station, date FROM staging.stg_meteo__quotidien GROUP BY ALL HAVING count(*) > 1"),
("Q-MET-02", "staging", "Complétude des valeurs", "année 1991-2025 où Lyon-Bron a moins de 98 % de TX renseignées", "alerter", "0",
 """SELECT year(date) a, count(tmax_c) / count(*) t FROM staging.stg_meteo__quotidien
    WHERE code_station = '69029001' AND year(date) BETWEEN 1991 AND 2025 GROUP BY 1 HAVING count(tmax_c) < 0.98 * count(*)"""),
("Q-MET-03", "staging", "Validité", "TX hors de -30 à 50 °C ou pluie négative", "alerter", "0",
 "SELECT * FROM staging.stg_meteo__quotidien WHERE tmax_c NOT BETWEEN -30 AND 50 OR pluie_mm < 0"),
("Q-GAS-01", "staging", "Conformité au référentiel", "commune GASPAR « feu de forêt » absente du COG 2026", "alerter", "0",
 """SELECT DISTINCT g.code_commune FROM staging.stg_gaspar__risques_communes g
    ANTI JOIN staging.stg_cog__codes_commune c ON c.code = g.code_commune WHERE g.risque = 'Feu de forêt'"""),
("Q-CAS-01", "staging", "Validité", "site SDMIS hors de l'emprise du Rhône", "alerter", "0",
 "SELECT * FROM staging.stg_sdmis__casernes WHERE NOT (lon BETWEEN 4.2 AND 5.2 AND lat BETWEEN 45.4 AND 46.35)"),
("Q-RGPD-01", "intermediate", "Conformité", "colonne interdite après raw (décès, bâtiments, adresse, victimes…)", "bloquer", "0",
 """SELECT table_schema, table_name, column_name FROM information_schema.columns
    WHERE table_schema IN ('staging','intermediate','marts')
      AND regexp_matches(lower(column_name), 'd[ée]c[eè]s|b[âa]timent|adresse|requ[ée]rant|victime|agent|gps|coordonn')"""),
]


# --------------------------------------------------------------------------- marts (restitution)

MARTS = {
"fct_feux": r"""
SELECT f.feu_sk, f.id_feu_bdiff, year(f.date_alerte) AS annee, month(f.date_alerte) AS mois, f.date_alerte,
       f.code_departement, d.code_region, f.code_commune_cog2026 AS code_commune, c.code_ctcd,
       f.surface_parcourue_m2 / 1e4 AS surface_ha, f.niveau_j1, f.niveau_j2, f.statut_bulletin
FROM intermediate.int_feux__danger f
LEFT JOIN staging.stg_cog__departements d USING (code_departement)
LEFT JOIN staging.stg_cog__communes c ON c.code_commune = f.code_commune_cog2026""",

"fct_danger_jour": r"""
SELECT j.code_departement, d.code_region, j.jour_cible AS jour, year(j.jour_cible) AS annee, j.niveau_j1, j.niveau_j2
FROM intermediate.int_mdf__danger_jour j LEFT JOIN staging.stg_cog__departements d USING (code_departement)""",

"dim_departements": r"""
SELECT d.code_departement, d.libelle_departement, d.code_region, r.libelle_region,
       sum(v.surface_foret_m2) / 1e4 AS surface_boisee_ha, sum(v.surface_commune_m2) / 1e4 AS surface_ha,
       (SELECT sum(population) FROM staging.stg_admin_express__communes a WHERE a.code_departement = d.code_departement) AS population
FROM staging.stg_cog__departements d
LEFT JOIN staging.stg_cog__regions r USING (code_region)
LEFT JOIN intermediate.int_territoire__vegetation_commune v USING (code_departement)
GROUP BY ALL""",

"fct_sdis_feux_vegetation": r"""
SELECT s.annee, s.code_departement, d.libelle_departement, d.code_region, s.feux_vegetation, s.incendies,
       s.feux_bdiff, s.feux_bdiff_1ha
FROM intermediate.int_sdis__feux_vegetation s
JOIN staging.stg_cog__departements d USING (code_departement)
WHERE NOT s.sis_hors_sdis""",

"fct_meteo_lyon_bron": r"""
SELECT date, year(date) AS annee, month(date) AS mois, tmax_c, pluie_mm, pluie_10j_mm, chaleur_seche, jour_tx30,
       niveau_mdf_69
FROM intermediate.int_meteo__jours_lyon_bron WHERE year(date) >= 1991""",

"dim_casernes": "SELECT * FROM staging.stg_sdmis__casernes",
"ref_presse_2026": "SELECT * FROM staging.stg_presse__chiffres_2026",
}


def construire_marts(con) -> None:
    """Couche gold de restitution du tableau de bord, exportée aussi en Parquet (data/marts)."""
    import numpy as np
    import shapely
    from pyproj import Transformer

    for nom, sql in MARTS.items():
        con.execute(f"CREATE OR REPLACE TABLE marts.{nom} AS {sql}")
    # communes du Rhône avec un contour simplifié (50 m) en WGS84 pour la carte
    rows = con.execute("""
        SELECT t.code_commune, t.libelle_commune, t.code_ctcd, t.population,
               v.surface_commune_m2 / 1e4, v.surface_foret_m2 / 1e4, v.surface_lande_m2 / 1e4, v.taux_boisement,
               r.risque_feu_ddrm, g.geometrie_wkb
        FROM intermediate.int_territoire__communes t
        JOIN intermediate.int_territoire__vegetation_commune v USING (code_commune)
        JOIN intermediate.int_territoire__risque_feu_communes r USING (code_commune)
        JOIN staging.stg_admin_express__geometries_communes g USING (code_commune)
        WHERE t.code_departement = '69'""").fetchall()
    vers_wgs84 = Transformer.from_crs(2154, 4326, always_xy=True)
    geoms = shapely.simplify(shapely.from_wkb(np.array([r[-1] for r in rows], dtype=object)), 50)
    geoms = shapely.transform(geoms, lambda xy: np.column_stack(vers_wgs84.transform(xy[:, 0], xy[:, 1])))
    df = pd.DataFrame([r[:-1] for r in rows], columns=[
        "code_commune", "libelle_commune", "code_ctcd", "population", "surface_ha", "surface_foret_ha",
        "surface_lande_ha", "taux_boisement", "risque_feu_ddrm"])
    df["geojson"] = shapely.to_geojson(shapely.set_precision(geoms, 1e-5))
    con.register("_communes69", df)
    con.execute("""CREATE OR REPLACE TABLE marts.dim_communes_rhone AS
        SELECT c.*, coalesce(f.feux, 0) AS feux_bdiff_2006_2025, coalesce(f.ha, 0) AS surface_brulee_ha_2006_2025
        FROM _communes69 c LEFT JOIN (SELECT code_commune, count(*) AS feux, sum(surface_ha) AS ha
                                      FROM marts.fct_feux GROUP BY 1) f USING (code_commune)""")
    con.unregister("_communes69")
    sortie = RACINE / "data" / "marts"
    sortie.mkdir(parents=True, exist_ok=True)
    for (nom,) in con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='marts'").fetchall():
        con.execute(f"COPY marts.{nom} TO '{(sortie / (nom + '.parquet')).as_posix()}' (FORMAT parquet)")
    log(f"marts : {len(MARTS) + 1} tables, exportées dans {sortie}")


def exporter_qualite(con, id_exec: str) -> None:
    """Copie pour le tableau de bord : résultats des règles de l'exécution et bilan des chargements par source."""
    sortie = RACINE / "data" / "marts"
    con.execute(f"""COPY (SELECT couche, id_regle, dimension, enonce, decision, nb_en_faute, statut
                          FROM qualite.resultats_tests WHERE id_execution = '{id_exec}' ORDER BY couche, id_regle)
                    TO '{(sortie / "_qualite_tests.parquet").as_posix()}' (FORMAT parquet)""")
    # dernier chargement réussi de chaque fichier : un fichier rechargé (remplacement idempotent) ne compte qu'une fois
    con.execute(f"""COPY (WITH dernier AS (
                              SELECT * FROM raw._journal_chargement WHERE statut = 'succès'
                              QUALIFY row_number() OVER (PARTITION BY fichier, table_cible ORDER BY fin DESC) = 1)
                          SELECT source, count(DISTINCT fichier) AS fichiers, sum(taille_octets) AS octets,
                                 sum(lignes_inserees) AS lignes, sum(lignes_rejetees) AS rejets, max(fin) AS charge_le
                          FROM dernier GROUP BY source ORDER BY source)
                    TO '{(sortie / "_journal_sources.parquet").as_posix()}' (FORMAT parquet)""")


def tester(con, couche: str, id_exec: str, ignorer: set[str] = frozenset()) -> None:
    bloquants = []
    for rid, c, dim, enonce, decision, seuil, sql in REGLES:
        if c != couche:
            continue
        if rid in ignorer:
            con.execute("INSERT INTO qualite.resultats_tests VALUES (?,?,?,?,?,?,?,?,?,?)",
                        [id_exec, datetime.now(), couche, rid, dim, enonce, decision, None, seuil, "non exécuté"])
            continue
        try:
            n = con.execute(f"SELECT count(*) FROM ({sql})").fetchone()[0]
            statut = "réussi" if n == 0 else ("échec" if decision == "bloquer" else decision)
        except duckdb.Error as e:
            n, statut = None, f"erreur : {e}"[:200]
        con.execute("INSERT INTO qualite.resultats_tests VALUES (?,?,?,?,?,?,?,?,?,?)",
                    [id_exec, datetime.now(), couche, rid, dim, enonce, decision, n, seuil, statut])
        if statut == "échec" or statut.startswith("erreur"):
            bloquants.append(f"{rid} ({n} en faute)" if n is not None else f"{rid} {statut}")
    if bloquants:
        raise Bloquant(f"couche {couche} : " + ", ".join(bloquants))


def verifier_idempotence(con, id_exec: str) -> None:
    """Q-PIP-01 : recharger les mêmes fichiers ne change aucun compte."""
    tables = [r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='raw' AND NOT starts_with(table_name,'_')").fetchall()]
    avant = {t: con.execute(f"SELECT count(*) FROM raw.{t}").fetchone()[0] for t in tables}
    charger_raw(con, forcer=True)
    apres = {t: con.execute(f"SELECT count(*) FROM raw.{t}").fetchone()[0] for t in tables}
    ecarts = {t: (avant[t], apres[t]) for t in tables if avant[t] != apres[t]}
    con.execute("INSERT INTO qualite.resultats_tests VALUES (?,?,?,?,?,?,?,?,?,?)",
                [id_exec, datetime.now(), "raw", "Q-PIP-01", "Unicité",
                 f"compte des {len(tables)} tables raw identique après rechargement forcé",
                 "bloquer", len(ecarts), "0", "réussi" if not ecarts else "échec"])
    log(f"Q-PIP-01 idempotence : {'réussi' if not ecarts else ecarts}")
    if ecarts:
        raise Bloquant(f"Q-PIP-01 : {ecarts}")


# --------------------------------------------------------------------------- principal

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--idempotence", action="store_true", help="recharger une 2e fois et comparer (Q-PIP-01)")
    p.add_argument("--sans-geo", action="store_true", help="ne pas refaire le géotraitement BD Forêt")
    a = p.parse_args()

    BASE.parent.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(BASE))
    initialiser(con)
    id_exec = uuid.uuid4().hex[:12]
    t0 = time.time()
    con.execute("CREATE OR REPLACE TABLE qualite._execution AS SELECT ? AS id_execution, now()::TIMESTAMP AS debut", [id_exec])
    try:
        charger_raw(con)
        if a.idempotence:
            verifier_idempotence(con, id_exec)
        tester(con, "raw", id_exec)
        construire_staging(con)
        tester(con, "staging", id_exec)
        construire_intermediate(con, geo=not a.sans_geo)
        tester(con, "intermediate", id_exec, ignorer={"Q-CONS-10"} if a.sans_geo else set())
        construire_marts(con)
        tester(con, "marts", id_exec)
        exporter_qualite(con, id_exec)
    except Bloquant as e:
        log(f"ARRÊT (règle bloquante) : {e}")
        return 2
    finally:
        res = con.execute("""SELECT id_regle, statut, nb_en_faute FROM qualite.resultats_tests
                             WHERE id_execution=? ORDER BY id_regle""", [id_exec]).fetchall()
        for r in res:
            log(f"  {r[0]:<10} {r[1]:<10} {r[2]}")
        con.close()
        shutil.rmtree(TMP, ignore_errors=True)
    compacter()
    log(f"Entrepôt construit en {time.time() - t0:.0f} s : {BASE} ({BASE.stat().st_size / 1e6:.0f} Mo)")
    return 0


def compacter() -> None:
    """Réécrit la base sans l'espace libéré par les rechargements, au format DuckDB 1.2
    (lisible par toutes les versions récentes : Python, DBeaver, ODBC)."""
    tmp = BASE.with_suffix(".compact.duckdb")
    tmp.unlink(missing_ok=True)
    c = duckdb.connect()
    c.execute(f"ATTACH '{BASE.as_posix()}' AS src (READ_ONLY)")
    c.execute(f"ATTACH '{tmp.as_posix()}' AS dst (STORAGE_VERSION 'v1.2.0')")
    c.execute("COPY FROM DATABASE src TO dst")
    c.close()
    tmp.replace(BASE)


if __name__ == "__main__":
    sys.exit(main())
