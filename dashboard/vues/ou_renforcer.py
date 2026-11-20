import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from shapely.geometry import shape

from commun import (GRIS, MUET, SERIE_1, TEXTE, TEXTE_2, donnees, encadre, entete, filtres, fr, graphique, kpis,
                    mise_en_forme, page, pct)

page("4 · Où renforcer")
d = donnees()
filtres(avec_calibrage=False)


@st.cache_data
def communes() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    c = d["dim_communes_rhone"].copy()
    k = d["dim_casernes"]
    k = k[k.cis != "Hors CIS"].reset_index(drop=True)
    points = [shape(json.loads(g)).representative_point() for g in c.geojson]
    c["lon"], c["lat"] = [p.x for p in points], [p.y for p in points]
    la1, lo1 = np.radians(c.lat.values)[:, None], np.radians(c.lon.values)[:, None]
    la2, lo2 = np.radians(k.lat.values)[None], np.radians(k.lon.values)[None]
    h = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    dist = 2 * 6371 * np.arcsin(np.sqrt(h))
    c["distance_cis_km"] = dist.min(axis=1)
    c["cis_proche"] = k.nom_site.values[dist.argmin(axis=1)]
    def anneaux(g):
        geom = shape(json.loads(g))
        polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
        return [list(p.exterior.coords) for p in polys]
    geo = {code: anneaux(g) for code, g in zip(c.code_commune, c.geojson)}
    return c.drop(columns="geojson"), k, geo


c, k, geo = communes()
foret = c.surface_foret_ha.sum()
boisees = c[c.taux_boisement >= 0.4]

entete(
    "4 · Où renforcer",
    f"{len(boisees)} communes portent {pct(boisees.surface_foret_ha.sum() / foret)} de la forêt du Rhône,<br>"
    "et sont plus loin des secours que les autres.",
    "Aucune commune du Rhône n'est classée « feu de forêt » dans le dossier départemental des risques majeurs, et la "
    "BDIFF n'y recense presque aucun feu. Le risque n'est pas absent pour autant : il se concentre là où la forêt est "
    "dense, surtout au nord-ouest du département (Haut-Beaujolais, monts de Tarare), c'est-à-dire là où les casernes "
    "du SDMIS sont les plus espacées. <b>C'est là qu'un prépositionnement les jours de niveau 2 a le plus "
    "de sens.</b>")

kpis([
    ("Forêt du Rhône", f"{fr(foret)} ha", f"dont {pct(c[c.code_ctcd == '69D'].surface_foret_ha.sum() / foret)} hors Métropole"),
    ("Communes boisées à 40 % ou plus", fr(len(boisees)), f"{pct(boisees.surface_foret_ha.sum() / foret)} de la forêt du département"),
    ("Distance médiane à la caserne la plus proche", f"{fr(boisees.distance_cis_km.median(), 1)} km",
     f"contre {fr(c[c.taux_boisement < 0.4].distance_cis_km.median(), 1)} km pour les autres communes"),
    ("Communes classées « feu de forêt »", f"{fr(c.risque_feu_ddrm.sum())} / {fr(len(c))}", "DDRM du Rhône (GASPAR)"),
])
encadre("pourquoi",
        "<b>Pourquoi ces indicateurs ?</b> Prépositionner un engin, c'est réduire le délai d'arrivée là où un départ de feu "
        "peut s'étendre. Il faut donc croiser deux choses : <b>la quantité de combustible</b> (le taux de boisement de la "
        "commune) et <b>l'éloignement des moyens</b> (la distance à la caserne la plus proche). Les feux passés, "
        "trop rares dans la BDIFF du Rhône, ne peuvent pas servir à désigner ces communes.")

st.sidebar.markdown("### Règle de repérage")
seuil_bois = st.sidebar.slider("Taux de boisement minimal", 20, 70, 40, 5, format="%d %%") / 100
seuil_km = st.sidebar.slider("Distance minimale à la caserne la plus proche", 2.0, 6.0, 4.0, 0.5, format="%.1f km")
c["candidate"] = (c.taux_boisement >= seuil_bois) & (c.distance_cis_km >= seuil_km)
cand = c[c.candidate].sort_values("surface_foret_ha", ascending=False)

# Carte en coordonnées planes (aucun fond de carte à télécharger : fonctionne hors ligne).
CLASSES = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 101)]
VERTS = ["#1b241d", "#1f3d26", "#245a30", "#2c7a3a", "#3f9b4c", "#6bbd73", "#a6e0ad"]
fig = go.Figure()
for (bas, haut), vert in zip(CLASSES, VERTS):
    sel = c[(100 * c.taux_boisement >= bas) & (100 * c.taux_boisement < haut)]
    xs, ys = [], []
    for code in sel.code_commune:
        for anneau in geo[code]:
            xs += [p[0] for p in anneau] + [None]
            ys += [p[1] for p in anneau] + [None]
    fig.add_trace(go.Scatter(x=xs, y=ys, fill="toself", fillcolor=vert, mode="lines",
                             line=dict(color="#0a0a0b", width=0.6), hoverinfo="skip",
                             name=f"{bas}-{haut} %" if haut <= 100 else f"{bas} % et plus", legendgroup="bois",
                             legendgrouptitle=dict(text="Boisement") if bas == 0 else None))
fig.add_trace(go.Scatter(
    x=c.lon, y=c.lat, mode="markers", marker=dict(size=14, opacity=0), showlegend=False,
    customdata=np.stack([c.libelle_commune, 100 * c.taux_boisement, c.surface_foret_ha, c.distance_cis_km,
                         c.cis_proche], axis=1),
    hovertemplate="<b>%{customdata[0]}</b><br>Boisement : %{customdata[1]:.0f} %<br>Forêt : %{customdata[2]:,.0f} ha"
                  "<br>%{customdata[4]} à %{customdata[3]:.1f} km<extra></extra>"))
fig.add_trace(go.Scatter(
    x=k.lon, y=k.lat, mode="markers", marker=dict(size=6, color=TEXTE, line=dict(width=1, color="#0a0a0b")),
    name="Caserne du SDMIS", text=k.nom_site + " (" + k.cis.fillna("") + ")", hovertemplate="%{text}<extra></extra>"))
fig.add_trace(go.Scatter(
    x=cand.lon, y=cand.lat, mode="markers",
    marker=dict(size=16, color="rgba(0,0,0,0)", line=dict(width=2.5, color=SERIE_1)),
    name="Commune repérée", text=cand.libelle_commune, hovertemplate="%{text}<extra>commune repérée</extra>"))
mise_en_forme(fig, f"{len(cand)} communes cumulent forêt dense et éloignement d'une caserne", 760,
              xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor="x", scaleratio=1 / np.cos(np.radians(45.87))),
              legend=dict(orientation="v", x=1, xanchor="left", y=1, yanchor="top", font=dict(color=TEXTE_2),
                          groupclick="toggleitem"))
fig.update_layout(margin=dict(l=0, r=0, t=12, b=0), hovermode="closest")
graphique(fig)

st.markdown("### La règle de repérage, commune par commune")
fig2 = go.Figure()
for est, couleur, nom in [(False, GRIS, "Autres communes"), (True, SERIE_1, "Communes repérées")]:
    sel = c[c.candidate == est]
    fig2.add_trace(go.Scatter(
        x=100 * sel.taux_boisement, y=sel.distance_cis_km, mode="markers", name=nom,
        marker=dict(color=couleur, size=np.clip(np.sqrt(sel.surface_foret_ha) / 2.2, 5, 30), line=dict(width=1, color="#0a0a0b")),
        customdata=np.stack([sel.libelle_commune, sel.surface_foret_ha, sel.cis_proche], axis=1),
        hovertemplate="<b>%{customdata[0]}</b><br>Boisement : %{x:.0f} %<br>Forêt : %{customdata[1]:,.0f} ha<br>"
                      "Caserne de %{customdata[2]} à %{y:.1f} km<extra></extra>"))
fig2.add_vline(x=100 * seuil_bois, line=dict(color=MUET, width=1, dash="dot"))
fig2.add_hline(y=seuil_km, line=dict(color=MUET, width=1, dash="dot"))
fig2.add_annotation(x=72, y=6.4, text="forêt dense<br>et moyens éloignés", showarrow=False, xanchor="right",
                    yanchor="top", align="right", font=dict(color=TEXTE_2))
mise_en_forme(fig2, "Les communes les plus boisées sont, en moyenne, plus loin d'une caserne", 460,
              xaxis=dict(title="Taux de boisement de la commune", ticksuffix=" %", range=[-2, 73]),
              yaxis=dict(title="Distance à la caserne la plus proche (km, à vol d'oiseau)", range=[0, 6.6]))
st.caption("Taille des points : surface de forêt de la commune.")
graphique(fig2)

kpis([("Communes repérées", fr(len(cand)), f"boisement ≥ {pct(seuil_bois)} et caserne à {fr(seuil_km, 1)} km ou plus"),
      ("Part de la forêt du Rhône", pct(cand.surface_foret_ha.sum() / foret), f"{fr(cand.surface_foret_ha.sum())} ha"),
      ("Feux BDIFF 2006-2025 dans ces communes", fr(cand.feux_bdiff_2006_2025.sum()),
       f"sur {fr(c.feux_bdiff_2006_2025.sum())} dans tout le département")])

tableau = cand[["libelle_commune", "code_ctcd", "taux_boisement", "surface_foret_ha", "distance_cis_km", "cis_proche",
                "feux_bdiff_2006_2025"]].rename(columns={
    "libelle_commune": "Commune", "code_ctcd": "Territoire", "taux_boisement": "Boisement",
    "surface_foret_ha": "Forêt (ha)", "distance_cis_km": "Distance (km)", "cis_proche": "Caserne la plus proche",
    "feux_bdiff_2006_2025": "Feux BDIFF 2006-2025"})
tableau["Territoire"] = tableau["Territoire"].map({"69D": "Département", "69M": "Métropole"})
tableau["Boisement"] = 100 * tableau["Boisement"]
tableau["Forêt (ha)"] = tableau["Forêt (ha)"].round()
st.dataframe(tableau, hide_index=True, use_container_width=True, column_config={
    "Commune": st.column_config.TextColumn(width="medium"),
    "Boisement": st.column_config.NumberColumn(format="%.0f %%"),
    "Forêt (ha)": st.column_config.NumberColumn(format="localized"),
    "Distance (km)": st.column_config.NumberColumn(format="%.1f km"),
    "Caserne la plus proche": st.column_config.TextColumn(width="large")})

encadre("lecture",
        "Ces communes sont une <b>liste de travail</b> pour l'état-major : y prépositionner un engin feux de forêt, ou "
        "y avancer un groupe, les jours où la Météo des forêts annonce le niveau 2. La règle se règle dans le panneau de "
        "gauche ; elle ne remplace pas l'analyse de couverture opérationnelle du SDACR, qui raisonne en temps de trajet "
        "réel et en disponibilité des équipes.", "Ce que cela change pour la décision")

with st.expander("Lecture, méthode et limites"):
    st.markdown("""
- **Taux de boisement** : surface de forêt de la BD Forêt v2 (IGN) intersectée avec le contour de chaque commune
  (ADMIN EXPRESS), rapportée à la surface communale. Les landes sont exclues.
- **Casernes** : 101 sites opérationnels du SDMIS, regroupés en 24 centres d'incendie et de secours (CIS)
  (data.grandlyon.com, fiches mises à jour pour la plupart en 2020-2021). Les 7 sites « Hors CIS » (état-major, logistique,
  école) sont écartés.
- **Distance** : à vol d'oiseau, entre un point intérieur de la commune et la caserne la plus proche. C'est un indicateur
  d'éloignement, pas un temps d'intervention : le relief et le réseau routier du Haut-Beaujolais allongent les trajets.
- **Ce que l'on ignore** : l'effectif et la disponibilité de chaque caserne (volontaires ou professionnels), les engins
  disponibles, les accès aux massifs. Ces données appartiennent au SDMIS.
- Le classement DDRM vient de la base GASPAR (risques par commune) ; aucune commune du Rhône n'y porte le risque
  « feu de forêt ».
""")
