import pandas as pd
import pytest

from src.data_cleaning import (
    EMAIL_REGEX, clean_dataframe, detect_duplicates, detect_invalid_emails, detect_missing,
    export_dataframe, load_file, quality_report, remove_duplicates,
)


@pytest.fixture
def raw_df():
    """Petit jeu de données avec toutes les erreurs à détecter."""
    return pd.DataFrame(
        {
            "nom": ["  diop ", "FALL", "Ndiaye", "Ndiaye", None],
            "prenom": ["Awa", "moussa", "Fatou", "Fatou", "Omar"],
            "email": ["awa@gmail.com", "moussa@gmail", "Fatou@Gmail.COM", "fatou@gmail.com", "omar@@gmail.com"],
            "telephone": ["771", "772", "773", "773", None],
        }
    )


# ---------- Importation ----------
def test_load_csv_valide(tmp_path, raw_df):
    chemin = tmp_path / "clients.csv"
    raw_df.to_csv(chemin, index=False)
    df = load_file(chemin)
    assert df.shape == (5, 4)


def test_load_excel_valide(tmp_path, raw_df):
    chemin = tmp_path / "clients.xlsx"
    raw_df.to_excel(chemin, index=False)
    df = load_file(chemin)
    assert df.shape == (5, 4)


def test_load_csv_separateur_point_virgule(tmp_path):
    chemin = tmp_path / "clients.csv"
    chemin.write_text("nom;email\nDiop;awa@gmail.com\nFall;moussa@gmail.com\n", encoding="utf-8")
    df = load_file(chemin)
    assert list(df.columns) == ["nom", "email"]
    assert len(df) == 2


def test_load_csv_une_seule_colonne(tmp_path):
    chemin = tmp_path / "emails.csv"
    chemin.write_text("email\nawa@gmail.com\nmoussa@gmail.com\n", encoding="utf-8")
    df = load_file(chemin)
    assert list(df.columns) == ["email"]
    assert len(df) == 2


def test_load_csv_separateur_tabulation(tmp_path):
    chemin = tmp_path / "clients.csv"
    chemin.write_text("nom\temail\nDiop\tawa@gmail.com\n", encoding="utf-8")
    assert list(load_file(chemin).columns) == ["nom", "email"]


def test_load_csv_enregistre_depuis_excel_cp1252(tmp_path):
    chemin = tmp_path / "clients.csv"
    chemin.write_bytes("nom;email\nCissé;cisse@gmail.com\nMbaye;marième@gmail.com\n".encode("cp1252"))
    df = load_file(chemin)
    assert df["nom"].iloc[0] == "Cissé"


def test_load_fichier_introuvable(tmp_path):
    with pytest.raises(FileNotFoundError, match="introuvable"):
        load_file(tmp_path / "absent.csv")


def test_load_format_non_supporte(tmp_path):
    chemin = tmp_path / "document.pdf"
    chemin.write_bytes(b"%PDF")
    with pytest.raises(ValueError, match="Format non supporté"):
        load_file(chemin)


def test_load_fichier_vide(tmp_path):
    chemin = tmp_path / "vide.csv"
    chemin.write_bytes(b"")
    with pytest.raises(ValueError, match="vide"):
        load_file(chemin)


def test_load_csv_en_tetes_seulement(tmp_path):
    chemin = tmp_path / "entetes.csv"
    chemin.write_text("nom,prenom,email\n", encoding="utf-8")
    with pytest.raises(ValueError, match="vide"):
        load_file(chemin)


def test_load_excel_corrompu(tmp_path):
    chemin = tmp_path / "faux.xlsx"
    chemin.write_text("ceci n'est pas un vrai fichier Excel", encoding="utf-8")
    with pytest.raises(ValueError, match="illisible"):
        load_file(chemin)


def test_load_extension_en_majuscules(tmp_path, raw_df):
    chemin = tmp_path / "CLIENTS.CSV"
    raw_df.to_csv(chemin, index=False)
    assert len(load_file(chemin)) == 5


# ---------- Nettoyage ----------
def test_nettoyage_espaces_debut_fin(raw_df):
    assert clean_dataframe(raw_df)["nom"].iloc[0] == "Diop"


def test_nettoyage_espaces_multiples():
    df = pd.DataFrame({"nom": ["Jean    Paul"], "prenom": ["x"]})
    assert clean_dataframe(df)["nom"].iloc[0] == "Jean Paul"


def test_nettoyage_format_titre(raw_df):
    df = clean_dataframe(raw_df)
    assert df["nom"].iloc[1] == "Fall"
    assert df["prenom"].iloc[1] == "Moussa"


def test_nettoyage_email_en_minuscules(raw_df):
    assert clean_dataframe(raw_df)["email"].iloc[2] == "fatou@gmail.com"


def test_nettoyage_chaine_vide_devient_champ_manquant():
    df = pd.DataFrame({"nom": ["   ", "Diop"], "email": ["", "a@b.com"]})
    propre = clean_dataframe(df)
    assert propre["nom"].isna().iloc[0]
    assert propre["email"].isna().iloc[0]


def test_nettoyage_noms_de_colonnes():
    df = pd.DataFrame({" NOM ": ["diop"], "Email": ["A@B.COM"]})
    propre = clean_dataframe(df)
    assert list(propre.columns) == ["nom", "email"]
    assert propre["email"].iloc[0] == "a@b.com"


def test_nettoyage_ne_modifie_pas_loriginal(raw_df):
    avant = raw_df.copy()
    clean_dataframe(raw_df)
    pd.testing.assert_frame_equal(raw_df, avant)


# ---------- Contrôle qualité ----------
def test_champs_manquants(raw_df):
    assert detect_missing(clean_dataframe(raw_df)) == {"nom": 1, "telephone": 1}


def test_doublons_detectes_apres_nettoyage(raw_df):
    masque = detect_duplicates(clean_dataframe(raw_df))
    assert int(masque.sum()) == 1
    assert bool(masque.iloc[3]) is True  # la 2e occurrence, pas la 1re


def test_emails_invalides(raw_df):
    masque = detect_invalid_emails(clean_dataframe(raw_df))
    assert masque.tolist() == [False, True, False, False, True]


def test_email_manquant_nest_pas_invalide():
    df = clean_dataframe(pd.DataFrame({"email": [None, "a@b.com"]}))
    assert detect_invalid_emails(df).tolist() == [False, False]


def test_colonne_email_absente():
    df = pd.DataFrame({"nom": ["Diop", "Fall"]})
    assert detect_invalid_emails(df).tolist() == [False, False]


@pytest.mark.parametrize("email", ["a@b.com", "awa.diop@gmail.com", "x_y+z@mail.orange.sn", "A1@b-c.fr"])
def test_regex_emails_valides(email):
    assert EMAIL_REGEX.match(email)


@pytest.mark.parametrize(
    "email", ["moussa@gmail", "omar@@gmail.com", "sans-arobase.com", "@gmail.com", "a b@gmail.com", "a@b.c", "a@.com"]
)
def test_regex_emails_invalides(email):
    assert not EMAIL_REGEX.match(email)


def test_quality_report(raw_df):
    bilan = quality_report(clean_dataframe(raw_df))
    assert bilan["lignes_total"] == 5
    assert bilan["nb_doublons"] == 1
    assert bilan["nb_emails_invalides"] == 2
    assert bilan["lignes_emails_invalides"] == [1, 4]
    assert bilan["champs_manquants"] == {"nom": 1, "telephone": 1}


# ---------- Suppression des doublons et export ----------
def test_remove_duplicates_garde_la_premiere(raw_df):
    df = remove_duplicates(clean_dataframe(raw_df))
    assert len(df) == 4
    assert df["prenom"].tolist() == ["Awa", "Moussa", "Fatou", "Omar"]


def test_export_cree_un_fichier_nettoye(tmp_path, raw_df):
    source = tmp_path / "clients.csv"
    chemin = export_dataframe(clean_dataframe(raw_df), source, tmp_path / "sortie")
    assert chemin.name == "clients_nettoye.xlsx"
    assert chemin.exists()
    assert len(pd.read_excel(chemin)) == 5


def test_export_necrase_jamais_un_fichier(tmp_path, raw_df):
    source = tmp_path / "clients.csv"
    df = clean_dataframe(raw_df)
    premier = export_dataframe(df, source, tmp_path / "sortie")
    deuxieme = export_dataframe(df, source, tmp_path / "sortie")
    assert premier != deuxieme
    assert deuxieme.name == "clients_nettoye_1.xlsx"
    assert premier.exists() and deuxieme.exists()