# Fiche source : Archives de la Météo des forêts

- **Auteur de la fiche :** Rayan IOUSSAIDENE (responsable sources)
- **Fiche remplie le :** 17/11/2026, avec les trois fichiers ouverts (`mdf_2024.csv.gz`, `mdf_2025.csv.gz`, `mdf_2026.csv.gz`)
- **Trois dates à ne pas confondre :**
  - réalité décrite : saisons 2024, 2025 et 2026 (jours cibles du 04/06/2024 au 06/10/2026) ;
  - publication : catalogue « mis à jour le 5 octobre 2026 » ;
  - mise à jour de la fiche : 17/11/2026.

| Catégorie | Rubrique | Valeur |
|---|---|---|
| Identité | Nom | Archives de la Météo des forêts MdF |
| | Description | Niveau de danger « feux de forêt » par département, publié chaque jour pendant la saison pour J+1 et J+2 |
| | Identifiant | data.gouv.fr `692f01d38fef6c5815d9262a` |
| | Domaine métier | Prévention, danger météorologique d'incendie |
| Provenance et propriété | Producteur / propriétaire | Météo-France |
| | Système producteur | Chaîne de production de la Météo des forêts. Les détails de calcul (IFM, état de la végétation, expertise) sont **non vérifiés** : la documentation PDF du jeu de données n'a pas été ouverte. |
| Technique | Format | CSV compressé gzip, un fichier par année |
| | Schéma | 2024 : `date,num_dep,niveau_j1,niveau_j2,nom_dep`, séparateur `,`. 2025 : même schéma, mais la colonne s'appelle `dep_nom`. 2026 : séparateur `;` et `num_dep` complété à 2 caractères (`01`). |
| | Localisation | Ressources data.gouv.fr, servies depuis `meteofrance.s3.sbg.io.cloud.ovh.net/data/BULLETIN/MDF/mdf_AAAA.csv.gz` |
| | Clés disponibles | (`num_dep`, `date`), unique dans chaque fichier : aucun doublon constaté |
| Accès | Mode | Téléchargement de fichier publié (batch). Une API Météo des forêts existe aussi (non testée). |
| Couverture | Grain | **Une ligne = un département × un bulletin émis** (date d'émission), avec deux niveaux : J+1 et J+2 |
| | Emprise | France métropolitaine, 96 départements (dont 2A et 2B). Pas d'outre-mer. |
| | Période réellement couverte | Émissions du 03/06 au 30/09 en 2024 et 2025 (120 bulletins), du 28/05 au 05/10 en 2026 (131 bulletins). **Rien hors saison.** |
| Fraîcheur | Mise à jour affichée | 5 octobre 2026 (fichier 2026) |
| | Fréquence | Quotidienne pendant la saison. Le catalogue signale « fréquence de mise à jour non respectée », ce qui est cohérent avec l'arrêt du bulletin hors saison. |
| | Volumétrie | 11 520 lignes (2024), 11 520 (2025), 12 576 (2026), soit 35 616 lignes et environ 1,5 Mo décompressé |
| | Heure d'émission | 16:00Z (18 h, heure de Paris) en 2024 ; 14:50Z (16 h 50) en 2025 et 2026 |
| Qualité | Complétude | 96 départements chaque jour, aucune valeur manquante pour J+1 ni pour J+2 |
| | Cohérence | Niveaux compris entre 1 et 4. J+1 et J+2 donnent le même niveau pour le même jour cible dans 93,3 % des cas (France, 2024-2026). |
| | Pièges relevés | Schéma différent selon les années ; code département `1` contre `01` ; lignes non triées en 2024 ; **`date` est la date d'émission, pas le jour cible** |
| Gouvernance | Données personnelles | Aucune |
| | Licence | Licence Ouverte / Open Licence 2.0 (Etalab) : réutilisation libre avec mention de la source |
| | Référentiel géographique | Codes départements Insee, sans millésime indiqué. Le code 69 couvre le Rhône et la Métropole de Lyon (D-09). |
| Lineage | Amont | Production Météo-France (non documentée ici) |
| | Transformations | Aucune à ce stade. Pour le profil : concaténation des trois fichiers et harmonisation du schéma (`src/README.md`) |
| Besoin | Questions servies | Q2 (seuil), Q3 (feux à niveau bas), Q4 (comparaison régionale et nationale) |

**Limites pour la commande**

- Trois saisons seulement : on ne peut pas estimer la stabilité d'un seuil sur dix ans.
- Pas de bulletin hors juin-septembre. Or, de 2006 à 2025, 49,6 % des feux de la région et 40,9 % de la surface brûlée se situent hors de cette période (profil BDIFF).
- Le niveau est départemental : il ne permet pas de cibler un secteur dans le Rhône.
