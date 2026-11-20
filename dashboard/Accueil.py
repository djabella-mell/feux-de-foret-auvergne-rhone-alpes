"""Tableau de bord « Saison feux 2027 · SDMIS 69 ». Lancement : streamlit run dashboard/Accueil.py"""
import streamlit as st

st.navigation([
    st.Page("vues/accueil.py", title="Accueil", default=True),
    st.Page("vues/seuil.py", title="1 · Le seuil", url_path="seuil"),
    st.Page("vues/cout_ete.py", title="2 · Le coût dépend de l'été", url_path="cout-ete"),
    st.Page("vues/angle_mort_bdiff.py", title="3 · L'angle mort de la BDIFF", url_path="angle-mort-bdiff"),
    st.Page("vues/ou_renforcer.py", title="4 · Où renforcer", url_path="ou-renforcer"),
    st.Page("vues/sources_methode.py", title="5 · Sources et méthode", url_path="sources-methode"),
]).run()
