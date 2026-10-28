"""Raccord entre l'API et le modèle entraîné au TP2.

L'API n'entraîne rien et ne connaît pas scikit-learn : elle appelle la fonction
predict() de src/predict.py, qui charge models/sentiment.joblib une seule fois.
"""
import sys
from pathlib import Path
from typing import Literal, TypedDict

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
from predict import charger_modele  # noqa: E402  (fonctions du TP2)
from predict import predict as _predict  # noqa: E402

Etiquette = Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]

# Correspondance explicite entre les étiquettes du modèle et celles du contrat,
# vérifiée au démarrage : un modèle aux étiquettes inconnues ne démarre pas.
CORRESPONDANCE: dict[str, Etiquette] = {"positive": "POSITIVE", "negative": "NEGATIVE"}

# Sous ce seuil de confiance, l'API s'abstient : INDETERMINE, un humain tranche.
# Mesuré avec src/courbe_seuil.py : à 0.60, exactitude 0.952 au lieu de 0.879,
# 16 avis sur 58 partent vers un humain.
SEUIL_ABSTENTION = 0.60


class Verdict(TypedDict):
    """Ce que l'API renvoie : une étiquette du contrat, un score, un aperçu."""

    label: Etiquette
    score: float
    text: str


class SentimentClassifier:
    """Enveloppe du modèle TP2 avec l'interface attendue par l'API."""

    model_name = "tfidf-logreg (TP2, models/sentiment.joblib)"

    def __init__(self) -> None:
        # Échoue immédiatement si le joblib manque : on ne démarre pas sans modèle.
        pipeline = charger_modele()
        inconnues = {str(c) for c in pipeline.classes_} - set(CORRESPONDANCE)
        if inconnues:
            raise ValueError(f"modèle aux étiquettes inconnues du contrat : {sorted(inconnues)}")

    def predict(self, text: str) -> Verdict:
        """Renvoie le verdict ; INDETERMINE quand la confiance est sous le seuil."""
        r = _predict(text)  # lève ValueError si le texte est vide
        label: Etiquette = CORRESPONDANCE[r["label"]]
        if r["score"] < SEUIL_ABSTENTION:
            label = "INDETERMINE"
        return {"label": label, "score": r["score"], "text": text[:100]}


def load_model() -> SentimentClassifier:
    """Construit le classifier (le cache de chargement est dans src/predict.py)."""
    return SentimentClassifier()
