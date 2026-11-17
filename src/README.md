# Scripts

| Script | Rôle | Entrées (`data/raw/`) | Sortie |
|---|---|---|---|
| `profil_qualite.py` | Profil de qualité par colonne et contrôles de validité et de cohérence | `mdf_france_2024_2026.csv`, `bdiff_ara_2006_2025.csv`, `v_commune_2026.csv`, `v_mvt_commune_2026.csv` | `docs/sources/profils-qualite-generes.md` |

Lancement : `python src/profil_qualite.py`. Il faut pandas et tabulate.

## Récupérer les fichiers bruts (extractions du 17/11/2026)

**Météo des forêts** (Licence Ouverte 2.0)
1. data.gouv.fr › « Archives de la Météo des forêts MdF » : télécharger `mdf_2024.csv.gz`, `mdf_2025.csv.gz` et `mdf_2026.csv.gz`.
2. Concaténer les trois fichiers dans `mdf_france_2024_2026.csv` :
   - ajouter une colonne `annee_fichier` ;
   - remplacer le séparateur `;` du fichier 2026 par `,` ;
   - utiliser l'en-tête `annee_fichier,date,num_dep,niveau_j1,niveau_j2,nom_dep`.

**BDIFF** (conditions du site, pas de licence ouverte, voir D-06)
1. bdiff.agriculture.gouv.fr › Accéder aux données.
2. Choisir les dates du 01/01/2006 00:00 au 31/12/2025 23:59 et la région AUVERGNE-RHÔNE-ALPES, puis Filtrer.
3. Cliquer sur « Télécharger : CSV ».
4. Renommer `Incendies.csv` en `bdiff_ara_2006_2025.csv`. La ligne 2 doit annoncer 4072 incendies.

**COG 2026** (Insee)
- Télécharger depuis insee.fr/fr/information/8740222 : `v_commune_2026.csv`, `v_mvt_commune_2026.csv`, `v_departement_2026.csv`, `v_ctcd_2026.csv`.
