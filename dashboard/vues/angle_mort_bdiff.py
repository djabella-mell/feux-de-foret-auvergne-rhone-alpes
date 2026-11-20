import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from commun import (GRIS, MUET, SERIE_1, SERIE_2, TEXTE, TEXTE_2, donnees, encadre, entete, filtres, fr, graphique,
                    kpis, mise_en_forme, page, pct)

page("3 · L'angle mort de la BDIFF")
d = donnees()
filtres(avec_calibrage=False)

s = d["fct_sdis_feux_vegetation"]
detail = s[s.feux_vegetation.notna() & s.annee.between(2014, 2024)]
r69 = s[s.code_departement == "69"].sort_values("annee")
d69 = detail[detail.code_departement == "69"]
part69 = d69.feux_bdiff.sum() / d69.feux_vegetation.sum()
metro = detail[detail.code_departement.str.len() == 2]
part_fr = metro.feux_bdiff.sum() / metro.feux_vegetation.sum()
a22 = r69.set_index("annee").loc[2022]

entete(
    "3 · L'angle mort de la BDIFF",
    f"Dans le Rhône, la base nationale voit<br>un feu de végétation sur {fr(1 / part69)}.",
    "La BDIFF ne recense que les feux de forêt et de terres boisées, déclarés par les services. Les statistiques "
    "annuelles de la Sécurité civile comptent, elles, toutes les interventions du SDMIS pour feux de végétation : "
    "forêts, mais aussi chaumes, friches, talus. L'écart entre les deux n'est donc pas une erreur, mais il dit une chose "
    "simple : <b>une règle de seuil calibrée sur les seuls feux BDIFF du Rhône repose sur une infime partie de "
    "l'activité réelle</b>.")

kpis([
    ("Part vue par la BDIFF · Rhône", pct(part69, 1), f"{fr(d69.feux_bdiff.sum())} feux sur {fr(d69.feux_vegetation.sum())} interventions, 2014-2024"),
    ("Part vue par la BDIFF · France", pct(part_fr, 1), "même période, départements de métropole"),
    ("Rhône, année 2022", f"{fr(a22.feux_vegetation)} → {fr(a22.feux_bdiff)}", "interventions SDMIS → feu(x) dans la BDIFF"),
])
encadre("pourquoi",
        "<b>Pourquoi ce rapport ?</b> Il mesure ce que la source de calibrage laisse de côté. Un rapport bas ne prouve pas "
        "une sous-déclaration (les feux agricoles n'ont pas à figurer dans la BDIFF), mais il interdit de lire l'absence de "
        "feux BDIFF comme une absence de risque. En 2022, année de sécheresse exceptionnelle, le Rhône a connu près de neuf "
        "cents interventions pour feux de végétation, et la base nationale n'en retient qu'un.")

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12,
                    subplot_titles=("Interventions du SDMIS pour feux de végétation (DGSCGC)",
                                    "Feux de forêt du Rhône dans la BDIFF"))
fig.add_bar(x=r69.annee, y=r69.feux_vegetation, marker_color=SERIE_1, row=1, col=1, showlegend=False,
            hovertemplate="%{x} : %{y:.0f} interventions<extra></extra>")
fig.add_bar(x=r69.annee, y=r69.feux_bdiff, marker_color=SERIE_2, row=2, col=1, showlegend=False,
            hovertemplate="%{x} : %{y:.0f} feux BDIFF<extra></extra>")
fig.add_annotation(x=2011.5, y=500, text="non détaillé<br>2010-2013", showarrow=False, font=dict(color=MUET, size=12),
                   row=1, col=1)
fig.add_annotation(x=2022, y=a22.feux_vegetation, text=f"2022 : {fr(a22.feux_vegetation)}", showarrow=False, yshift=12,
                   font=dict(color=TEXTE), row=1, col=1)
fig.add_annotation(x=2015, y=r69.set_index("annee").loc[2015, "feux_bdiff"], text="2015 : 41, dont 35 de plus d'1 ha",
                   showarrow=False, yshift=12, font=dict(color=TEXTE), row=2, col=1)
mise_en_forme(fig, "Les pics d'activité du SDMIS (2015, 2019, 2022) : seul 2015 laisse une trace nette dans la BDIFF", 520,
              bargap=0.25)
for ann in fig.layout.annotations[:2]:
    ann.font = dict(color=TEXTE_2, size=13)
    ann.x, ann.xanchor = 0, "left"
fig.update_xaxes(dtick=2)
fig.update_layout(margin=dict(t=40))
graphique(fig)

st.markdown("### Le Rhône face aux autres départements de la région")
par = (detail[detail.code_region == "84"].groupby(["code_departement", "libelle_departement"])
       [["feux_bdiff", "feux_vegetation"]].sum().reset_index())
par["part"] = par.feux_bdiff / par.feux_vegetation
par = par.sort_values("part")
rang = list(par.code_departement).index("69") + 1
fig2 = go.Figure(go.Bar(
    x=100 * par.part, y=par.libelle_departement, orientation="h",
    marker_color=[SERIE_1 if c == "69" else GRIS for c in par.code_departement],
    text=[pct(v, 1) for v in par.part], textposition="outside", textfont=dict(color=TEXTE_2),
    customdata=par[["feux_bdiff", "feux_vegetation"]],
    hovertemplate="%{y} : %{customdata[0]:.0f} feux BDIFF pour %{customdata[1]:.0f} interventions<extra></extra>"))
fig2.add_vline(x=100 * part_fr, line=dict(color=MUET, width=1),
               annotation_text=f"France : {pct(part_fr, 1)}", annotation_font_color=TEXTE_2,
               annotation_position="top right")
mise_en_forme(fig2, f"Sur {len(par)} départements de la région, le Rhône est au {rang}ᵉ rang des plus mal couverts par la BDIFF", 440,
              xaxis=dict(title="Feux BDIFF pour 100 interventions pour feux de végétation, 2014-2024", range=[0, 19]),
              showlegend=False)
graphique(fig2)

st.markdown("### Et 2026 ?")
p = d["ref_presse_2026"].set_index("indicateur")
v26 = p.loc["feux de végétation depuis le début de l'année 2026", "valeur"]
v25 = p.loc["feux de végétation sur la saison 2025", "valeur"]
kpis([("Feux de végétation au 15 juillet 2026", fr(v26), "chiffre SDMIS relayé par la presse"),
      ("Sur toute la saison 2025", fr(v25), "chiffre SDMIS relayé par la presse"),
      ("Écart, à mi-saison", f"+{pct(v26 / v25 - 1)}", "la saison 2026 n'était pas finie")])
encadre("alerte",
        "La BDIFF ne publiera la saison 2026 qu'en 2027, et le fichier d'interventions du SDMIS n'a pas encore été transmis. "
        "Ces chiffres de presse sont un <b>indicateur de confiance faible</b> : ils ne servent ni au calcul des KPIs ni au "
        "calibrage, seulement à confirmer que 2026 a été une saison hors norme dans le Rhône, comme le montrent les "
        "bulletins (page 2).")
encadre("lecture",
        "La règle de seuil se calibre aujourd'hui sur la région, faute de feux recensés dans le Rhône. <b>La demande "
        "prioritaire au SDMIS est son fichier d'interventions « feux de végétation » 2015-2026</b>, avec la date, la "
        "commune et la surface : il permettra de recalculer la couverture du seuil sur le département lui-même, et de "
        "couvrir 2026.", "Ce que cela change pour la décision")

with st.expander("Lecture, méthode et limites"):
    st.markdown("""
- **Interventions pour feux de végétation** : rubrique « Feux de végétations » des statistiques annuelles des services
  d'incendie et de secours (DGSCGC, data.gouv.fr), une ligne par SIS et par an. Le détail n'existe pas pour 2010-2013
  (seul le total des incendies est publié). Le BMPM et la BSPP sont exclus du calcul par département.
- **Feux BDIFF** : tous les feux de la BDIFF du département pour la même année, quelle que soit leur surface.
- Les deux sources ne mesurent pas le même objet : une intervention peut concerner un feu de jardin, de chaume ou de
  talus, et un feu peut donner lieu à plusieurs interventions. Le rapport décrit une couverture, pas un taux d'erreur.
- Chiffres 2026 : articles de presse citant le SDMIS ou la préfecture (Lyon Capitale, info.fr), conservés dans la source
  `presse` de l'entrepôt avec leur lien. Confiance faible.
""")
