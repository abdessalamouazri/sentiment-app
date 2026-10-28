# Semaine 6 : le paquet, notes du binôme

> Trois questions, quelques phrases chacune. Répondez avec ce que vous avez observé.

## 1. Pourquoi le modèle n'est-il pas dans la roue ? Comment le paquet le trouve-t-il ?

La roue ne contient que du code (`api`, `sentiment_app`, `ui`) : le modèle est un
artefact lourd et reproductible, propre à chaque déploiement — même règle qu'au TP2,
où seul `models/metrics.json` entre dans Git. Le paquet le cherche via
`chemin_modele()` : d'abord la variable d'environnement `SENTIMENT_MODELE`, sinon
`models/sentiment.joblib` sous la racine. Observé au T40 : sans la variable, la
commande échoue proprement (« modèle introuvable : …\roue-tp6\Lib\site-packages\
models\sentiment.joblib. Lancez python src/train.py, ou indiquez son chemin dans la
variable SENTIMENT_MODELE », code de sortie 1) ; avec la variable pointant sur le
modèle du dépôt, elle répond `POSITIVE` à 0,777 — le même verdict que l'API.

## 2. Qu'est-ce qui a changé dans api/model.py quand predict() est entré dans le paquet, et pourquoi est-ce mieux ?

Les quatre lignes de bricolage ont disparu : `RACINE = ...`,
`sys.path.insert(0, str(RACINE / "src"))` et les deux imports marqués
`# noqa: E402`. À la place, deux imports ordinaires :
`from sentiment_app.predict import charger_modele` et `predict as _predict`.
C'est mieux parce que l'import ne dépend plus de l'endroit d'où on lance le
programme ni d'une manipulation du chemin de Python à l'exécution : une fois le
paquet installé (editable en développement, roue en production), `sentiment_app`
se trouve comme n'importe quelle bibliothèque. C'est ce que vérifie
`test_l_api_ne_bricole_plus_le_chemin_de_python`, et `Select-String -Path api\*.py
-Pattern "sys.path"` ne renvoie plus rien.

## 3. La roue installée hors du dépôt : qu'a-t-il fallu lui fournir, et pourquoi scikit-learn est-il épinglé dans pyproject.toml ?

Deux choses seulement : un environnement Python où `pip install` la roue (pip a
téléchargé lui-même FastAPI, uvicorn, Pydantic, scikit-learn 1.5 et joblib depuis
les métadonnées du paquet), et le chemin d'un modèle entraîné via
`SENTIMENT_MODELE` — aucun fichier du dépôt, ni `requirements.txt`, ni `src/`.
scikit-learn est épinglé `>=1.5,<1.6` parce que le fichier
`models/sentiment.joblib` est une sérialisation d'objets scikit-learn : il ne se
relit de façon fiable qu'avec la version qui l'a écrit. Une roue installée avec un
scikit-learn 1.6 pourrait refuser de charger, ou pire, charger un pipeline au
comportement différent ; l'épingle fait échouer l'installation plutôt que la
prédiction.
