import plotly.graph_objects as go
import streamlit as st

from commun import (GRIS, GRILLE, MUET, SERIE_1, SERIE_2, TEXTE, TEXTE_2, departements_du_perimetre, donnees, encadre,
                    entete, filtres, fr, graphique, indicateurs, kpis, mise_en_forme, page, pct, variantes)

page("1 · Le seuil")
d = donnees()
f = filtres()
deps = departements_du_perimetre(d, f["perimetre"])
k = indicateurs(d, deps, f["annees"], niveau=f["niveau"], seuil_ha=f["seuil_ha"])
lib_taille = "de plus d'1 ha" if f["seuil_ha"] == 1 else ("de plus de 5 ha" if f["seuil_ha"] == 5 else "")
lib_feux = f"feux {lib_taille}".strip()

entete(
    "1 · Le seuil",
    "Entre le seuil 2 et le seuil 3,<br>on échange de la couverture contre des jours.",
    "La tentation est de chercher le seuil « le plus efficace ». Les données disent autre chose : un jour de renfort au "
    "niveau 3 ne couvre pas nettement plus de feux qu'un jour au niveau 2. Ce qui change entre les deux options, c'est le "
    "nombre de jours mobilisés, et donc la part des feux de la saison qui tombent un jour où le dispositif est en place.")

r = k.loc[3, "rendement"] / k.loc[2, "rendement"] if k.loc[2, "rendement"] else float("nan")
kpis([
    (f"Couverture au seuil 2", pct(k.loc[2, "couverture"]),
     f"{fr(k.loc[2, 'feux_couverts'])} {lib_feux} sur {fr(k.loc[2, 'feux_saison'])} · {fr(k.loc[2, 'jours'])} jours"),
    (f"Couverture au seuil 3", pct(k.loc[3, "couverture"]),
     f"{fr(k.loc[3, 'feux_couverts'])} {lib_feux} sur {fr(k.loc[3, 'feux_saison'])} · {fr(k.loc[3, 'jours'])} jours"),
    ("Feux couverts par jour, seuil 3 ÷ seuil 2", fr(r, 2) if r == r else "—",
     "1 = un jour de niveau 3 « rapporte » autant qu'un jour de niveau 2"),
])
encadre("pourquoi",
        "<b>Pourquoi ce rapport ?</b> Le <b>rendement</b> R(s) est le nombre de feux couverts par jour de renfort. "
        "Il se décompose exactement en <b>précision</b> (la part des jours renforcés où survient au moins un feu) × "
        "<b>multiplicité</b> (le nombre de feux ces jours-là). Si R(3) était très supérieur à R(2), relever le seuil "
        "concentrerait les moyens sur les bons jours. Un rapport proche de 1 dit l'inverse : les jours de niveau 2 sont "
        "presque aussi « productifs », et renoncer au seuil 2, c'est surtout renoncer aux feux de ces jours-là.")

if f["perimetre"] == "rhone":
    encadre("alerte", f"Le Rhône seul ne compte que {fr(k.loc[1, 'feux_saison'] + k.loc[1, 'feux_hors_saison'])} "
            f"{lib_feux} sur les saisons choisies : les pourcentages sautent d'un extrême à l'autre avec un seul feu. "
            "Ils sont affichés pour transparence, pas pour décider.")

b = k.loc[[2, 3, 4]]
etiq = [f"Seuil {s}" for s in b.index]
fig = go.Figure()
fig.add_bar(name="Jours de la saison mobilisés", x=etiq, y=100 * b.part_jours, marker_color=SERIE_1,
            text=[pct(v) for v in b.part_jours], textposition="outside", textfont_color=TEXTE_2,
            customdata=b.jours, hovertemplate="%{x} : %{customdata} jours-département (%{y:.1f} %)<extra></extra>")
fig.add_bar(name=f"{lib_feux.capitalize()} de la saison couverts", x=etiq, y=100 * b.couverture.fillna(0),
            marker_color=SERIE_2, text=[pct(v) for v in b.couverture], textposition="outside", textfont_color=TEXTE_2,
            customdata=b.feux_couverts, hovertemplate="%{x} : %{customdata:.0f} feux couverts (%{y:.1f} %)<extra></extra>")
mise_en_forme(fig, "Ce que chaque seuil mobilise, et ce qu'il couvre", barmode="group", bargap=0.35, bargroupgap=0.08,
              yaxis=dict(title="% de la saison", range=[0, 105]))
graphique(fig)

tab = b.assign(**{"Seuil": etiq}).set_index("Seuil")
tab = tab.rename(columns={"jours": "Jours de renfort", "feux_couverts": "Feux couverts",
                          "couverture": "Couverture", "rendement": "Feux par jour", "precision": "Jours avec un feu"})
with st.expander("Voir le tableau"):
    st.dataframe(tab[["Jours de renfort", "Feux couverts", "Couverture", "Feux par jour", "Jours avec un feu"]]
                 .style.format({"Jours de renfort": "{:.0f}", "Feux couverts": "{:.0f}", "Couverture": "{:.1%}",
                                "Feux par jour": "{:.3f}", "Jours avec un feu": "{:.1%}"}), use_container_width=True)

st.markdown("### La conclusion résiste-t-elle à d'autres choix ?")
v = variantes(d)
noms = list(v.index)[::-1]
fig2 = go.Figure()
for n in noms:
    fig2.add_shape(type="line", x0=100 * v.loc[n, "C3"], x1=100 * v.loc[n, "C2"], y0=n, y1=n,
                   line=dict(color=GRILLE, width=3))
fig2.add_scatter(name="Seuil 3", x=100 * v.loc[noms, "C3"], y=noms, mode="markers",
                 marker=dict(color=GRIS, size=12, line=dict(color="#0a0a0b", width=2)),
                 hovertemplate="%{y}<br>Seuil 3 : %{x:.0f} %<extra></extra>")
fig2.add_scatter(name="Seuil 2", x=100 * v.loc[noms, "C2"], y=noms, mode="markers",
                 marker=dict(color=SERIE_2, size=12, line=dict(color="#0a0a0b", width=2)),
                 hovertemplate="%{y}<br>Seuil 2 : %{x:.0f} %<extra></extra>")
ratio_c = v.C2 / v.C3
mise_en_forme(fig2, f"Couverture : le seuil 2 reste {fr(ratio_c.min())} à {fr(ratio_c.max())} fois au-dessus<br>du seuil 3, "
                    "quelle que soit la variante", 360,
              xaxis=dict(title="Part des feux de la saison couverts (%)", range=[0, 100]))
c1, c2 = st.columns([3, 2])
with c1:
    graphique(fig2)
with c2:
    fig3 = go.Figure()
    fig3.add_vline(x=1, line=dict(color=MUET, width=1))
    fig3.add_scatter(x=v.loc[noms, "R3_R2"], y=noms, mode="markers+text", text=[fr(x, 2) for x in v.loc[noms, "R3_R2"]],
                     textposition="middle right", textfont=dict(color=TEXTE_2),
                     marker=dict(color=TEXTE, size=11), showlegend=False,
                     hovertemplate="%{y}<br>R(3) ÷ R(2) = %{x:.2f}<extra></extra>")
    mise_en_forme(fig3, "Feux par jour de renfort : le seuil 3<br>n'est pas nettement plus « productif »", 360,
                  xaxis=dict(title="Feux par jour, seuil 3 ÷ seuil 2", range=[0, 2.6]),
                  yaxis=dict(showticklabels=False))
    graphique(fig3)

encadre("lecture",
        "Si le seuil 3 était un meilleur seuil, on verrait ses points gris près des points orange à gauche, et un rapport "
        "nettement au-dessus de 1 à droite. Ce n'est pas le cas : la couverture s'effondre dans les six variantes, et le "
        f"rapport de rendement oscille autour de 1 (de {fr(v.R3_R2.min(), 2)} à {fr(v.R3_R2.max(), 2)}). Il ne dépasse "
        "franchement 1 qu'à l'échelle nationale, "
        "où les niveaux 3 et 4 concentrent les grands feux méditerranéens. <b>Le choix entre 2 et 3 se joue donc sur le "
        "nombre de jours que le SDMIS peut financer</b>, pas sur un gain d'efficacité.",
        "Ce que montrent ces graphiques")

with st.expander("Lecture, méthode et limites"):
    st.markdown(f"""
- **Jours de renfort J(s)** : couples département × jour de la saison où le niveau {'J+1' if f['niveau'] == 'niveau_j1' else 'J+2'}
  de la Météo des forêts est au moins égal au seuil. Pour la région, ce sont des jours-département cumulés.
- **Couverture C(s)** = feux survenus un jour de niveau ≥ s ÷ feux survenus un jour avec bulletin. Les feux hors saison
  du bulletin ({fr(k.loc[1, 'feux_hors_saison'])} ici) sont exclus et comptés à part : aucun seuil ne peut les couvrir.
- **Rendement R(s)** = feux couverts ÷ jours de renfort = précision × multiplicité (décomposition exacte).
- Jointure feux × bulletin sur (département, date d'alerte = date d'émission + 1 jour). Le niveau n'existe qu'au département.
- Un feu survenu un jour renforcé n'est pas un feu « évité » : l'indicateur mesure l'adéquation du déclenchement, pas
  l'efficacité des moyens.
- Limites : deux saisons communes seulement (archives Météo des forêts depuis 2024, BDIFF jusqu'en 2025) ; « 1 ha » est
  la définition provisoire du feu significatif, à confirmer avec le SDMIS ; la BDIFF sous-représente fortement le Rhône
  (page 3).
""")
