import pandas as pd
import streamlit as st

from commun import donnees, encadre, entete, filtres, fr, kpis, page

page("5 · Sources et méthode")
d = donnees()
filtres(avec_calibrage=False)

journal = d.get("_journal_sources", pd.DataFrame())
tests = d.get("_qualite_tests", pd.DataFrame())

SOURCES = pd.DataFrame([
    ("bdiff", "BDIFF, base de données sur les incendies de forêt", "MASA · IGN", "2006-2025",
     "Feux de forêt déclarés : date, commune, surface", "Usage non commercial, citation obligatoire, pas de redistribution",
     "https://bdiff.agriculture.gouv.fr/"),
    ("meteo_des_forets", "Météo des forêts, données expertisées", "Météo-France", "juin 2024 - oct. 2026",
     "Niveau de danger J+1 et J+2 par département", "Licence Ouverte 2.0", "https://meteo.data.gouv.fr/"),
    ("meteo_france_quotidien", "Données climatologiques quotidiennes du Rhône", "Météo-France", "1991-2026 (Lyon-Bron)",
     "Contexte de long terme : jours de chaleur sèche", "Licence Ouverte 2.0", "https://meteo.data.gouv.fr/"),
    ("dgscgc_interventions_sis", "Statistiques des services d'incendie et de secours", "DGSCGC, ministère de l'Intérieur",
     "2008-2024", "Interventions pour feux de végétation par SIS", "Licence Ouverte 2.0", "https://www.data.gouv.fr/"),
    ("bd_foret_v2", "BD Forêt V2", "IGN", "2014-2021 selon le département", "Surface forestière par commune",
     "Licence Ouverte 2.0", "https://geoservices.ign.fr/bdforet"),
    ("admin_express_cog", "ADMIN EXPRESS COG", "IGN", "1er janvier 2026", "Contours des communes et départements",
     "Licence Ouverte 2.0", "https://geoservices.ign.fr/adminexpress"),
    ("cog", "Code officiel géographique", "Insee", "2026", "Référentiel des communes, départements, régions",
     "Licence Ouverte 2.0", "https://www.insee.fr/fr/information/2560452"),
    ("gaspar", "GASPAR, risques par commune (DDRM)", "Géorisques (MTE)", "état 2026",
     "Communes classées « feu de forêt »", "Licence Ouverte 2.0",
     "https://www.georisques.gouv.fr/donnees/bases-de-donnees/base-gaspar"),
    ("sdmis_casernes", "Casernes du SDMIS", "SDMIS · Métropole de Lyon", "état 2026",
     "Position des 101 casernes (24 CIS)", "Non précisée dans la fiche, à vérifier",
     "https://data.grandlyon.com/"),
    ("presse", "Chiffres 2026 relayés par la presse", "Presse locale", "été 2026",
     "Contexte 2026 seulement, confiance faible", "Citation courte avec lien", "https://www.lyoncapitale.fr/"),
], columns=["source", "Jeu de données", "Producteur", "Période", "Usage dans le tableau de bord", "Licence", "Lien"])

entete(
    "5 · Sources et méthode",
    "Dix sources publiques, une base unique,<br>des règles qualité exécutées à chaque chargement.",
    "Chaque chiffre de ce tableau de bord se recalcule depuis les fichiers d'origine, conservés tels quels et datés. "
    "Cette page dit d'où vient chaque donnée, ce qu'elle permet de conclure et ce qu'elle ne permet pas.")

bloquantes = tests[(tests.decision == "bloquer") & (tests.statut != "réussi")] if len(tests) else tests
kpis([
    ("Sources publiques", fr(len(SOURCES)), "téléchargées et conservées dans leur format d'origine"),
    ("Lignes chargées", fr(journal.lignes.sum()) if len(journal) else "–",
     f"{fr(journal.rejets.sum())} rejetées et tracées" if len(journal) else ""),
    ("Règles qualité", fr(len(tests)) if len(tests) else "–",
     f"{fr(len(bloquantes))} règle bloquante en échec" if len(tests) else ""),
])

st.markdown("### Les sources")
tab = SOURCES.merge(journal[["source", "fichiers", "lignes"]], on="source", how="left") if len(journal) else SOURCES
tab = tab.rename(columns={"fichiers": "Fichiers", "lignes": "Lignes"}).drop(columns="source")
st.dataframe(tab, hide_index=True, use_container_width=True, column_config={
    "Jeu de données": st.column_config.TextColumn(width="medium"),
    "Producteur": st.column_config.TextColumn(width="small"),
    "Période": st.column_config.TextColumn(width="small"),
    "Usage dans le tableau de bord": st.column_config.TextColumn(width="medium"),
    "Licence": st.column_config.TextColumn(width="small"),
    "Lien": st.column_config.LinkColumn(display_text="ouvrir", width="small"),
    "Lignes": st.column_config.NumberColumn(format="localized"),
    "Fichiers": st.column_config.NumberColumn(format="%d")})
encadre("alerte",
        "<b>Licence BDIFF.</b> Les données de la BDIFF sont réservées à un usage non commercial, doivent être citées "
        "(« BDIFF, MASA-IGN, extraction du 18/11/2026 ») et ne peuvent pas être redistribuées. C'est pourquoi le dossier "
        "<code>data/</code> n'est pas versionné : chaque membre reconstruit la base depuis les fichiers d'origine.")

st.markdown("### Le chemin d'une donnée")
c1, c2, c3, c4 = st.columns(4)
for col, (t, txt) in zip((c1, c2, c3, c4), [
    ("Bronze", "Fichiers d'origine, non modifiés, rangés par source et par date de téléchargement, avec leur empreinte SHA-256."),
    ("Raw", "Chargement ligne à ligne, toutes colonnes en texte. Un journal compte les lignes lues, insérées et rejetées."),
    ("Staging et intermédiaire", "Typage, dédoublonnage, rattachement au référentiel des communes, calculs par jour et par commune."),
    ("Marts", "Tables prêtes à l'analyse lues par ce tableau de bord : feux, danger quotidien, communes, SIS, météo."),
]):
    col.markdown(f'<div class="carte"><div class="n">{t}</div><div class="q">{txt}</div></div>', unsafe_allow_html=True)

st.markdown("### Les règles qualité de la dernière exécution")
if len(tests):
    ecarts = tests[tests.statut != "réussi"].sort_values(["decision", "nb_en_faute"], ascending=[True, False])
    st.caption(f"{fr((tests.statut == 'réussi').sum())} règles réussies sur {fr(len(tests))}. Les écarts ci-dessous sont "
               "connus et documentés : ils déclenchent une alerte ou sont tolérés, aucun n'arrête le chargement.")
    st.dataframe(ecarts.rename(columns={
        "couche": "Couche", "id_regle": "Règle", "dimension": "Dimension", "enonce": "Énoncé", "decision": "Décision",
        "nb_en_faute": "Lignes en écart", "statut": "Résultat"}), hide_index=True, use_container_width=True,
        column_config={"Lignes en écart": st.column_config.NumberColumn(format="localized", width="small"),
                       "Couche": st.column_config.TextColumn(width="small"),
                       "Règle": st.column_config.TextColumn(width="small"),
                       "Décision": st.column_config.TextColumn(width="small"),
                       "Résultat": st.column_config.TextColumn(width="small"),
                       "Énoncé": st.column_config.TextColumn(width="large")})
    with st.expander("Toutes les règles"):
        st.dataframe(tests, hide_index=True, use_container_width=True)

st.markdown("### Ce que ces données ne permettent pas de dire")
encadre("lecture", """
<ul>
<li><b>La saison 2026 des feux.</b> La BDIFF la publiera en 2027 ; les bulletins 2026 sont connus, les feux non.</li>
<li><b>La couverture du seuil dans le Rhône seul.</b> Trop peu de feux y sont recensés (62 en vingt ans) : le seuil est
calibré sur la région Auvergne-Rhône-Alpes, puis appliqué au Rhône.</li>
<li><b>Les causes.</b> Elles sont inconnues pour un feu sur deux dans la BDIFF ; elles ne sont pas exploitées.</li>
<li><b>Les délais d'intervention.</b> Les distances aux casernes sont à vol d'oiseau, sans réseau routier ni effectifs.</li>
</ul>
""", "Limites")
encadre("pourquoi", """
<ul>
<li><b>SDMIS</b> : fichier des interventions « feux de végétation » 2015-2026 (date, commune, surface, moyens engagés).
C'est la donnée qui manque le plus : elle permettrait de calibrer le seuil sur le Rhône et de couvrir 2026.</li>
<li><b>NASA FIRMS</b> : détections satellitaires de points chauds, gratuites après création d'une clé d'accès ; utiles
pour repérer des feux absents de la BDIFF, avec une résolution limitée pour les petits feux.</li>
</ul>
""", "Prochaines données à obtenir")

with st.expander("Définition des indicateurs"):
    st.markdown("""
- **Jours de renfort J(s)** : nombre de jours-départements, sur la période couverte par les bulletins (début juin à
  début octobre), où le bulletin annonce un niveau au moins égal au seuil *s*. Pour le Rhône seul, ce sont des jours.
- **Couverture C(s)** : parmi les feux significatifs (1 ha ou plus par défaut) survenus pendant la période des bulletins,
  part de ceux dont le département était au niveau *s* ou plus ce jour-là.
- **Rendement R(s)** : feux couverts par jour de renfort, soit F(s) / J(s). Il se décompose exactement en
  P(s) × M(s) : part des jours de renfort avec au moins un feu, multipliée par le nombre moyen de feux de ces jours-là.
- **Chaleur sèche (Lyon-Bron)** : jour à 30 °C ou plus, précédé de dix jours avec moins de 1 mm de pluie au total.
  Indicateur de contexte, non utilisé dans le calcul du seuil.
""")
