import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from commun import (GRIS, MUET, NIVEAUX, SERIE_1, TEXTE, TEXTE_2, donnees, encadre, entete, filtres, fr, graphique,
                    kpis, mise_en_forme, page, pct)

page("2 · Le coût dépend de l'été")
d = donnees()
filtres(avec_calibrage=False)

dj = d["fct_danger_jour"]
r = dj[(dj.code_departement == "69") & dj.niveau_j1.notna()].copy()
r["jour"] = pd.to_datetime(r.jour)
cout = r.assign(s2=r.niveau_j1 >= 2, s3=r.niveau_j1 >= 3, s4=r.niveau_j1 >= 4).groupby("annee")[["s2", "s3", "s4"]].sum()
m = d["fct_meteo_lyon_bron"].copy()
cs = m.groupby("annee").chaleur_seche.sum()
ref = cs.loc[1991:2020].mean()
annee_max = int(cs.idxmax())
valid = m[m.niveau_mdf_69.notna()]
precision = (valid.chaleur_seche & (valid.niveau_mdf_69 >= 2)).sum() / valid.chaleur_seche.sum()

entete(
    "2 · Le coût dépend de l'été",
    f"Le même seuil a coûté {fr(cout.loc[2024, 's2'])} jours en 2024<br>et {fr(cout.loc[2026, 's2'])} en 2026.",
    "Le nombre de jours de renfort n'est pas une décision : c'est la conséquence du seuil et de la météo. À seuil "
    f"constant, il a été multiplié par {fr(cout.loc[2026, 's2'] / cout.loc[2024, 's2'])} en deux saisons. Une règle chiffrée sur une saison calme serait donc sous-"
    "financée dès l'été suivant. La question utile n'est pas « combien de jours en moyenne », mais « combien de jours "
    "dans une saison comme 2026 », et à quelle fréquence de telles saisons reviennent.")

kpis([(f"Jours au seuil 2 · {a}", fr(cout.loc[a, "s2"]),
       f"seuil 3 : {fr(cout.loc[a, 's3'])} jour{'s' if cout.loc[a, 's3'] > 1 else ''} · seuil 4 : {fr(cout.loc[a, 's4'])}")
      for a in (2024, 2025, 2026)])
encadre("pourquoi",
        f"<b>Pourquoi trois saisons côte à côte ?</b> Une moyenne des trois ({fr(cout.s2.mean())} jours) décrirait une "
        "saison qui n'a pas "
        "existé. Le budget se dimensionne sur la saison chargée, et la question devient de savoir si 2026 était une "
        "exception. Le seuil 4 n'a jamais été atteint dans le Rhône en trois saisons : le retenir reviendrait à ne jamais "
        "déclencher le dispositif.")

# calendrier des niveaux J+1 dans le Rhône
debut = {a: pd.Timestamp(a, 6, 1) for a in cout.index}
r["x"] = [(j - debut[j.year]).days for j in r.jour]
annees = sorted(cout.index, reverse=True)
xs = np.arange(r.x.min(), r.x.max() + 1)
z = [[r.loc[(r.annee == a) & (r.x == x), "niveau_j1"].squeeze() if ((r.annee == a) & (r.x == x)).any() else None
      for x in xs] for a in annees]
dates = [[(debut[a] + pd.Timedelta(days=int(x))).strftime("%d/%m/%Y") for x in xs] for a in annees]
echelle = []
for i, (lib, c) in NIVEAUX.items():
    echelle += [[(i - 1) / 4, c], [i / 4, c]]
fig = go.Figure(go.Heatmap(
    z=z, x=xs, y=[str(a) for a in annees], zmin=0.5, zmax=4.5, colorscale=echelle, xgap=1, ygap=6,
    customdata=dates, hovertemplate="%{customdata} : niveau %{z}<extra></extra>",
    colorbar=dict(title=dict(text="Niveau J+1", font=dict(color=TEXTE_2)), tickvals=[1, 2, 3, 4],
                  ticktext=[v[0] for v in NIVEAUX.values()], tickfont=dict(color=TEXTE_2), len=0.9, thickness=12)))
mois = {0: "1er juin", 30: "1er juil.", 61: "1er août", 92: "1er sept.", 122: "1er oct."}
mise_en_forme(fig, "En 2026, le niveau 2 tient de mi-juin à fin septembre ; en 2024, il se limite à août", 300,
              xaxis=dict(tickvals=list(mois), ticktext=list(mois.values()), showgrid=False),
              yaxis=dict(showgrid=False, type="category", tickfont=dict(color=TEXTE_2, size=14)))
graphique(fig)
st.caption("Niveau de danger J+1 de la Météo des forêts pour le département 69, chaque jour où un bulletin a été publié. "
           "Cases vides : pas de bulletin (hors saison).")

st.markdown("### 2026 était-il une exception ?")
couleurs = [SERIE_1 if a >= 2024 else GRIS for a in cs.index]
fig2 = go.Figure()
fig2.add_bar(x=cs.index, y=cs.values, marker_color=couleurs, showlegend=False,
             hovertemplate="%{x} : %{y:.0f} jours de chaleur sèche<extra></extra>")
fig2.add_hline(y=ref, line=dict(color=MUET, width=1),
               annotation_text=f"moyenne 1991-2020 : {fr(ref, 1)} jours", annotation_font_color=TEXTE_2,
               annotation_position="top left")
for a in sorted(cs.sort_values().index[-3:]):
    fig2.add_annotation(x=a, y=cs[a], text=f"{a} : {fr(cs[a])}", showarrow=False, yshift=12, font=dict(color=TEXTE))
mise_en_forme(fig2, f"{annee_max} : {fr(cs.max())} jours de chaleur sèche à Lyon-Bron, le plus haut niveau depuis 1991",
              360, yaxis=dict(title="Jours par an"), xaxis=dict(dtick=5), bargap=0.25)
graphique(fig2)

p1, p2, p3 = cs.loc[1991:2005].mean(), cs.loc[2006:2020].mean(), cs.loc[2021:2026].mean()
kpis([("Moyenne 1991-2005", fr(p1, 1), "jours de chaleur sèche par an"),
      ("Moyenne 2006-2020", fr(p2, 1), "jours par an"),
      ("Moyenne 2021-2026", fr(p3, 1), f"{fr(p3 / p2, 1)} fois la période précédente")])

encadre("lecture",
        f"Les saisons 2024 à 2026 (en bleu) ne sont pas des accidents isolés. Depuis 2021, Lyon-Bron compte en moyenne "
        f"{fr(p3, 1)} jours de chaleur sèche par an, contre {fr(p2, 1)} entre 2006 et 2020, et deux étés (2022 et 2026) "
        f"dépassent 30 jours. <b>Le budget 2027 doit donc être dimensionné sur une saison de type 2026</b>, soit de "
        f"l'ordre de {fr(cout.loc[2026, 's2'])} jours au seuil 2, et non sur la moyenne des trois saisons connues.",
        "Ce que montrent ces graphiques")

with st.expander("Lecture, méthode et limites"):
    st.markdown(f"""
- **Jour de chaleur sèche** : à Lyon-Bron (station Météo-France 69029001), température maximale ≥ 30 °C et moins de 1 mm
  de pluie cumulée sur les 10 derniers jours. C'est un indicateur de contexte, pas un substitut à la Météo des forêts,
  qui intègre aussi l'état de la végétation et le vent.
- **Validation sur 2024-2026** : {pct(precision)} des jours de chaleur sèche étaient de niveau J+1 ≥ 2 dans le Rhône. En
  revanche, il ne repère qu'une partie des jours de niveau 2 (beaucoup sont liés à la sécheresse de la végétation sans
  forte chaleur) : il sert à comparer les étés entre eux, pas à prévoir les jours de renfort.
- Une seule station : le sud-est lyonnais est plus chaud que les Monts du Beaujolais. Les écarts entre années comptent,
  pas les valeurs absolues.
- Les jours de renfort sont ceux du département 69 entier : le bulletin ne distingue pas le Rhône de la Métropole.
""")
