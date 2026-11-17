# Inventaire des sources (17/11/2026)

Responsable : Rayan IOUSSAIDENE. Une ligne par source examinée, y compris celles écartées ou inaccessibles.

| Source | Fiche | Auteur·rice | Producteur | Grain | Période | Accès | Licence | Statut |
|---|---|---|---|---|---|---|---|---|
| Archives Météo des forêts | [fiche](fiche-meteo-des-forets.md) | Rayan | Météo-France | département × bulletin (J+1, J+2) | 2024-2026, saison seulement | fichier csv.gz | Licence Ouverte 2.0 | **Retenue**, extraite |
| BDIFF | [fiche](fiche-bdiff.md) | Melissa | MASA / IGN | feu × commune | 2006-2025 | formulaire web + CSV | conditions BDIFF (non ouverte) | **Retenue**, extraite (région 84) |
| COG 2026 | [fiche](fiche-cog-insee.md) | Lynda | Insee | commune | au 01/01/2026 + mouvements | fichier CSV | non vérifiée | **Retenue**, extraite (région 84) |
| BD Forêt V2 | [fiche](fiche-bd-foret-v2.md) | Yakoub | IGN | polygone ≥ 0,5 ha | 2007-2018 | téléchargement par département | Etalab 2.0 (à confirmer) | **Retenue**, non extraite |
| Interventions SDMIS | [fiche](fiche-interventions-sdmis.md) | Rayan | SDMIS 69 | intervention | 2015-2026 attendu | demande à la direction | données internes | **Manquante**, demandée (D-05) |
| API Météo des forêts | — | — | Météo-France | département × jour | temps réel | API | non vérifiée | Écartée pour l'historique (pas d'archive), à garder pour l'exploitation |
| Indice IFM/FWI horaire (data.gouv.fr) | — | — | collaboration hackathon | maille × heure | — | — | — | **Écartée** : le catalogue indique « jeu de données pas actif, aucune garantie sur la qualité » |
| Presse locale (feux 2026 du Rhône) | — | Rayan | médias | feu | 2026 | articles | droit d'auteur (faits seulement) | **Proxy** temporaire, confiance faible (D-04) |

## Sources envisagées, non examinées à ce stade

- **Météo quotidienne et indice de sécheresse** (SAFRAN / SIM, stations Météo-France) : nécessaires pour Q3 (feux les jours de niveau bas) et pour recalculer un indice hors saison.
- **RPG** (registre parcellaire graphique) : cultures et moissons, pour les feux agricoles de l'été.
- **Casernes du SDMIS** (data.grandlyon.com) : distance d'intervention, pour Q1.

## Constats transversaux

1. **Aucune source ne couvre à la fois l'indice et les feux sur une longue période.** Le recouvrement se limite à 2024-2025, soit deux saisons.
2. **La saison du bulletin ne couvre pas la saison des feux.** De 2006 à 2025, 49,6 % des feux régionaux et 40,9 % de la surface brûlée se situent hors juin-septembre.
3. **Le Rhône est presque absent de la BDIFF** (62 feux en 20 ans). Les données du SDMIS sont indispensables pour une règle propre au 69.
