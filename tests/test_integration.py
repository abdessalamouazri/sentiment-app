"""Tests d'intégration : l'API telle qu'elle tourne vraiment (TP4, étape D).

Les tests du TP3 vérifient des réponses ; ceux-ci vérifient le démarrage de l'API
et son comportement quand le modèle manque ou tombe en panne.
"""
from pathlib import Path

import pytest

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")


def test_demarrage_reel_charge_le_modele():
    """D.1 (donné en exemple) : un client ouvert par « with » exécute le lifespan."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as client:
        reponse = client.get("/health")
    assert reponse.status_code == 200
    assert "TP2" in reponse.json()["model"]


def test_sans_modele_l_api_refuse_de_demarrer(monkeypatch, tmp_path):
    """D.2 : chemin du modèle redirigé vers un fichier absent, l'API ne démarre pas."""
    from fastapi.testclient import TestClient

    import api.model  # noqa: F401  (met src/ dans sys.path)
    import predict
    from api.main import app

    monkeypatch.setattr(predict, "MODELE", tmp_path / "absent.joblib")
    predict.charger_modele.cache_clear()
    try:
        with pytest.raises(FileNotFoundError):
            with TestClient(app):
                pass
    finally:
        predict.charger_modele.cache_clear()  # ne pas laisser un cache vide aux autres tests


def test_modele_retire_donne_503(monkeypatch):
    """D.3 : l'API démarrée mais le modèle retiré de app.state : 503 partout."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as client:
        monkeypatch.setattr(app.state, "classifier", None)
        assert client.get("/health").status_code == 503
        assert client.post("/predict", json={"text": "très bon produit"}).status_code == 503


class ModeleEnPanne:
    """Un classifier qui plante : l'API doit répondre 500 sans divulguer le message."""

    model_name = "modele-en-panne"

    def __init__(self, exception: Exception) -> None:
        self.exception = exception

    def predict(self, text: str) -> dict:
        raise self.exception


@pytest.mark.parametrize(
    "panne", [RuntimeError("panne interne du gpu"), ValueError("bug interne")],
    ids=["RuntimeError", "ValueError"],
)
def test_toute_panne_du_modele_donne_500_sans_le_message(monkeypatch, panne):
    """D.4 : RuntimeError comme ValueError : 500, et le message interne reste côté serveur."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app, raise_server_exceptions=False) as client:
        monkeypatch.setattr(app.state, "classifier", ModeleEnPanne(panne))
        reponse = client.post("/predict", json={"text": "très bon produit"})
    assert reponse.status_code == 500
    assert str(panne) not in reponse.text


def test_modele_aux_etiquettes_inconnues_refuse(monkeypatch):
    """D.5 : un modèle dont les classes ne sont pas dans la correspondance ne démarre pas."""
    import api.model

    class PipelineExotique:
        classes_ = ["positif", "négatif"]  # pas les étiquettes du contrat

    monkeypatch.setattr(api.model, "charger_modele", lambda: PipelineExotique())
    with pytest.raises(ValueError, match="étiquettes inconnues"):
        api.model.load_model()
