"""Briques communes du tableau de bord : données, style, filtres, calcul des KPIs, graphiques."""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

MARTS = Path(os.environ.get("FEUX_MARTS", Path(__file__).resolve().parents[1] / "data" / "marts"))

# --- palette (validée sur le fond sombre #0a0a0b : contraste, daltonisme) -------------
FOND = "#0a0a0b"
CARTE = "#141416"
TEXTE = "#f0efec"
TEXTE_2 = "#c3c2b7"
MUET = "#898781"
GRILLE = "#26262a"
ACCENT = "#22d3ee"          # interface uniquement (surtitres, filets), jamais une série
SERIE_1 = "#3987e5"         # bleu
SERIE_2 = "#d95926"         # orange
GRIS = "#55555b"            # mise en retrait
# échelle officielle de la Météo des forêts (sémantique, toujours avec sa légende)
NIVEAUX = {1: ("Faible", "#3f9b45"), 2: ("Modéré", "#f2c919"), 3: ("Élevé", "#ef7d18"), 4: ("Très élevé", "#d62b2b")}

PERIMETRES = {"Auvergne-Rhône-Alpes": "region", "France métropolitaine": "france", "Rhône (69) seul": "rhone"}
TAILLES = {"Feux de plus d'1 ha": 1.0, "Feux de plus de 5 ha": 5.0, "Tous les feux": 0.0}
ECHEANCES = {"J+1 (bulletin de la veille)": "niveau_j1", "J+2 (bulletin de l'avant-veille)": "niveau_j2"}


# --- format français ----------------------------------------------------------------------
def fr(v, dec: int = 0, suffixe: str = "") -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    s = f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")
    return s + suffixe


def pct(v, dec: int = 0) -> str:
    return fr(100 * v, dec, " %")


# --- données ------------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def donnees() -> dict[str, pd.DataFrame]:
    if not MARTS.exists():
        st.error(f"Données introuvables : {MARTS}. Lancez d'abord `python pipeline/construire_entrepot.py`.")
        st.stop()
    return {p.stem: pd.read_parquet(p) for p in MARTS.glob("*.parquet")}


def departements_du_perimetre(d, perimetre: str) -> set[str]:
    dj = d["fct_danger_jour"]
    if perimetre == "rhone":
        return {"69"}
    if perimetre == "region":
        return set(dj.loc[dj.code_region == "84", "code_departement"])
    return set(dj.code_departement)


# --- KPIs du seuil ------------------------------------------------------------------------
def indicateurs(d, deps: set[str], annees: list[int], niveau: str = "niveau_j1", seuil_ha: float = 1.0,
                mesure: str = "nombre") -> pd.DataFrame:
    """Pour chaque seuil s : jours de renforcement J(s), feux couverts F(s), couverture C(s),
    rendement R(s) = F(s) / J(s), précision P(s) = jours actifs / J(s). R(s) = P(s) × M(s), exacte."""
    dj = d["fct_danger_jour"]
    dj = dj[dj.code_departement.isin(deps) & dj.annee.isin(annees) & dj[niveau].notna()]
    f = d["fct_feux"]
    f = f[f.code_departement.isin(deps) & f.annee.isin(annees) & (f.surface_ha >= seuil_ha)]
    f = f.merge(dj[["code_departement", "jour", niveau]].rename(columns={niveau: "niv"}),
                left_on=["code_departement", "date_alerte"], right_on=["code_departement", "jour"], how="left")
    poids = f.surface_ha if mesure == "surface" else pd.Series(1.0, index=f.index)
    actifs = set(zip(f.code_departement, pd.to_datetime(f.date_alerte)))
    total_jours = len(dj)
    lignes = []
    for s in (1, 2, 3, 4):
        jr = dj[dj[niveau] >= s]
        J = len(jr)
        Jact = sum((c, pd.Timestamp(j)) in actifs for c, j in zip(jr.code_departement, jr.jour))
        F = poids[f.niv >= s].sum()
        Fs = poids[f.niv.notna()].sum()
        lignes.append({"seuil": s, "jours": J, "part_jours": J / total_jours if total_jours else np.nan,
                       "jours_actifs": Jact, "feux_couverts": F, "feux_saison": Fs,
                       "feux_hors_saison": poids[f.niv.isna()].sum(),
                       "couverture": F / Fs if Fs else np.nan, "rendement": F / J if J else np.nan,
                       "precision": Jact / J if J else np.nan})
    return pd.DataFrame(lignes).set_index("seuil")


def variantes(d) -> pd.DataFrame:
    """Test de sensibilité : la conclusion tient-elle si l'on change un choix raisonnable ?"""
    ara = departements_du_perimetre(d, "region")
    cas = {
        "Référence (région, J+1, ≥ 1 ha, nombre)": indicateurs(d, ara, [2024, 2025]),
        "France métropolitaine": indicateurs(d, departements_du_perimetre(d, "france"), [2024, 2025]),
        "Bulletin de l'avant-veille (J+2)": indicateurs(d, ara, [2024, 2025], niveau="niveau_j2"),
        "Tous les feux": indicateurs(d, ara, [2024, 2025], seuil_ha=0),
        "Surface brûlée au lieu du nombre": indicateurs(d, ara, [2024, 2025], mesure="surface"),
        "Saison 2025 seule": indicateurs(d, ara, [2025]),
    }
    return pd.DataFrame({k: {"C2": v.loc[2, "couverture"], "C3": v.loc[3, "couverture"],
                             "R3_R2": v.loc[3, "rendement"] / v.loc[2, "rendement"],
                             "J2_J3": v.loc[2, "jours"] / v.loc[3, "jours"]} for k, v in cas.items()}).T


# --- style --------------------------------------------------------------------------------
CSS = f"""
<style>
.block-container {{ padding-top: 3.6rem; max-width: 1180px; }}
.surtitre {{ color: {ACCENT}; font-weight: 700; letter-spacing: .14em; font-size: .82rem; text-transform: uppercase; margin-bottom: .6rem; }}
.titre {{ font-size: 2.65rem; line-height: 1.12; font-weight: 800; color: {TEXTE}; margin: 0 0 1.2rem 0; }}
.chapo {{ background: {CARTE}; border-left: 3px solid {ACCENT}; border-radius: 8px; padding: 1.05rem 1.3rem;
          color: {TEXTE_2}; font-size: 1.06rem; line-height: 1.6; margin-bottom: 1.6rem; }}
.chapo b {{ color: {TEXTE}; }}
.kpi {{ padding: .2rem 0 .6rem 0; }}
.kpi .lib {{ color: {TEXTE_2}; font-size: .92rem; }}
.kpi .val {{ color: {TEXTE}; font-size: 2.5rem; font-weight: 700; line-height: 1.15; }}
.kpi .sous {{ color: {MUET}; font-size: .88rem; }}
.pourquoi {{ background: {CARTE}; border-radius: 8px; padding: 1rem 1.2rem; color: {TEXTE_2}; font-size: .97rem;
             line-height: 1.55; margin: .6rem 0 1.6rem 0; }}
.pourquoi b, .alerte b {{ color: {TEXTE}; }}
.pourquoi .t, .alerte .t {{ color: {TEXTE}; font-weight: 700; margin-bottom: .3rem; }}
.pourquoi ul, .lecture ul {{ margin: .2rem 0 0 0; padding-left: 1.2rem; }}
.lecture {{ border: 1px solid {GRILLE}; border-radius: 8px; padding: .9rem 1.1rem; color: {TEXTE_2}; font-size: .95rem;
            line-height: 1.55; margin: .2rem 0 1.4rem 0; }}
.lecture .t {{ color: {TEXTE}; font-weight: 700; margin-bottom: .3rem; }}
.carte {{ background: {CARTE}; border-radius: 8px; padding: 1rem 1.1rem; min-height: 9.5rem; border-top: 2px solid {GRILLE}; }}
.carte .n {{ color: {ACCENT}; font-weight: 700; font-size: .95rem; margin-bottom: .35rem; }}
.carte .q {{ color: {TEXTE_2}; font-size: .92rem; line-height: 1.45; }}
.alerte {{ border-left: 3px solid {NIVEAUX[3][1]}; background: {CARTE}; border-radius: 8px; padding: .9rem 1.1rem;
           color: {TEXTE_2}; font-size: .95rem; line-height: 1.55; margin: .4rem 0 1.2rem 0; }}
.titre-graph {{ color: {TEXTE}; font-weight: 700; font-size: 1.02rem; line-height: 1.35; margin: .4rem 0 -.2rem 0; }}
h3 {{ font-size: 1.22rem !important; margin-top: 1.4rem !important; }}
</style>
"""


def page(titre_onglet: str) -> None:
    st.set_page_config(page_title=titre_onglet, page_icon="🔥", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)


def entete(surtitre: str, titre: str, chapo: str) -> None:
    st.markdown(f'<div class="surtitre">{surtitre}</div><div class="titre">{titre}</div>'
                f'<div class="chapo">{chapo}</div>', unsafe_allow_html=True)


def kpis(items: list[tuple[str, str, str]]) -> None:
    for col, (lib, val, sous) in zip(st.columns(len(items)), items):
        col.markdown(f'<div class="kpi"><div class="lib">{lib}</div><div class="val">{val}</div>'
                     f'<div class="sous">{sous}</div></div>', unsafe_allow_html=True)


def encadre(classe: str, html: str, titre: str | None = None) -> None:
    t = f'<div class="t">{titre}</div>' if titre else ""
    st.markdown(f'<div class="{classe}">{t}{html}</div>', unsafe_allow_html=True)


def mise_en_forme(fig: go.Figure, titre: str, hauteur: int = 420, **axes) -> go.Figure:
    """Le titre est rendu en HTML au-dessus du graphique (il passe à la ligne tout seul) ; Plotly n'en affiche pas."""
    legende = axes.get("showlegend", True) and sum(t.showlegend is not False for t in fig.data) >= 2
    fig.update_layout(
        meta=dict(titre=titre),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=hauteur,
        font=dict(color=TEXTE_2, size=13), margin=dict(l=10, r=20, t=36 if legende else 12, b=10),
        legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0, font=dict(color=TEXTE_2)),
        hoverlabel=dict(bgcolor=CARTE, font_color=TEXTE, bordercolor=GRILLE), separators=", ")
    fig.update_xaxes(gridcolor=GRILLE, linecolor=GRILLE, zeroline=False, tickfont=dict(color=MUET))
    fig.update_yaxes(gridcolor=GRILLE, linecolor=GRILLE, zeroline=False, tickfont=dict(color=MUET))
    if axes:
        fig.update_layout(**axes)
    return fig


def graphique(fig: go.Figure) -> None:
    titre = (fig.layout.meta or {}).get("titre") if isinstance(fig.layout.meta, dict) else None
    if titre:
        st.markdown(f'<div class="titre-graph">{titre}</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "locale": "fr"})


# --- barre latérale -------------------------------------------------------------------------
def filtres(avec_calibrage: bool = True) -> dict:
    sb = st.sidebar
    choix = {}
    if avec_calibrage:
        sb.markdown("### Filtres")
        choix["perimetre"] = PERIMETRES[sb.selectbox("Territoire de calibrage", list(PERIMETRES), index=0,
                                                       help="Le Rhône seul compte trop peu de feux pour conclure.")]
        choix["seuil_ha"] = TAILLES[sb.selectbox("Feu significatif", list(TAILLES), index=0)]
        choix["niveau"] = ECHEANCES[sb.radio("Échéance du bulletin", list(ECHEANCES), index=0)]
        choix["annees"] = sb.multiselect("Saisons (feux et bulletins connus)", [2024, 2025], default=[2024, 2025]) or [2024, 2025]
    if avec_calibrage:
        sb.markdown("---")
    sb.caption("**Sources** : BDIFF (MASA-IGN, extraction du 18/11/2026, non commerciale, droits réservés) · "
               "Météo des forêts et données quotidiennes (Météo-France, Licence Ouverte) · Statistiques des SIS "
               "(DGSCGC) · COG 2026 (Insee) · BD Forêt V2, ADMIN EXPRESS (IGN) · GASPAR (Géorisques) · "
               "Casernes SDMIS (Grand Lyon). Détail page « Sources et méthode ».")
    sb.caption("Non exploités : les causes des feux (inconnues pour un feu sur deux) et la saison 2026 des feux, "
               "que la BDIFF ne publiera qu'en 2027.")
    return choix
