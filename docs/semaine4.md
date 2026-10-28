# Semaine 4 : tests approfondis et qualité, notes du binôme

> Une à deux pages. Uniquement des chiffres issus de VOS exécutions.

## 1. Couverture

- Avant (étape A) : 91 %, lignes jamais exécutées : `api/main.py` 49, 77-79, 85-87.
- Pour chacune, le comportement qu'aucun test ne vérifiait : la ligne 49 est le 503
  quand le modèle n'est pas chargé ; les lignes 77-79 sont le 500 quand le modèle
  plante ; les lignes 85-87 sont le lancement direct (`uvicorn.run`), jamais exécuté
  sous pytest.
- Après (étape D) : … % ; lignes exclues de la mesure et pourquoi : …

## 2. Défauts trouvés

| Symptôme | Test qui l'a révélé | Correction |
| --- | --- | --- |
| … | … | … |

## 3. Seuil d'abstention

- Deux ou trois points de la courbe (`python src/courbe_seuil.py`) : …
- Seuil retenu : … ; part des avis envoyés à un humain : … ; justification : …

## 4. Jeu d'or

- Bilan (`python src/bilan_jeu_or.py`) : justes …, abstentions …, erreurs franches déclarées …
- Ce que ces chiffres disent du modèle : …

## 5. Outils statiques

- Remarques au départ : ruff 9 (B904 ×2 dans `api/main.py` ; I001 et F401 dans
  `api/model.py` ; F401 et B905 ×2 dans `src/evaluate.py` ; I001 dans
  `tests/test_api.py` ; E741 dans `tests/test_environment.py`), mypy 0
  (`Success: no issues found in 4 source files`).
- Parmi les défauts de la partie 2, combien ruff et mypy avaient-ils signalés ? Qu'en concluez-vous ?
