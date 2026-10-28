# Semaine 5 : l'interface, notes du binôme

> Trois questions, quelques phrases chacune. Répondez avec ce que vous avez observé.

## 1. Pourquoi l'interface n'importe-t-elle jamais `predict()` ni le fichier `.joblib` ?

Parce que la page est un client de l'API, comme n'importe quel autre programme :
elle ne connaît que `ui/client.py`, qui envoie `POST /predict` sur le port 8000 et
traduit la réponse. C'est la troisième règle d'architecture du dépôt : les clients
passent par l'API, jamais par le fichier `.joblib`. Conséquence observée : nous
avons réentraîné le modèle (`python src/train.py`) sans toucher une ligne de
`ui/app.py`, et la page a continué de fonctionner ; demain, une API déplacée sur un
autre serveur ne demanderait que le changement de `API_URL`. Si la page importait
`predict()`, elle chargerait sa propre copie du modèle, avec son propre seuil, et
les deux programmes pourraient donner des verdicts différents pour le même avis.

## 2. Que montre l'interface quand le modèle hésite, et pourquoi est-ce mieux qu'un verdict forcé ?

Pour « xqzvb wlkptr grombu », l'API répond `INDETERMINE` avec 0,5162 de confiance,
et la page affiche « Je ne sais pas… » avec le message « la confiance est sous le
seuil d'abstention : un humain doit trancher ». Sans le seuil du TP4, le même texte
recevait NEGATIVE à 0,5162 : un verdict présenté avec la même assurance qu'un vrai,
alors que le TF-IDF n'a reconnu aucun mot. Pour l'équipe relation client, une
abstention est une file « à vérifier » ; un faux NEGATIVE ferait traiter en urgence
un avis qui n'en est pas un, et un faux POSITIVE enterrerait un client mécontent.
Dire « je ne sais pas » est une information fiable ; forcer un verdict en fabrique
une fausse.

## 3. Que voit l'utilisateur quand l'API tombe ? Et le fichier `data/avis_exemple.csv` : combien d'avis partent vers un humain ?

API arrêtée (Ctrl+C dans son terminal) puis page rechargée : un bandeau d'erreur
en haut de la page, « API injoignable : lancez d'abord uvicorn api.main:app » —
le client transforme l'échec de connexion en message, la page n'affiche jamais de
trace technique. Trois espaces dans le champ donnent l'avertissement « Texte
refusé : vide, fait d'espaces, ou de plus de 2000 caractères » (le 422 du schéma).
Sur `data/avis_exemple.csv` : six avis, résumé observé
`{'INDETERMINE': 1, 'NEGATIVE': 2, 'POSITIVE': 3}` — un avis sur six part vers un
humain (« xqzvb wlkptr grombu », 0,52 de confiance), et le bouton « Télécharger
les résultats » renvoie le tableau complété en `resultats.csv`.
