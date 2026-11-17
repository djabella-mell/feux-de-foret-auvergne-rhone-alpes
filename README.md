# Feux de forêt – Auvergne-Rhône-Alpes

Projet MD5 · UE01 Stratégie business data-driven · UE01.A Modélisation et pipelines de données (HETIC 2026-2027).

**Commanditaire :** direction du SDMIS 69 (Service départemental-métropolitain d'incendie et de secours du Rhône et de la Métropole de Lyon). Le sujet écrit « SMDIS 69 ».
**Commande :** saison feux 2027. Où concentrer les moyens, et à partir de quel niveau de la Météo des forêts déclencher le dispositif renforcé. Situer le Rhône dans la région et en France. Réponse attendue le **11 décembre 2026**.
**Région :** Auvergne-Rhône-Alpes (code région 84, 12 départements : 01, 03, 07, 15, 26, 38, 42, 43, 63, 69, 73, 74).

## Rôles

Proposition du 17/11/2026, à valider en groupe. Toute modification sera consignée dans [`docs/decisions.md`](docs/decisions.md).

| Rôle | Responsable de | Membre |
|---|---|---|
| Cheffe de projet | Dépôt, tickets, checkpoints, journal des décisions | Melissa DJABELLA |
| Responsable sources | Inventaire, fiches d'identité, matrice questions × sources | Rayan IOUSSAIDENE |
| Responsable qualité et conformité | Règles de qualité, tests, données personnelles | Lynda LAZRI |
| Responsable pipeline et modèle | Chargement, consolidation, entrepôt | Yakoub KEBAILI |

## Organisation du dépôt

```
docs/
  analyse/          analyses individuelles de la commande (une par personne)
  sources/          dossier de sources v1 (fiches, inventaire, matrice, profils, minimisation, manques)
  glossaire.md      définitions communes du projet
  decisions.md      journal des décisions
  rgpd.md           données personnelles et conformité
src/                scripts (profil de qualité)
data/raw/           données brutes (NON versionnées, voir .gitignore et D-06)
```

## Reproduire les profils de qualité

1. Déposer les fichiers bruts dans `data/raw/` (procédure dans [`src/README.md`](src/README.md)).
2. `python src/profil_qualite.py` : régénère les profils de qualité du dossier de sources.

Dépendances : Python ≥ 3.10, pandas, tabulate.

## Calendrier

| Date | Livrable |
|---|---|
| Lun. 16/11 | Analyses de la commande, fiches de sources et inventaire, glossaire v0, matrice v0 |
| Mar. 17/11 (fin FOAD 1) | Dossier de sources v1 : fiches, matrice, profils de qualité, minimisation, décision face au manque |
| vers le 04/12 (à confirmer) | Pipeline v0.1 : couches raw, staging, consolidée |
| Mer. 09/12 (fin FOAD 2) | Étoile historisée : faits, dimensions, quatre tests, trois requêtes décisionnelles |
| à fixer | Rendu final |
