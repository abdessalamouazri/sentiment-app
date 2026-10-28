"""23 tests d'environnement : Python, paquets, structure, .gitignore."""
import importlib
import subprocess
import sys

import pytest

REQUIRED_DIRS = ["app", "data", "docs", "models", "scripts", "tests", "ui"]
REQUIRED_FILES = ["README.md", "requirements.txt", ".gitignore", ".env.example"]
GITIGNORE_MUST_CONTAIN = [".venv/", "__pycache__/", ".env", "models/", "mlruns/"]
CORE_PACKAGES = ["pandas", "sklearn", "pytest"]


def test_python_version():
    assert sys.version_info >= (3, 10), (
        f"Python 3.10 minimum attendu, trouvé {sys.version.split()[0]}"
    )


def test_virtualenv_active():
    assert sys.prefix != getattr(sys, "base_prefix", sys.prefix), (
        "aucun environnement virtuel actif : activez .venv avant de lancer pytest"
    )


@pytest.mark.parametrize("module", CORE_PACKAGES)
def test_core_package_importable(module):
    try:
        importlib.import_module(module)
    except ImportError:
        pytest.fail(f"le paquet {module} ne s'importe pas : venv non activé ou paquet absent")


@pytest.mark.parametrize("dirname", REQUIRED_DIRS)
def test_required_directory_exists(root, dirname):
    assert (root / dirname).is_dir(), f"dossier manquant : {dirname}/"


@pytest.mark.parametrize("filename", REQUIRED_FILES)
def test_required_file_exists(root, filename):
    assert (root / filename).is_file(), f"fichier manquant : {filename}"


def test_requirements_pins_versions(root):
    lines = (root / "requirements.txt").read_text(encoding="utf-8").splitlines()
    useful = [ligne.strip() for ligne in lines if ligne.strip() and not ligne.strip().startswith("#")]
    assert useful, "requirements.txt est vide"
    for line in useful:
        assert "==" in line, f"version non figée dans requirements.txt : {line}"


@pytest.mark.parametrize("pattern", GITIGNORE_MUST_CONTAIN)
def test_gitignore_contains(root, pattern):
    content = (root / ".gitignore").read_text(encoding="utf-8")
    assert pattern in content, f"motif absent du .gitignore : {pattern}"


def test_no_real_env_file_committed(root):
    try:
        result = subprocess.run(
            ["git", "ls-files"], cwd=root, capture_output=True, text=True
        )
    except FileNotFoundError:
        pytest.skip("git absent du PATH")
    if result.returncode != 0:
        pytest.skip("pas de dépôt Git")
    tracked = result.stdout.splitlines()
    offenders = [
        f for f in tracked
        if f == ".env" or f.startswith(".venv/") or f.startswith(".venv\\")
    ]
    assert not offenders, f".env ou .venv/ suivis par Git : {offenders}"
