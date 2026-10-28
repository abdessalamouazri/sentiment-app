# Semaine 4 : tests approfondis et qualité, notes du binôme

> Une à deux pages. Uniquement des chiffres issus de VOS exécutions.

## 1. Couverture

- Avant (étape A) : 91 %, lignes jamais exécutées : `api/main.py` 49, 77-79, 85-87.
- Pour chacune, le comportement qu'aucun test ne vérifiait : la ligne 49 est le 503
  quand le modèle n'est pas chargé ; les lignes 77-79 sont le 500 quand le modèle
  plante ; les lignes 85-87 sont le lancement direct (`uvicorn.run`), jamais exécuté
  sous pytest.
- Après (étape D) : 97,7 % sans exclusion, 100 % avec une seule exclusion : le bloc
  `if __name__ == "__main__":` de `api/main.py`, jamais exécuté sous pytest et couvert
  à la main à chaque TP par `uvicorn api.main:app` (exclusion déclarée et justifiée
  dans `pyproject.toml`).

## 2. Défauts trouvés

| Symptôme | Test qui l'a révélé | Correction |
| --- | --- | --- |
| Un texte fait d'espaces donne un 422 dont `detail` est la chaîne `'texte vide'`, pas la liste standard de FastAPI : deux formes pour le même refus | `test_frontieres_du_contrat[espaces-seuls]` et la propriété hypothesis des blancs (`Falsifying example: texte='\x85'`) | `field_validator` dans `api/schemas.py` : le schéma refuse un texte vide une fois ses blancs retirés, même règle que `predict()` du TP2 |
| Une panne `ValueError("bug interne")` du modèle répondait 422 **avec le message interne** dans la réponse | `test_toute_panne_du_modele_donne_500_sans_le_message[ValueError]` | Suppression de la conversion `ValueError` → 422 dans `api/main.py` : le schéma garantit l'entrée, toute exception du modèle est un bug → 500, message journalisé côté serveur seulement |
| Sans mot connu du vocabulaire, le modèle répond toujours NEGATIVE à 0,5162 (il ne reste que l'ordonnée à l'origine) | Essais `/docs` sur des mots inventés, puis `test_tout_texte_non_blanc_recoit_un_verdict` | Seuil d'abstention dans `api/model.py` : sous 0,60, l'étiquette devient INDETERMINE |
| `predict()` renvoyait un `dict` non typé : mypy laissait passer n'importe quelle sortie, et `.upper()` masquait les étiquettes inconnues | mypy après le passage au `TypedDict` | `Verdict(TypedDict)` avec `Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]`, correspondance explicite des étiquettes vérifiée au démarrage (`test_modele_aux_etiquettes_inconnues_refuse`) |

## 3. Seuil d'abstention

- Trois points de la courbe (`python src/courbe_seuil.py`, 58 avis de test) :
  à 0,50 le modèle répond à tout, exactitude 0,879, 7 erreurs ; à 0,60 il répond à
  72 %, exactitude 0,952, 2 erreurs, 16 avis vers un humain ; à 0,70 exactitude 1,000
  mais 21 avis sur 58 partent vers un humain.
- Seuil retenu : 0,60 ; part des avis envoyés à un humain : 28 % (16/58) ;
  justification : c'est le premier seuil qui divise les erreurs par trois (7 → 2)
  sans envoyer plus d'un tiers de la file au service client ; au-delà, chaque point
  d'exactitude coûte trop d'avis déroutés.

## 4. Jeu d'or

- Bilan (`python src/bilan_jeu_or.py`, 20 avis) : justes 6, abstentions 11,
  erreurs franches déclarées 3.
- Ce que ces chiffres disent du modèle : le modèle de démonstration (316 termes de
  vocabulaire) ne connaît pas la plupart des mots de nos avis rédigés à la main,
  d'où 11 abstentions — le seuil fait son travail : il déroute vers un humain plutôt
  que de se tromper. Les 3 erreurs franches ont une cause lisible : vocabulaire
  absent (« écrasé », « aux abonnés absents ») et ironie, que le sac de mots ne peut
  pas voir. Elles restent déclarées en `xfail(strict=True)` : le jour où un meilleur
  modèle les corrige, le test le signalera.

## 5. Outils statiques

- Remarques au départ : ruff 9 (B904 ×2 dans `api/main.py` ; I001 et F401 dans
  `api/model.py` ; F401 et B905 ×2 dans `src/evaluate.py` ; I001 dans
  `tests/test_api.py` ; E741 dans `tests/test_environment.py`), mypy 0
  (`Success: no issues found in 4 source files`).
- Parmi les défauts de la partie 2, combien ruff et mypy avaient-ils signalés ?
  Aucun des quatre. ruff signalait des défauts de forme (imports, `zip` sans
  `strict`, `raise` sans `from`) et mypy ne disait rien tant que `predict()`
  renvoyait un `dict` : tout ce qui en sortait était `Any`. Conclusion : les outils
  statiques attrapent une classe de défauts (forme, types déclarés), jamais les
  défauts de comportement — ceux-là ne tombent qu'avec des tests qui exercent les
  frontières et les pannes. Les deux familles sont complémentaires, aucune ne
  remplace l'autre.
