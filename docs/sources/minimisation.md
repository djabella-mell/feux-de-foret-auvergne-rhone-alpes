# Tableau de minimisation (17/11/2026)

Responsable : Lynda LAZRI. Principe (RGPD art. 5.1.c) : on ne garde un champ que s'il sert une question. Les questions Q1 à Q4 sont celles de la [matrice](matrice.md).

**Légende :** ✅ gardé · ❌ écarté · 🔶 gardé sous condition.

## BDIFF

| Champ | Gardé ? | Question servie | Justification / traitement |
|---|---|---|---|
| Année, Numéro | ✅ | toutes | Identifiant du feu, sans donnée personnelle |
| Département, Code INSEE | ✅ | Q1, Q4 | Localisation à la commune : grain le plus fin disponible et suffisant |
| Nom de la commune | ❌ | — | Redondant avec le code ; le libellé du COG fait foi |
| Date de première alerte | ✅ | Q2, Q3 | Rattachement au niveau du jour, mois, heure |
| Surface parcourue | ✅ | Q1, Q2 | Gravité, feu significatif |
| Surface forêt | ✅ | Q1, Q4 | Part forestière du feu |
| Autres surfaces ventilées (9 colonnes) | ❌ | — | Aucune question ne les utilise ; ventilation incohérente pour 4 % des feux |
| Précision des surfaces | ✅ | qualité | Indicateur de fiabilité de la surface |
| Type de peuplement | 🔶 | Q3 | Gardé si Q3 l'exploite ; vide à 53 % |
| Nature (cause) | 🔶 | Q3 | Jamais diffusée à la commune si moins de 3 feux (risque de ré-identification, voir [`rgpd.md`](../rgpd.md)) |
| Décès, bâtiments détruits (4 colonnes) | ❌ | — | Ne sert ni le lieu ni le seuil ; information sensible sur des personnes |
| Précision de la donnée | ✅ | qualité | Signale les fiches partielles |

## Météo des forêts

| Champ | Gardé ? | Question servie | Justification |
|---|---|---|---|
| date (émission), num_dep, niveau_j1, niveau_j2 | ✅ | Q2, Q4 | Cœur de la question du seuil |
| nom_dep | ❌ | — | Redondant avec le code ; le libellé du COG fait foi |

## COG 2026

| Champ | Gardé ? | Question servie | Justification |
|---|---|---|---|
| COM, DEP, REG, CTCD, LIBELLE | ✅ | Q1, Q4 | Jointure, appartenance 69D / 69M, affichage |
| TYPECOM, TNCC, NCC, NCCENR, ARR, CAN, COMPARENT | ❌ | — | Aucune question ne les utilise |
| Mouvements : COM_AV, COM_AP, DATE_EFF, MOD | ✅ | jointure | Rattacher les codes de communes disparues |

## Interventions SDMIS (champs demandés)

| Champ | Demandé ? | Question servie | Justification |
|---|---|---|---|
| Identifiant d'intervention **pseudonymisé** | ✅ | toutes | Dédoublonnage, sans possibilité de remonter au dossier |
| Date et heure d'alerte, code INSEE de la commune | ✅ | Q1, Q2, Q3 | Lieu et moment, au grain de la commune |
| Nature de l'intervention, surface | ✅ | Q1, Q3 | Type de feu, gravité |
| Nombre d'engins, durée | ✅ | Q1 | Mesure de l'engagement de moyens |
| Adresse, coordonnées GPS | ❌ | — | La commune suffit ; une adresse identifie un foyer |
| Requérant (nom, téléphone) | ❌ | — | Aucune question ne l'utilise |
| Agents engagés, victimes | ❌ | — | Données personnelles, et de santé pour les victimes (art. 9) |
