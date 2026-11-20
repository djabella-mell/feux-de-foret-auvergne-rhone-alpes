"""Sources longues ajoutées le 20/11/2026 : danger météo reconstitué depuis 1958 et détections satellitaires.

Lit les silos de data/bronze/ et écrit des tables Parquet dans data/marts/ :
  - fct_ifm_jour.parquet          : IFM quotidien reconstitué (SAFRAN) pour 15 points, 1958-2026
  - ref_ifm_seuils.parquet        : seuils d'IFM équivalents aux niveaux 2 et 3 de la Météo des forêts, par département
  - fct_ifm_validation.parquet    : comparaison jour par jour avec la Météo des forêts (2024-2026)
  - fct_ifm_ete.parquet           : jours équivalents « niveau 2 » et « niveau 3 » par été et par point
  - fct_feux_ifm.parquet          : feux BDIFF de la région (≥ 1 ha) avec l'IFM et le niveau équivalent du jour
  - fct_firms_detections.parquet  : détections satellitaires (feux de végétation présumés) en Auvergne-Rhône-Alpes
  - ifm_station_lyon_bron.parquet : IFM calculé à la station de Lyon-Bron (humidité minimale observée), contrôle

Lancement : python pipeline/sources_longues.py   (après construire_entrepot.py, qui produit les marts utilisés)
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

import ifm

RACINE = Path(__file__).resolve().parents[1]
BRONZE = RACINE / "data" / "bronze"
MARTS = RACINE / "data" / "marts"
BASE = RACINE / "data" / "entrepot" / "feux_de_foret.duckdb"
DEPS_ARA = ["01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"]
POINTS_RHONE = ["dep_69", "69_claveisolles", "69_saint_martin_en_haut"]


def lire_safran() -> pd.DataFrame:
    """CoverageJSON de l'API EDR SAFRAN (GéoSAS) → une ligne par point et par jour, avec l'IFM calculé."""
    points = {p["cle"]: p for p in json.loads((Path(__file__).with_name("points_safran.json")).read_text("utf-8"))}
    morceaux = []
    for f in sorted(glob.glob(str(BRONZE / "safran_sim2" / "*" / "*.covjson"))):
        j = json.loads(Path(f).read_text())
        cle = Path(f).stem[len("safran_"):].rsplit("_", 2)[0]
        d = pd.DataFrame({k: v["values"] for k, v in j["ranges"].items()})
        d["date"] = pd.to_datetime([s[:10] for s in j["domain"]["axes"]["t"]["values"]])
        d = d.sort_values("date").reset_index(drop=True)
        hu = ifm.humidite_midi(d.HU_Q.values, d.T_Q.values, d.TSUP_H_Q.values)
        codes = ifm.serie_ifm(d.TSUP_H_Q.values, hu, d.FF_Q.values * 3.6, (d.PRELIQ_Q + d.PRENEI_Q).values,
                              d.date.dt.month.values)
        d = d.rename(columns={"T_Q": "t_moy_c", "TSUP_H_Q": "t_max_c", "TINF_H_Q": "t_min_c", "HU_Q": "hu_moy_pct",
                              "FF_Q": "vent_ms", "PRELIQ_Q": "pluie_mm", "PRENEI_Q": "neige_mm", "SWI_Q": "swi_pct"})
        d["hu_midi_pct"] = hu
        for k, c in enumerate(["ffmc", "dmc", "dc", "isi", "bui", "ifm"]):
            d[c] = codes[:, k]
        p = points[cle]
        d.insert(0, "point", cle)
        d.insert(1, "code_departement", p["dep"])
        d.insert(2, "commune_point", p["nom"])
        d["_fichier_source"] = str(Path(f).relative_to(BRONZE))
        morceaux.append(d)
    return pd.concat(morceaux, ignore_index=True)


def seuils_equivalents(ifm_pts: pd.DataFrame, danger: pd.DataFrame) -> pd.DataFrame:
    """Seuil d'IFM qui reproduit, sur 2024-2026, le nombre de jours où le bulletin annonçait le niveau 2 (et 3)."""
    lignes = []
    for d in DEPS_ARA:
        cle = "dep_" + d
        m = danger[danger.code_departement == d].dropna(subset=["niveau_j1"]).merge(
            ifm_pts[ifm_pts.point == cle][["date", "ifm"]], left_on="jour", right_on="date")
        v = np.sort(m.ifm.values)[::-1]
        n2, n3 = int((m.niveau_j1 >= 2).sum()), int((m.niveau_j1 >= 3).sum())
        from sklearn.metrics import roc_auc_score
        lignes.append({"code_departement": d, "point": cle, "jours_bulletin": len(m), "jours_niveau2": n2,
                       "jours_niveau3": n3, "seuil_ifm_niveau2": v[n2 - 1] if n2 else np.nan,
                       "seuil_ifm_niveau3": v[n3 - 1] if n3 else np.nan,
                       "auc_niveau2": roc_auc_score(m.niveau_j1 >= 2, m.ifm) if 0 < n2 < len(m) else np.nan,
                       "correlation_rang": m[["ifm", "niveau_j1"]].corr("spearman").iloc[0, 1]})
    return pd.DataFrame(lignes)


def main() -> None:
    con = duckdb.connect(str(BASE), read_only=True)
    danger = pd.read_parquet(MARTS / "fct_danger_jour.parquet")
    danger["jour"] = pd.to_datetime(danger.jour)

    jour = lire_safran()
    jour.to_parquet(MARTS / "fct_ifm_jour.parquet", index=False)

    seuils = seuils_equivalents(jour, danger)
    seuils.to_parquet(MARTS / "ref_ifm_seuils.parquet", index=False)
    s2 = dict(zip(seuils.code_departement, seuils.seuil_ifm_niveau2))
    s3 = dict(zip(seuils.code_departement, seuils.seuil_ifm_niveau3))

    # validation jour par jour, Rhône : moyenne des trois points boisés
    rh = jour[jour.point.isin(POINTS_RHONE)].groupby("date", as_index=False).ifm.mean()
    val = danger[danger.code_departement == "69"].dropna(subset=["niveau_j1"]).merge(rh, left_on="jour", right_on="date")
    val[["jour", "niveau_j1", "niveau_j2", "ifm"]].to_parquet(MARTS / "fct_ifm_validation.parquet", index=False)

    # jours équivalents par été (1er juin - 30 septembre)
    ete = jour[jour.date.dt.month.between(6, 9) & jour.point.str.startswith("dep_")].copy()
    ete["annee"] = ete.date.dt.year
    ete["eq_niveau2"] = ete.ifm >= ete.code_departement.map(s2)
    ete["eq_niveau3"] = ete.ifm >= ete.code_departement.map(s3)
    (ete.groupby(["annee", "code_departement"], as_index=False)
        .agg(jours=("ifm", "size"), jours_eq_niveau2=("eq_niveau2", "sum"), jours_eq_niveau3=("eq_niveau3", "sum"),
             ifm_moyen=("ifm", "mean"))
        .to_parquet(MARTS / "fct_ifm_ete.parquet", index=False))

    # feux de la région ≥ 1 ha avec l'IFM du jour
    feux = pd.read_parquet(MARTS / "fct_feux.parquet")
    feux = feux[(feux.code_region == "84") & (feux.surface_ha >= 1)].copy()
    feux["date"] = pd.to_datetime(feux.date_alerte)
    feux = feux.merge(jour[jour.point.str.startswith("dep_")][["code_departement", "date", "ifm"]],
                      on=["code_departement", "date"], how="left")
    feux["eq_niveau2"] = feux.ifm >= feux.code_departement.map(s2)
    feux["eq_niveau3"] = feux.ifm >= feux.code_departement.map(s3)
    feux.drop(columns="date").to_parquet(MARTS / "fct_feux_ifm.parquet", index=False)

    # détections satellitaires FIRMS dans la région (type 0 : feu de végétation présumé)
    import shapely
    from pyproj import Transformer
    g = con.execute("SELECT code_departement, geometrie_wkb FROM staging.stg_admin_express__geometries_communes "
                    f"WHERE code_departement IN ({','.join(repr(d) for d in DEPS_ARA)})").df()
    geo = shapely.from_wkb(g.geometrie_wkb.apply(bytes).values)
    polys = {d: shapely.union_all(geo[(g.code_departement == d).values]) for d in DEPS_ARA}
    t = Transformer.from_crs(4326, 2154, always_xy=True)
    detections = []
    for capteur, motif in [("MODIS", "firms_modis_*.csv"), ("VIIRS S-NPP", "firms_viirs-snpp_*.csv")]:
        for f in glob.glob(str(BRONZE / "firms" / "*" / motif)):
            x = pd.read_csv(f)
            x = x[x.type == 0].copy()
            pts = shapely.points(*t.transform(x.longitude.values, x.latitude.values))
            x["code_departement"] = None
            for d, poly in polys.items():
                shapely.prepare(poly)
                x.loc[shapely.contains(poly, pts), "code_departement"] = d
            x = x[x.code_departement.notna()]
            detections.append(pd.DataFrame({
                "capteur": capteur, "date": pd.to_datetime(x.acq_date), "heure": x.acq_time.astype(str).str.zfill(4),
                "latitude": x.latitude, "longitude": x.longitude, "code_departement": x.code_departement,
                "confiance": x.confidence.astype(str), "puissance_mw": x.frp, "jour_nuit": x.daynight,
                "_fichier_source": str(Path(f).relative_to(BRONZE))}))
    pd.concat(detections, ignore_index=True).to_parquet(MARTS / "fct_firms_detections.parquet", index=False)

    # contrôle : IFM à la station de Lyon-Bron avec l'humidité minimale observée
    hum = pd.concat(pd.read_csv(f, sep=";", usecols=["NUM_POSTE", "AAAAMMJJ", "UN"], dtype={"NUM_POSTE": str})
                    for f in glob.glob(str(BRONZE / "meteo_france_quotidien" / "*" / "Q_69_*autres-parametres.csv.gz")))
    hum = hum[hum.NUM_POSTE == "69029001"].assign(date=lambda x: pd.to_datetime(x.AAAAMMJJ.astype(str)))
    st = con.execute("SELECT date, tmax_c, pluie_mm, vent_moyen_ms FROM staging.stg_meteo__quotidien "
                     "WHERE code_station = '69029001' AND date >= DATE '1981-01-01' ORDER BY date").df()
    st["date"] = pd.to_datetime(st.date)
    st = st.merge(hum[["date", "UN"]], on="date", how="left").sort_values("date")
    codes = ifm.serie_ifm(st.tmax_c.values.astype(float), st.UN.values.astype(float),
                          st.vent_moyen_ms.values.astype(float) * 3.6, st.pluie_mm.values.astype(float),
                          st.date.dt.month.values)
    st["ifm_station"] = codes[:, 5]
    st.rename(columns={"UN": "hu_min_pct"}).to_parquet(MARTS / "ifm_station_lyon_bron.parquet", index=False)
    print("tables écrites dans", MARTS)


if __name__ == "__main__":
    main()
