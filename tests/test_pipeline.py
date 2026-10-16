import pandas as pd
import pytest

from src.pipeline import clean_file, clean_upload, organize_folder
from src.reports import format_report


@pytest.fixture
def csv_demo(tmp_path):
    df = pd.DataFrame(
        {
            "nom": ["  diop ", "FALL", "Ndiaye", "Ndiaye", None],
            "prenom": ["Awa", "moussa", "Fatou", "Fatou", "Omar"],
            "email": ["awa@gmail.com", "moussa@gmail", "Fatou@Gmail.COM", "fatou@gmail.com", "omar@@gmail.com"],
            "telephone": ["771", "772", "773", "773", None],
        }
    )
    chemin = tmp_path / "clients.csv"
    df.to_csv(chemin, index=False)
    return chemin


def test_scenario_complet(csv_demo, tmp_path):
    original = csv_demo.read_bytes()
    r = clean_file(csv_demo, tmp_path / "sortie")

    assert r["lignes_lues"] == 5
    assert r["lignes_exportees"] == 4
    assert r["doublons_supprimes"] == 1
    assert r["emails_invalides"] == 2
    assert r["champs_manquants"] == {"nom": 1, "telephone": 1}
    assert r["lignes_emails_invalides"] == [3, 6]  # numéros de ligne Excel

    assert (tmp_path / "sortie" / "clients_nettoye.xlsx").exists()
    assert (tmp_path / "sortie" / "clients_rapport.txt").exists()
    assert csv_demo.read_bytes() == original  # le fichier d'origine est intact


def test_rapport_contient_les_informations(csv_demo, tmp_path):
    texte = format_report(clean_file(csv_demo, tmp_path / "sortie"))
    for attendu in ["Lignes lues : 5", "Doublons supprimés : 1", "E-mails invalides : 2", "Durée du traitement"]:
        assert attendu in texte


def test_rapport_necrase_pas(csv_demo, tmp_path):
    r1 = clean_file(csv_demo, tmp_path / "sortie")
    r2 = clean_file(csv_demo, tmp_path / "sortie")
    assert r1["fichier_rapport"] != r2["fichier_rapport"]
    assert r1["fichier_nettoye"] != r2["fichier_nettoye"]


def test_clean_file_erreur_fichier_absent(tmp_path):
    with pytest.raises(FileNotFoundError):
        clean_file(tmp_path / "absent.csv", tmp_path / "sortie")


def test_clean_upload(csv_demo, tmp_path):
    r = clean_upload("clients.csv", csv_demo.read_bytes(), tmp_path / "sortie")
    assert r["lignes_exportees"] == 4
    assert r["fichier_source"] == "clients.csv"


def test_clean_upload_ignore_les_chemins(csv_demo, tmp_path):
    r = clean_upload("../../dossier/clients.csv", csv_demo.read_bytes(), tmp_path / "sortie")
    assert r["fichier_source"] == "clients.csv"


def test_clean_upload_fichier_vide(tmp_path):
    with pytest.raises(ValueError, match="vide"):
        clean_upload("vide.csv", b"", tmp_path / "sortie")


def test_organize_folder(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    (src / "a.pdf").write_text("x")
    (src / "b.txt").write_text("x")
    r = organize_folder(src, tmp_path / "dest", mode="extension")
    assert r["fichiers_traites"] == 2
    assert r["fichiers_classes"] == 2
    assert r["erreurs"] == []
    assert len(list((tmp_path / "dest").glob("*_rapport.txt"))) == 1


def test_le_rapport_est_dans_les_fichiers_generes(csv_demo, tmp_path):
    r = clean_file(csv_demo, tmp_path / "sortie")
    assert r["fichier_rapport"] in r["fichiers_generes"]