"""Profil de qualité v1 des sources extraites (dossier de sources, FOAD 1 du 17/11).

Pour chaque source : un profil par colonne (type, complétude, distincts, min, max),
puis des contrôles de validité et de cohérence.
Entrées (data/raw/, non versionné) : mdf_france_2024_2026.csv, bdiff_ara_2006_2025.csv,
v_commune_2026.csv, v_mvt_commune_2026.csv.
Sortie : docs/sources/profils-qualite-generes.md (ne pas modifier à la main).
"""
import io
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"


def lire_bdiff():
    lines = (RAW / "bdiff_ara_2006_2025.csv").read_text(encoding="utf-8").splitlines()
    hi = next(i for i, l in enumerate(lines) if l.startswith("Année;"))
    return pd.read_csv(io.StringIO("\n".join(lines[hi:])), sep=";", dtype=str)


def profil(df):
    rows = []
    for c in df.columns:
        nn = df[c].dropna()
        num = pd.to_numeric(nn, errors="coerce")
        est_num = len(nn) > 0 and num.notna().all()
        rows.append({"colonne": c,
                     "type observé": "numérique" if est_num else "texte",
                     "complétude": f"{df[c].notna().mean():.1%}",
                     "distincts": nn.nunique(),
                     "min": nn.min() if len(nn) else "",
                     "max": nn.max() if len(nn) else ""})
    return pd.DataFrame(rows).to_markdown(index=False)


def controles(liste):
    return pd.DataFrame(liste, columns=["contrôle", "dimension", "résultat"]).to_markdown(index=False)


# --- Météo des forêts
mdf = pd.read_csv(RAW / "mdf_france_2024_2026.csv", dtype=str)
mdf["dep"] = mdf["num_dep"].str.zfill(2)
ts = pd.to_datetime(mdf["date"], utc=True)
mdf["emission"] = ts.dt.tz_convert("Europe/Paris").dt.normalize().dt.tz_localize(None)
j1 = mdf[["dep", "emission", "niveau_j1"]].assign(cible=mdf["emission"] + pd.Timedelta(days=1))
j2 = mdf[["dep", "emission", "niveau_j2"]].assign(cible=mdf["emission"] + pd.Timedelta(days=2))
acc = j1.merge(j2, on=["dep", "cible"])
c_mdf = [
    ("Niveaux dans {1,2,3,4}", "validité",
     f"{mdf[['niveau_j1','niveau_j2']].isin(list('1234')).all(axis=1).mean():.1%} des lignes"),
    ("Unicité (département, date d'émission)", "unicité",
     f"{mdf.duplicated(['dep','date']).sum()} doublon"),
    ("Départements par bulletin", "complétude de la population",
     ", ".join(f"{k} départements dans {v} bulletins" for k, v in mdf.groupby('date').size().value_counts().items())),
    ("Code département sur 1 caractère (`1` au lieu de `01`)", "cohérence",
     f"{(mdf['num_dep'].str.len()==1).sum()} lignes (fichiers 2024 et 2025)"),
    ("Heures d'émission (UTC)", "cohérence",
     ", ".join(f"{k} : {v}" for k, v in ts.dt.strftime('%H:%M').value_counts().items())),
    ("Période d'émission par année", "actualité / couverture",
     "; ".join(f"{y} : {g.min():%d/%m} → {g.max():%d/%m}" for y, g in mdf.groupby('annee_fichier')['emission'])),
    ("Même niveau J+1 et J+2 pour un même jour cible", "cohérence", f"{(acc.niveau_j1==acc.niveau_j2).mean():.1%} ({len(acc)} paires)"),
]

# --- BDIFF
b = lire_bdiff()
n = lambda c: pd.to_numeric(b[c], errors="coerce")
tot = n("Surface parcourue (m2)")
v_new = n("Surface forêt (m2)").fillna(0) + n("Surface autres terres boisées (m2)").fillna(0) + n("Surfaces non boisées (m2)").fillna(0)
v_old = (n("Surface forêt (m2)").fillna(0) + n("Surface maquis garrigues (m2)").fillna(0)
         + n("Autres surfaces naturelles hors forêt (m2)").fillna(0) + n("Surfaces agricoles (m2)").fillna(0)
         + n("Autres surfaces (m2)").fillna(0))
ventil = ((v_new - tot).abs() <= 1) | ((v_old - tot).abs() <= 1)
mois = pd.to_datetime(b["Date de première alerte"]).dt.month
hors = ~mois.between(6, 9)
com = pd.read_csv(RAW / "v_commune_2026.csv", dtype=str)
com = com[com["TYPECOM"] == "COM"]
mvt = pd.read_csv(RAW / "v_mvt_commune_2026.csv", dtype=str)
absent = ~b["Code INSEE"].isin(set(com["COM"]))
codes_abs = b.loc[absent, "Code INSEE"].unique()
retrouves = mvt.loc[mvt["COM_AV"].isin(codes_abs) & (mvt["TYPECOM_AP"] == "COM"), "COM_AV"].nunique()
lib = com.set_index("COM")["LIBELLE"]
ok = b.loc[~absent]
par_an_69 = b[b["Département"] == "69"].groupby("Année").size().reindex([str(y) for y in range(2006, 2026)], fill_value=0)
c_bdiff = [
    ("Unicité (Année, Numéro)", "unicité", f"{b.duplicated(['Année','Numéro']).sum()} doublon"),
    ("Année = année de la date d'alerte", "cohérence", f"{(b['Année']==b['Date de première alerte'].str[:4]).mean():.1%}"),
    ("Département = 2 premiers caractères du code INSEE", "cohérence",
     f"{(b['Département'].str.zfill(2)==b['Code INSEE'].str[:2]).mean():.1%}"),
    ("Surface parcourue > 0", "validité", f"{(tot>0).mean():.1%}"),
    ("Somme des surfaces ventilées = surface parcourue (±1 m²)", "cohérence", f"{ventil.mean():.1%} ({(~ventil).sum()} feux en écart)"),
    ("Code INSEE présent dans le COG 2026", "conformité au référentiel",
     f"{(~absent).mean():.1%} ; {absent.sum()} feux / {len(codes_abs)} codes absents, dont {retrouves} retrouvés par les mouvements"),
    ("Libellé BDIFF = libellé COG 2026 (codes valides)", "cohérence",
     f"{(ok['Nom de la commune']==ok['Code INSEE'].map(lib)).mean():.1%}"),
    ("Cause (`Nature`) renseignée", "complétude", f"{b['Nature'].notna().mean():.1%} (69 : {b.loc[b['Département']=='69','Nature'].notna().mean():.1%})"),
    ("Feux par an dans le 69 (2006 → 2025)", "complétude de la population",
     " ".join(par_an_69.astype(str)) + f" ; {(par_an_69==0).sum()} années à 0"),
    ("Feux hors juin-septembre (hors saison du bulletin MdF)", "couverture",
     f"{hors.mean():.1%} des feux, {tot[hors].sum()/tot.sum():.1%} de la surface"),
]

# --- COG
c_cog = [
    ("Unicité du code commune (TYPECOM = COM)", "unicité", "oui" if com["COM"].is_unique else "NON"),
    ("Communes du 69 par collectivité (CTCD)", "couverture",
     ", ".join(f"{k} : {v}" for k, v in com[com['DEP']=='69']['CTCD'].value_counts().items())),
]

txt = ["# Profils de qualité générés (annexe)\n",
       "Généré par `src/profil_qualite.py` à partir des extractions du 17/11/2026. Ne pas modifier à la main.\n",
       f"## Météo des forêts 2024-2026 (France)\n\n{len(mdf)} lignes.\n\n" + profil(mdf.drop(columns=['dep','emission'])) + "\n\n" + controles(c_mdf) + "\n",
       f"## BDIFF Auvergne-Rhône-Alpes 2006-2025\n\n{len(b)} lignes.\n\n" + profil(b) + "\n\n" + controles(c_bdiff) + "\n",
       f"## COG 2026, communes de la région 84\n\n{len(com)} communes.\n\n" + profil(com) + "\n\n" + controles(c_cog) + "\n"]
(ROOT / "docs/sources/profils-qualite-generes.md").write_text("\n".join(txt), encoding="utf-8")
print("profils écrits")
