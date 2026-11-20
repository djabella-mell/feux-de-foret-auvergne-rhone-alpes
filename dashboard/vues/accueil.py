import plotly.graph_objects as go
import streamlit as st

from commun import (SERIE_1, SERIE_2, TEXTE_2, departements_du_perimetre, donnees, encadre, entete, filtres, fr,
                    graphique, indicateurs, kpis, mise_en_forme, page, pct)

page("Saison feux 2027 · SDMIS 69")
d = donnees()
filtres(avec_calibrage=False)

ara = indicateurs(d, departements_du_perimetre(d, "region"), [2024, 2025])
dj = d["fct_danger_jour"]
r69 = dj[(dj.code_departement == "69") & dj.niveau_j1.notna()]
jours69 = r69.assign(s2=r69.niveau_j1 >= 2).groupby("annee").s2.sum()
sis = d["fct_sdis_feux_vegetation"]
s69 = sis[(sis.code_departement == "69") & sis.feux_vegetation.notna() & sis.annee.between(2014, 2024)]
part_bdiff = s69.feux_bdiff.sum() / s69.feux_vegetation.sum()

entete(
    "SDMIS 69 · Saison feux 2027 · dix sources publiques consolidées",
    "Le seuil 2 couvre huit feux sur dix.<br>Son coût, lui, dépend de l'été.",
    f"En Auvergne-Rhône-Alpes, déclencher le dispositif renforcé dès le niveau 2 de la Météo des forêts aurait "
    f"couvert <b>{pct(ara.loc[2, 'couverture'])} des feux de plus d'1 ha</b> des saisons 2024 et 2025, en mobilisant "
    f"{pct(ara.loc[2, 'part_jours'])} des jours. Le seuil 3 n'en couvre que {pct(ara.loc[3, 'couverture'])}. "
    f"Mais dans le Rhône, ce même seuil 2 a représenté <b>{fr(jours69[2024])} jours en 2024, {fr(jours69[2025])} en 2025 "
    f"et {fr(jours69[2026])} en 2026</b>. Le choix du seuil est donc d'abord un choix de budget, et le budget doit être "
    "dimensionné sur les étés chauds, qui se multiplient.")

kpis([
    ("Feux ≥ 1 ha couverts au seuil 2", pct(ara.loc[2, "couverture"]),
     f"contre {pct(ara.loc[3, 'couverture'])} au seuil 3 · région, 2024-2025"),
    ("Jours de renfort au seuil 2, Rhône 2026", fr(jours69[2026]),
     f"× {fr(jours69[2026] / jours69[2024], 0)} par rapport à 2024"),
    ("Feux de végétation vus par la BDIFF, Rhône", pct(part_bdiff, 1),
     f"{fr(s69.feux_bdiff.sum())} sur {fr(s69.feux_vegetation.sum())} interventions SDMIS, 2014-2024"),
])

encadre("pourquoi",
        "<b>Pourquoi ces trois indicateurs ?</b> Le premier dit ce que le seuil achète : la part des feux significatifs "
        "qui surviennent un jour de renfort. Il ne vaut rien sans le deuxième, qui dit ce qu'il coûte : un nombre de jours "
        "mobilisés, qui varie du simple au huitième selon l'été. Le troisième dit à quel point on peut s'y fier dans le "
        f"Rhône : la base nationale des feux de forêt n'y enregistre qu'un feu pour {fr(1 / part_bdiff)} interventions "
        "du SDMIS pour feux de végétation, "
        "si bien que la règle doit être calibrée sur la région, puis vérifiée avec les données du SDMIS. Un « nombre "
        "total de feux depuis 2006 » serait une métrique de vanité : il grossit chaque année et ne départage aucune "
        "option.")

b = ara.loc[[2, 3, 4]]
etiq = [f"Seuil {s}" for s in b.index]
fig = go.Figure()
fig.add_bar(name="Jours de la saison mobilisés", x=etiq, y=100 * b.part_jours, marker_color=SERIE_1,
            text=[pct(v) for v in b.part_jours], textposition="outside", textfont_color=TEXTE_2,
            hovertemplate="%{x} : %{y:.1f} % des jours-département de la saison<extra></extra>")
fig.add_bar(name="Feux ≥ 1 ha de la saison couverts", x=etiq, y=100 * b.couverture, marker_color=SERIE_2,
            text=[pct(v) for v in b.couverture], textposition="outside", textfont_color=TEXTE_2,
            hovertemplate="%{x} : %{y:.1f} % des feux ≥ 1 ha survenus pendant la saison<extra></extra>")
mise_en_forme(fig, f"Avec {pct(b.loc[2, 'part_jours'])} des jours, le seuil 2 couvre {pct(b.loc[2, 'couverture'])} des feux ; "
                   "le seuil 3 laisse passer presque tout",
              barmode="group", bargap=0.35, bargroupgap=0.08, yaxis=dict(title="% de la saison", range=[0, 100]))
graphique(fig)
st.caption(f"Auvergne-Rhône-Alpes, saisons 2024 et 2025 · {fr(ara.loc[1, 'jours'])} jours-département de bulletin · "
           f"{fr(ara.loc[1, 'feux_saison'])} feux ≥ 1 ha pendant la saison, et {fr(ara.loc[1, 'feux_hors_saison'])} hors "
           "saison, que le bulletin ne couvre pas.")

st.markdown("### Les quatre pièces du dossier")
cartes = [
    ("vues/seuil.py", "1 · Le seuil", "Couverture contre jours mobilisés : que gagne-t-on vraiment à passer du seuil 3 au seuil 2 ?"),
    ("vues/cout_ete.py", "2 · Le coût dépend de l'été", f"De {fr(jours69.get(2024))} à {fr(jours69.get(2026))} jours : 2026 est-il une anomalie, ou le nouveau standard ?"),
    ("vues/angle_mort_bdiff.py", "3 · L'angle mort de la BDIFF", "Pourquoi la base nationale ne suffit pas à fixer une règle pour le Rhône."),
    ("vues/ou_renforcer.py", "4 · Où renforcer", "La forêt est au nord-ouest du département : quelles communes sont loin d'une caserne ?"),
]
for col, (cible, n, q) in zip(st.columns(4), cartes):
    col.markdown(f'<div class="carte"><div class="n">{n}</div><div class="q">{q}</div></div>', unsafe_allow_html=True)
    col.page_link(cible, label="Ouvrir", icon=":material/arrow_forward:")
st.caption("Sur la page « Le seuil », les filtres du panneau de gauche recalculent tous les indicateurs.")
