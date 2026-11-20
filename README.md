# Feux de forêt – Auvergne-Rhône-Alpes

Projet MD5 · UE01.A Modélisation et pipelines de données · HETIC 2026-2027

**Région :** Auvergne-Rhône-Alpes
**Commanditaire :** direction du SDMIS 69 (Rhône et Métropole de Lyon). Commande « Saison feux 2027 », réponse attendue le 11 décembre 2026.

## Rôles

| Rôle | Responsable de | Membre |
|---|---|---|
| Cheffe de projet | Dépôt, tickets, checkpoints, journal des décisions | Melissa DJABELLA |
| Responsable sources | Inventaire, fiches d'identité, matrice questions × sources | Rayan IOUSSAIDENE |
| Responsable qualité et conformité | Règles de qualité, tests, données personnelles | Lynda LAZRI |
| Responsable pipeline et modèle | Chargement, consolidation, entrepôt | Yakoub KEBAILI |

## Contenu

- `docs/analyse/` : analyses individuelles de la commande
- `docs/glossaire.md` : glossaire du projet
- `docs/sources/` : dossier de sources v1 (fiches d'identité, inventaire, matrice questions × sources, profils de qualité, tableau de minimisation, décision face au manque)
- `docs/modele/` : modèle de données cible et entrepôt (couches bronze, silver et marts, consolidation multi-sources), règles de qualité et résultats
- `pipeline/` : script qui construit l'entrepôt à partir des silos (`python pipeline/construire_entrepot.py`)
  puis `python pipeline/sources_longues.py` : indice forêt météo reconstitué depuis 1958 (SAFRAN) et détections satellitaires FIRMS
- `kpi/` : atelier 1 du groupe G12, KPI du seuil de déclenchement (notebook, note PDF, résultats)
- `dashboard/` : tableau de bord Streamlit « Saison feux 2027 » (cinq pages, lues depuis `data/marts/`)
- `data/` (hors Git) : silos des sources d'origine (`data/bronze/`), base DuckDB qui les regroupe (`data/entrepot/feux_de_foret.duckdb`) et tables d'analyse exportées en Parquet (`data/marts/`)

## Lancer le tableau de bord

```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/Accueil.py
```

Le tableau de bord lit les fichiers de `data/marts/`. Pour les régénérer depuis les silos : `pip install -r pipeline/requirements.txt` puis `python pipeline/construire_entrepot.py` (4 à 5 minutes).

| Page | Question | Graphiques |
|---|---|---|
| Accueil | Quel seuil, à quel coût ? | couverture et jours mobilisés par seuil |
| 1 · Le seuil | Que gagne-t-on à passer du seuil 3 au seuil 2 ? | barres groupées, haltères sur six variantes, rapport de rendement |
| 2 · Le coût dépend de l'été | 2026 est-il une exception ? | calendrier des niveaux 2024-2026, chaleur sèche à Lyon-Bron depuis 1991 |
| 3 · L'angle mort de la BDIFF | La base nationale suffit-elle pour le Rhône ? | interventions SDMIS et feux BDIFF par an, comparaison des départements |
| 4 · Où renforcer | Quelles communes prépositionner ? | carte du boisement et des casernes, règle de repérage réglable |
| 5 · Sources et méthode | D'où viennent les chiffres ? | sources, licences, règles qualité de la dernière exécution |

## Sources

BDIFF (MASA-IGN, usage non commercial, citation obligatoire, pas de redistribution) · Météo des forêts et données climatologiques quotidiennes (Météo-France) · Statistiques des services d'incendie et de secours (DGSCGC) · BD Forêt V2 et ADMIN EXPRESS COG (IGN) · COG 2026 (Insee) · GASPAR (Géorisques) · Casernes du SDMIS (data.grandlyon.com) · chiffres 2026 relayés par la presse locale (contexte, confiance faible).
