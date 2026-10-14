# Semaine 2 : analyse des erreurs

Sur le jeu de démonstration, le modèle fait 7 erreurs sur 58 avis de test (F1 macro 0,879) : 5 positifs classés négatifs et 2 négatifs classés positifs, et les exemples affichés sont tous des avis mitigés comme « Commande jamais reçue et remboursement en attente au début, sauf que ensuite je recommande ».
Ces erreurs viennent du sac de mots : le modèle additionne les mots positifs et négatifs sans tenir compte de leur ordre, donc il ne voit pas le retournement « sauf que ensuite » alors que c'est la seconde moitié de l'avis qui porte l'étiquette.
Pour les corriger, il faudrait une représentation qui prend en compte le contexte et l'ordre des mots, comme des embeddings ou un modèle de type transformer, ce qui sera abordé en semaine 9.
