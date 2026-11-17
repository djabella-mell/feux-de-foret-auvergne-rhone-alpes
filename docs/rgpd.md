# Données personnelles et conformité (v1, 17/11/2026)

Responsable : Lynda LAZRI (qualité et conformité). Document lié aux compétences C4 et C8 de la séance S2.

## 1. Inventaire des données personnelles par source

| Source | Données personnelles ? | Détail | Traitement retenu |
|---|---|---|---|
| Météo des forêts | Non | Niveaux par département | — |
| BDIFF (export public) | **Non directement**, risque **indirect** | Feu localisé à la commune, date et heure, cause (`Involontaire (particulier)`, `Malveillance`…), nombre de décès et de bâtiments touchés | Voir §3 : risque de ré-identification dans les petites communes |
| COG | Non | Référentiel administratif | — |
| BD Forêt | Non | Polygones de végétation | — |
| Interventions SDMIS (attendues) | **Oui, probablement** | Adresse d'intervention, identité et numéro du requérant, agents engagés, victimes éventuelles | Minimisation **dès la demande** (§4) |
| Dépôt Git | Oui (limité) | Noms et adresses e-mail des membres dans les commits | Usage pédagogique, aucune action |

## 2. Rôles et base légale (cadre fictif du projet)

- **Responsable de traitement :** le SDMIS 69, qui définit la finalité, c'est-à-dire préparer le dispositif feux de forêt 2027.
- **Sous-traitant :** le groupe projet, qui traite les données pour le compte du SDMIS et selon ses instructions.
- **Base légale côté SDMIS :** mission d'intérêt public (article 6.1.e du RGPD), prévention et lutte contre l'incendie.
- **Catégories particulières (article 9) :** aucune n'est utile. Les données de santé des victimes, si elles figurent dans l'extraction SDMIS, **ne doivent pas nous être transmises**.

## 3. Principes de l'article 5 appliqués au projet

| Principe | Application concrète |
|---|---|
| Limitation des finalités | Les données servent uniquement à arbitrer l'emplacement et le seuil du dispositif renforcé. Pas de recherche de responsables, pas d'analyse individuelle des causes. |
| Minimisation | On ne demande que les champs liés à une question (Q1 à Q4). Le détail champ par champ est dans le [tableau de minimisation](sources/minimisation.md). |
| Exactitude | Rattachement des communes au COG 2026 avec table de passage (D-07). Le niveau de danger est pris tel qu'il était publié la veille (vérité à date). |
| Limitation de la conservation | Fichiers bruts SDMIS conservés jusqu'à la soutenance (11/12/2026), puis supprimés. Jamais versionnés. |
| Intégrité et confidentialité | `data/raw/` est exclu de Git (D-06). Les fichiers SDMIS restent sur les postes du groupe, jamais sur un dépôt public ni dans un outil en ligne. |
| Responsabilité | Ce document, le journal des décisions et l'historique Git tracent les choix. |

**Risque de ré-identification dans la BDIFF :** dans une commune de quelques centaines d'habitants, la combinaison « date + commune + cause `Involontaire (particulier)` » peut désigner une personne connue localement. **Règle de diffusion :** dans les livrables (tableau de bord, rapport), la cause n'est jamais affichée à la commune quand l'effectif est inférieur à 3. On agrège alors au département ou à la saison.

## 4. Pseudonymisation et anonymisation

- **Anonymisation** (irréversible) : c'est l'objectif pour tout ce qui est publié. On agrège à la commune, au jour, voire au mois.
- **Pseudonymisation** (réversible avec une clé) : si le SDMIS ne peut pas agréger, on lui demande de remplacer le numéro d'intervention par un identifiant haché avec une clé qu'il garde. Les données pseudonymisées restent des données personnelles.

### Demande d'extraction au SDMIS (modèle)

> Objet : extraction des interventions « feux de végétation » 2015-2026, projet saison feux 2027
>
> Pour répondre à votre commande, nous avons besoin, pour chaque intervention de nature « feu de végétation » (feux de forêt, broussailles, récoltes, chaumes) entre le 01/01/2015 et le 31/12/2026, des champs suivants : identifiant pseudonymisé, date et heure de l'alerte, code INSEE de la commune, nature de l'intervention, surface parcourue si connue, nombre d'engins engagés, durée d'intervention.
> Nous ne souhaitons **ni adresse, ni coordonnées précises, ni information sur le requérant, les victimes ou les agents**. Les fichiers seront conservés sur les postes du groupe jusqu'au 11/12/2026, puis supprimés.
> Nous souhaitons également connaître : le seuil actuel de déclenchement du dispositif renforcé, sa composition, et son coût par jour et par secteur.

## 5. Points à valider

- Qui, au SDMIS, valide la transmission (délégué à la protection des données du SDMIS) ?
- Le groupe a-t-il le droit d'utiliser les données BDIFF dans un livrable public de soutenance ? Les conditions permettent l'usage professionnel non commercial avec citation : **oui a priori**, sans modifier les données sources.
