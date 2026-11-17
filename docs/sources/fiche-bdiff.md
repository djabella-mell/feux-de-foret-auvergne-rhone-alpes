# Fiche source : BDIFF, Base de données sur les incendies de forêt en France

- **Autrice de la fiche :** Melissa DJABELLA
- **Fiche remplie le :** 17/11/2026, avec le fichier ouvert (export CSV de la région Auvergne-Rhône-Alpes, alertes du 01/01/2006 au 31/12/2025, `Incendies.csv`), plus `Mention légales.pdf` lu en entier
- **Trois dates :**
  - réalité décrite : feux dont la première alerte va du 02/02/2006 au 14/12/2025 ;
  - publication : l'année N-1 est diffusée au cours de l'année N, date exacte non affichée ;
  - mise à jour de la fiche : 17/11/2026.

| Catégorie | Rubrique | Valeur |
|---|---|---|
| Identité | Nom | Base de données sur les incendies de forêt en France (BDIFF) |
| | Description | Registre national des incendies de forêt, une fiche par feu, diffusé agrégé à la commune |
| | Identifiant | Numéro de fiche (`Année` + `Numéro`) |
| Provenance et propriété | Propriétaire | Ministère de l'Agriculture et de la Souveraineté alimentaire (éditeur), avec l'IGN (conception et hébergement) |
| | Système producteur | Saisie en ligne par un réseau de contributeurs : SDIS, DDT, ONF… |
| Technique | Format | Zip contenant `Incendies.csv` (séparateur `;`, UTF-8, fins de ligne CRLF), `Mention légales.pdf` et `Définitions.pdf` |
| | Schéma | 24 colonnes, dont : `Année`, `Numéro`, `Département`, `Code INSEE`, `Nom de la commune`, `Date de première alerte`, `Surface parcourue (m2)`, surfaces par type de terrain (forêt, maquis, autres terres boisées, non boisées…), `Précision des surfaces`, `Type de peuplement`, `Nature` (cause), décès et bâtiments, `Précision de la donnée` |
| | Particularité | Les 3 premières lignes sont des métadonnées : avertissement, nombre d'incendies, critères. L'en-tête est en ligne 4. |
| | Clés disponibles | (`Année`, `Numéro`), unique : 0 doublon. Jointure possible par `Code INSEE` et par date. |
| Accès | Mode | Formulaire web, puis « Télécharger : CSV ». Le robots.txt bloque la lecture automatique : pas d'API. |
| | Contrainte constatée | La sélection est gardée en session côté serveur, avec environ 20 s par requête. Les extractions parallèles se mélangent : l'extraction nationale a échoué le 17/11, elle est à refaire requête par requête. |
| Couverture | Grain | **Une ligne = un feu**, localisé à la commune. Pas de coordonnées ni de point d'éclosion. |
| | Emprise | Extraction faite : région 84, soit 4 072 feux répartis dans les 12 départements. La base couvre la France entière, outre-mer compris. |
| | Période réellement couverte | 2006-2025. **2026 n'est pas disponible** : la diffusion s'arrête à l'année précédente. |
| Fraîcheur | Fréquence | Annuelle |
| | Volumétrie | 4 072 lignes, 459 Ko (région, 20 ans) |
| Qualité | Complétude | `Nature` (cause) vide pour 53 % des feux de la région et pour 54 des 62 feux du Rhône. `Précision des surfaces` vide pour 49 %. `Type de peuplement` vide pour 53 %. |
| | Complétude de la population | **Très hétérogène** : le Rhône compte 62 feux en 20 ans, dont 41 en 2015, et aucun feu pendant 11 des 20 années. L'Ardèche en compte 1 608. Le site signale aussi des « campagnes avec un nombre d'incendies inconnu » (par exemple 2025 pour les départements 75, 92, 93, 94 et 972). Probable sous-déclaration dans les départements hors zone méditerranéenne. |
| | Cohérence | Surfaces toutes > 0. 56 noms de commune diffèrent du libellé COG 2026 pour des codes valides (accents, renommages). |
| | Référentiel | 48 feux (25 codes) portent un code commune absent du COG 2026, à cause des fusions de 2019 à 2025. Les 25 codes sont retrouvés par la table des mouvements. |
| Gouvernance | Données personnelles | Aucune dans l'export (localisation à la commune). Le formulaire de saisie a été « rénové » : certaines données relèvent de l'ancienne version (avertissement en ligne 1). |
| | Licence | **Pas une licence ouverte.** L'usage personnel, associatif ou professionnel est autorisé si l'on ne vend rien, si l'on ne modifie pas les données, si l'on cite `bdiff.agriculture.gouv.fr` et si l'on mentionne que les droits de reproduction sont réservés. Aucun usage commercial. |
| | Conséquence | Les données brutes ne sont pas déposées dans le dépôt public |
| Lineage | Transformations | Aucune |
| Besoin | Questions servies | Q1 (où), Q2 (seuil, période commune 2024-2025), Q3 (profil des feux à niveau bas), Q4 (comparaison) |

**À vérifier :** `Définitions.pdf` (définitions de forêt et des catégories de surface) n'a pas encore été relu. Les définitions ne sont donc pas reprises dans le glossaire.
