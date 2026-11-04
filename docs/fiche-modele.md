# Fiche modèle : sentiment-app

> Une fiche modèle dit, en une page, ce que fait le modèle, sur quelles données il a appris, ce qu'il
> vaut, où il se trompe et dans quelles conditions on peut s'en servir. Remplacez chaque consigne par
> votre texte ; les lignes qui commencent par « > » ne comptent pas. Les tests vérifient que chaque
> rubrique est remplie et que les chiffres cités sont ceux du dépôt.

## Identité du modèle

> Nom, version du paquet (celle de sentiment_app.__version__), date d'entraînement, type de modèle.

Classifieur de sentiment `tfidf-logreg`, livré par le paquet `sentiment-app` version 0.6.0,
entraîné le 2026-11-04 (date de `models/metrics.json`). Pipeline scikit-learn : TF-IDF
(unigrammes et bigrammes, 316 termes) suivi d'une régression logistique binaire ; le fichier
`models/sentiment.joblib` n'est pas distribué avec le paquet.

## Usage prévu

> Pour qui, pour quelle décision, dans quel flux de travail (relation client, avis en français).

Pour l'équipe relation client : prioriser la file des avis clients rédigés en français, en
faisant remonter les avis classés négatifs pour y répondre d'abord. Le modèle propose un ordre
de traitement via l'API (`POST /predict`) ou l'interface Streamlit ; il ne répond jamais au
client lui-même.

## Usages exclus

> Ce pour quoi le modèle ne doit pas servir : au moins deux cas.

Ne pas s'en servir pour : une décision individuelle à conséquence (rembourser, sanctionner,
supprimer un avis ou un compte) ; des textes hors domaine ou hors langue (courriels, tickets
de support, avis en anglais ou en darija) ; toute mesure de la satisfaction d'une personne
identifiée. Le verdict porte sur un texte, pas sur un client.

## Données d'entraînement

> Source, taille, répartition des classes, langue, domaine ; ce que ces données ne couvrent pas.

Jeu de démonstration généré par `src/make_demo.py` : 290 avis e-commerce en français, 145
positifs et 145 négatifs (232 pour l'entraînement, 58 pour le test), dont 100 avis mitigés et
30 neutres. Ces données ne couvrent ni l'argot, ni les fautes d'orthographe, ni les domaines
autres que l'e-commerce (hôtellerie, santé), ni les avis très longs : le vocabulaire appris ne
compte que 316 termes.

## Performances mesurées

> Le F1 macro et le rappel des négatifs, tels que dans models/metrics.json ; le seuil d'abstention de
> l'API et ce qu'il change (part des avis traités, erreurs restantes, avis envoyés à un humain).

Sur le jeu de test de 58 avis (`models/metrics.json`) : F1 macro 0.879, exactitude 0.8793,
rappel de la classe négative 0.931. L'API applique un seuil d'abstention de 0,60
(`src/courbe_seuil.py`) : elle répond alors à 42 avis sur 58 (72 %), avec 2 erreurs restantes
au lieu de 7, et envoie 16 avis vers un humain.

## Limites connues

> Les cas où le modèle se trompe, avec un exemple : ce que montrent l'étape F du TP2 et le jeu d'or.

Le sac de mots ne voit pas le retournement d'un avis mitigé : « Taille trop petite et retour
payant au déballage, sauf que ensuite produit conforme à la description, très satisfait » est
classé negative à 0,5335, les deux moitiés se compensant presque (contributions -1,0061 contre
+0,9177). Sur le jeu d'or de 20 avis rédigés à la main : 6 justes, 11 abstentions et 3 erreurs
franches déclarées, dont l'ironie (« Superbe qualité... si on aime les coutures qui lâchent »)
et le vocabulaire inconnu (« aux abonnés absents »).

## Biais mesurés

> Les groupes d'avis moins bien servis, chiffres de python src/biais.py à l'appui.

`python src/biais.py` sur les 58 avis de test : les avis avec retournement (17 avis) sont à
0,588 d'exactitude contre 1,000 pour les avis directs (41 avis) ; les 7 erreurs du modèle sont
toutes dans ce groupe. La longueur n'est pas la cause : les 10 avis longs sans retournement
sont tous justes. Effectifs faibles (17 avis) : l'écart est net mais à confirmer sur un vrai
jeu de données.

## Explicabilité

> Ce que montre python src/expliquer.py : les termes qui pèsent le plus, et ce que cela révèle.

`python src/expliquer.py` (SHAP sur le modèle linéaire, exact) : les termes qui poussent le
plus vers positive sont « je » (+0,771), « que je » (+0,764), « en » (+0,683) ; vers negative,
« arrivée », « cassé », « produit cassé » (-0,923). Des mots-outils figurent en tête : le
modèle a appris les tournures du jeu de démonstration, pas seulement des mots porteurs de
sentiment — une raison de plus de le réentraîner sur de vraies données avant tout usage sérieux.

## Conditions d'usage

> Ce qu'un humain doit vérifier, quand, et ce qu'on ne doit jamais décider sur la seule foi du modèle.

Un humain traite tous les avis : le modèle ne fait qu'ordonner la file. Il vérifie
systématiquement les avis INDETERMINE (confiance sous 0,60) et peut requalifier tout verdict
d'un clic ; les requalifications alimentent le réentraînement. On ne décide jamais sur la
seule foi du modèle d'une réponse au client, d'un remboursement ou de la suppression d'un
avis ; en cas de doute, l'avis part vers un humain, jamais vers une réponse automatique.

## Maintenance

> Quand réentraîner, avec quelle version de scikit-learn, comment indiquer le modèle au paquet.

Réentraîner avec `python src/train.py` (jeu de démonstration) ou `--allocine` (20 000 avis
réels), puis mettre cette fiche et `models/metrics.json` à jour : les tests échouent si les
chiffres cités ne sont plus ceux du dépôt. scikit-learn est épinglé `>=1.5,<1.6` dans
`pyproject.toml` : le joblib ne se relit qu'avec la version qui l'a écrit. Le paquet installé
hors du dépôt trouve le modèle par la variable d'environnement `SENTIMENT_MODELE` ; surveiller
la dérive est l'objet de la semaine 9.
