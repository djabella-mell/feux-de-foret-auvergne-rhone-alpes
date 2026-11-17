---
updated: 2026-11-17
---
# Analyse de la commande - Melissa DJABELLA

**Exercice 1 – De la commande aux données, partie B (individuelle)** · Projet feux-de-foret-auvergne-rhone-alpes

Ce que j'ai compris de la commande : la direction doit décider **où** concentrer ses moyens et **à partir de quel niveau** de la Météo des forêts déclencher le dispositif renforcé, sachant que le budget ne permet pas de renforcer tout le département tout l'été.

## 1. Les questions

Quatre questions dont la réponse aiderait la direction à trancher.

> [!test] Test
> Le test : si la réponse est X, la direction fait A ; si elle est Y, elle fait B. Si A et B sont identiques, ce n'est pas une question analytique pertinente.

1. **Où se passent vraiment les départs de feu dans le Rhône, en nombre et en gravité ?**
   - Les feux graves se concentrent dans quelques communes → la direction y envoie patrouilles, guet et budget.
   - Les départs sont nombreux ailleurs que là où les feux deviennent graves → prévention là où ils démarrent, moyens de lutte là où ils grossissent.
2. **Combien de fois l'indice « se trompe »-t-il, selon le seuil choisi ?** Pour chaque seuil possible : combien de jours annoncés à risque sans feu, et combien de feux partis sous le seuil ?
   - Un seuil limite les deux erreurs → la direction l'adopte.
   - Baisser le seuil multiplie les jours sans feu pour peu de feux en plus → elle garde le seuil haut et traite les feux restants autrement.
3. **À quels moments les feux partent-ils (mois, jour, heure), et d'où viennent-ils (cause, lisière, bord de route) ?**
   - Ils se concentrent sur des créneaux précis → renfort seulement sur ces créneaux.
   - Ils sont surtout d'origine humaine, près des routes ou des zones de loisirs → prévention et sensibilisation plutôt que guet.
4. **L'indice se comporte-t-il pareil dans le Rhône, dans les autres départements de la région et en France ?**
   - Non : le Rhône est plus souvent à risque, ou il a plus de feux à niveau égal → seuil propre au Rhône.
   - Oui → seuil aligné sur ses voisins, et le niveau de moyens se justifie par la comparaison.

J'ai écarté « combien de feux en France ? » et « quel est l'indice moyen ? » : quelle que soit la réponse, la direction ne ferait rien de différent.

## 2. Les termes inconnus

Les mots de la commande que vous ne savez pas définir précisément, ou qui peuvent se comprendre de plusieurs façons.

| Terme | Ce que je crois qu'il veut dire | Ce qu'il faudrait vérifier |
|---|---|---|
| SDMIS | Le service d'incendie et de secours du Rhône, commanditaire | Couvre-t-il aussi la Métropole de Lyon ? (Oui : 69D et 69M dans le COG.) |
| Météo des forêts | Indice quotidien de danger de feu publié par Météo-France | Calcul, niveaux, maille, historique disponible |
| Indice et seuil | Le seuil est le niveau à partir duquel on change de dispositif | Le seuil actuel du SDMIS |
| Dispositif renforcé | Patrouilles, guet, etc. | Moyens exacts et coût par jour : à demander |
| Départ de feu | Début d'un feu détecté et signalé | Surface minimale ; feux agricoles inclus ou non |
| Fausse alerte / feu manqué | Faux positif / faux négatif | Un jour « élevé » sans feu n'est pas forcément une erreur de l'indice |
| Fraîcheur | Délai entre l'événement et la disponibilité de la donnée | Pour la BDIFF : l'année N-1 seulement |
| Maille | Zone sur laquelle une donnée météo est calculée | Météo des forêts : le département |
| Base nationale des feux de forêt | Base publique qui recense les feux | Nom exact : BDIFF (bdiff.agriculture.gouv.fr) ; contenu vérifié le 17/11 |
| Occupation du sol, lisière | Nature de la surface, frontière forêt-habitat | Source : BD Forêt V2 (IGN) |

## 3. Les besoins

La décision à éclairer, en une phrase : fixer pour 2027 les secteurs prioritaires et le niveau de la Météo des forêts qui déclenche le dispositif renforcé, dans le budget disponible.

Ce qui manque dans la commande pour y répondre (une information, une précision, une hypothèse à confirmer) :
- Le coût d'un feu et d'une journée de renforcement pour le SDMIS (effectifs, engins, temps passé) : sans lui, impossible de traduire un seuil en budget.
- Le seuil actuel et ce que recouvre le « dispositif renforcé ».
- Une vérification de l'hypothèse « 2027 comme 2026 ou pire » : la tendance du nombre de feux sur plusieurs années.
- Les interventions du SDMIS, pour l'été 2026 que la base nationale ne couvre pas encore.
- Le contexte du terrain (occupation du sol, lisières) pour comprendre pourquoi certaines zones brûlent plus.

## 4. Les données

Pour chaque question, la donnée qu'il vous faudrait idéalement pour répondre.

| Question | Donnée idéale | Grain (une ligne = ?) | Période | Fraîcheur | Emprise géographique |
|---|---|---|---|---|---|
| 1 | Départs de feu : date, heure, commune, surface, cause, végétation ; occupation du sol | 1 feu ; 1 polygone de végétation | 15 à 20 ans, jusqu'à l'été 2026 | Saison précédente complète | Rhône (détail), région |
| 2 | Niveau Météo des forêts jour par jour + calendrier complet, jours sans feu compris | 1 département × 1 jour | Période commune avec les feux | Quotidienne | Rhône, région |
| 3 | Départs de feu horodatés avec cause ; interventions SDMIS (horaires, engins, durée) | 1 feu ; 1 intervention | Au moins 5 ans, 2026 inclus | Saison précédente | Rhône |
| 4 | Niveaux quotidiens et feux de tous les départements ; surface boisée | 1 département × 1 jour | Période commune | Quotidienne / annuelle | Région et France |

**Points de vigilance**
- Les feux non signalés n'apparaissent pas : le nombre de feux est sous-estimé. C'est confirmé le 17/11, le Rhône ne compte que 62 feux dans la BDIFF en 20 ans.
- Pour calculer un seuil, il faut aussi les jours **sans** feu.
- Les coordonnées précises sont à éviter (agrégation à la commune), à valider avec la responsable qualité et conformité.
