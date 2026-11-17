# Journal des décisions

Chaque décision porte une date, un porteur et une justification. Une décision n'est jamais effacée : si elle change, une nouvelle ligne la remplace.

| N° | Date | Décision | Pourquoi | Conséquence | Porteur |
|---|---|---|---|---|---|
| D-01 | 17/11 | Les rôles sont répartis comme dans le README (proposition à valider). | 4 membres pour 4 rôles ; Melissa a créé le dépôt. | Les PR de chaque domaine sont relues par son responsable. | Groupe |
| D-02 | 17/11 | Les analyses individuelles sont rangées dans `docs/analyse/commande-prenom-nom.md` ; le fichier de Lynda, déposé à la racine, est déplacé avec `git mv`. | Consigne de l'exercice 1, partie B. | L'historique du fichier est conservé. | Cheffe de projet |
| D-03 | 17/11 | Comme la BDIFF ne suffit pas pour le Rhône, les sources sont exploitées à l'échelle des **12 départements de la région**. Une conclusion sur le Rhône sera présentée comme une transposition, tant que les données du SDMIS manquent. | La BDIFF ne recense que 62 feux dans le Rhône en 20 ans, avec 11 années à 0 (profil de qualité). | Le périmètre d'extraction est la région 84. | Sources |
| D-04 | 17/11 | La **BDIFF est la source de vérité** pour les feux jusqu'en 2025. Pour 2026, la source prévue est le SDMIS ; en attendant, la presse sert de proxy, signalé comme tel. | La BDIFF ne publie pas l'année en cours ; la presse n'est ni exhaustive ni normalisée. | Chaque feu porte sa source et un niveau de confiance. | Sources |
| D-05 | 17/11 | Le groupe **demande au SDMIS** ses interventions « feux de végétation » 2015-2026, sous forme minimisée, ainsi que le seuil actuel et le coût du dispositif. | Seule source qui couvre 2026 et le Rhône. La minimisation s'applique dès la demande. | Liste des champs dans `docs/sources/minimisation.md`. | Cheffe de projet |
| D-06 | 17/11 | Les fichiers bruts (`data/raw/`) **ne sont pas versionnés**. | Le dépôt est public, et les conditions de la BDIFF ne sont pas une licence ouverte : pas de modification, citation de la source, droits de reproduction réservés. | `.gitignore` ; procédure d'extraction décrite dans `src/README.md`. | Qualité et conformité |
| D-07 | 17/11 | Le **référentiel des communes est le COG 2026**. Un code absent est rattaché par la table des mouvements, et le code d'origine est conservé. | 48 feux (25 codes) ont un code absent du COG 2026 ; tous sont retrouvés. | Les jointures se font par code, jamais par libellé. | Qualité et conformité |
| D-08 | 17/11 | « Feu significatif » = surface parcourue d'au moins **1 ha** (définition provisoire). | Il faut un critère lisible pour la direction. | À faire valider par le SDMIS. | Groupe |
| D-09 | 17/11 | Le Rhône distingue **69D (Rhône)** et **69M (Métropole de Lyon)** grâce à la colonne `CTCD` du COG. | Le SDMIS couvre les deux collectivités ; la Météo des forêts et la BDIFF ne connaissent que « 69 ». | Les résultats sur le 69 pourront être séparés. | Sources |
