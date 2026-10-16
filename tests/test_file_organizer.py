import os
from datetime import datetime

import pytest

from src.file_organizer import organize_files
from src.utils import unique_path


def creer_fichier(dossier, nom, date="2026-09-12", contenu="test"):
    """Crée un fichier avec une date de modification donnée."""
    chemin = dossier / nom
    chemin.write_text(contenu, encoding="utf-8")
    ts = datetime.strptime(date, "%Y-%m-%d").timestamp()
    os.utime(chemin, (ts, ts))
    return chemin


@pytest.fixture
def source(tmp_path):
    dossier = tmp_path / "source"
    dossier.mkdir()
    creer_fichier(dossier, "Liste Clients.xlsx", "2026-09-12")
    creer_fichier(dossier, "rapport.pdf", "2026-09-30")
    creer_fichier(dossier, "notes.TXT", "2026-10-02")
    creer_fichier(dossier, "LISEZMOI", "2026-10-14")
    return dossier


def destinations(resultats):
    return sorted(r["destination"].replace("\\", "/") for r in resultats)


def test_classement_par_extension(source, tmp_path):
    res = organize_files(source, tmp_path / "dest", mode="extension")
    assert destinations(res) == [
        "pdf/2026-09-30_rapport.pdf",
        "sans_extension/2026-10-14_lisezmoi",
        "txt/2026-10-02_notes.txt",
        "xlsx/2026-09-12_liste_clients.xlsx",
    ]
    assert all(r["statut"] == "ok" for r in res)


def test_classement_par_date(source, tmp_path):
    res = organize_files(source, tmp_path / "dest", mode="date")
    dossiers = sorted({r["destination"].replace("\\", "/").split("/")[0] for r in res})
    assert dossiers == ["2026-09", "2026-10"]


def test_renommage_convention(source, tmp_path):
    organize_files(source, tmp_path / "dest", mode="extension")
    assert (tmp_path / "dest" / "xlsx" / "2026-09-12_liste_clients.xlsx").exists()


def test_sans_renommage(source, tmp_path):
    organize_files(source, tmp_path / "dest", mode="extension", rename=False)
    assert (tmp_path / "dest" / "xlsx" / "Liste Clients.xlsx").exists()


def test_collision_de_noms(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    creer_fichier(src, "Liste Clients.xlsx", contenu="premier")
    creer_fichier(src, "liste_clients.xlsx", contenu="second")
    res = organize_files(src, tmp_path / "dest")
    assert destinations(res) == ["xlsx/2026-09-12_liste_clients.xlsx", "xlsx/2026-09-12_liste_clients_1.xlsx"]
    contenus = sorted(p.read_text() for p in (tmp_path / "dest" / "xlsx").iterdir())
    assert contenus == ["premier", "second"]  # aucun fichier écrasé


def test_relancer_necrase_rien(source, tmp_path):
    organize_files(source, tmp_path / "dest")
    organize_files(source, tmp_path / "dest")
    assert len(list((tmp_path / "dest" / "pdf").iterdir())) == 2


def test_copie_laisse_les_originaux(source, tmp_path):
    organize_files(source, tmp_path / "dest", move=False)
    assert len(list(source.iterdir())) == 4


def test_deplacement_retire_les_originaux(source, tmp_path):
    organize_files(source, tmp_path / "dest", move=True)
    assert list(source.iterdir()) == []


def test_nom_deja_date_pas_double_prefixe(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    creer_fichier(src, "2026-01-05_budget.xlsx", "2026-09-12")
    res = organize_files(src, tmp_path / "dest")
    assert destinations(res) == ["xlsx/2026-01-05_budget.xlsx"]


def test_fichiers_caches_ignores(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    creer_fichier(src, ".gitkeep")
    creer_fichier(src, "notes.txt")
    res = organize_files(src, tmp_path / "dest")
    assert len(res) == 1


def test_sous_dossiers_ignores(tmp_path):
    src = tmp_path / "source"
    (src / "sous_dossier").mkdir(parents=True)
    creer_fichier(src, "notes.txt")
    res = organize_files(src, tmp_path / "dest")
    assert len(res) == 1


def test_dossier_source_introuvable(tmp_path):
    with pytest.raises(FileNotFoundError, match="introuvable"):
        organize_files(tmp_path / "absent", tmp_path / "dest")


def test_dossier_source_vide(tmp_path):
    src = tmp_path / "vide"
    src.mkdir()
    with pytest.raises(ValueError, match="aucun fichier"):
        organize_files(src, tmp_path / "dest")


def test_mode_inconnu(source, tmp_path):
    with pytest.raises(ValueError, match="Mode inconnu"):
        organize_files(source, tmp_path / "dest", mode="couleur")


def test_unique_path_fichier_libre(tmp_path):
    assert unique_path(tmp_path / "a.txt") == tmp_path / "a.txt"


def test_unique_path_incremente(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "a_1.txt").write_text("x")
    assert unique_path(tmp_path / "a.txt") == tmp_path / "a_2.txt"