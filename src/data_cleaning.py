import logging
import re #permet de rechercher des motifs dans du texte par exemple pour ici le format de l'email
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Modèle d'un e-mail valide : texte@domaine.extension
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")


def load_file(path) -> pd.DataFrame:
    """Charge un fichier CSV ou Excel et vérifie qu'il est lisible."""
    path = Path(path)

    if not path.exists():
        logger.error("Fichier introuvable : %s", path)
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    extension = path.suffix.lower()
    if extension not in (".csv", ".xlsx"):
        logger.error("Format non supporté : %s", extension)
        raise ValueError(f"Format non supporté : {extension} (utiliser .csv ou .xlsx)")

    if path.stat().st_size == 0:
        logger.error("Le fichier %s est vide", path)
        raise ValueError("Le fichier est vide.")

    try:
        # dtype=str : tout est lu comme du texte (les téléphones gardent leurs zéros)
        if extension == ".csv":
            # sep=None : pandas devine le séparateur (, ou ;)
            df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig", dtype=str)
        else:
            df = pd.read_excel(path, engine="openpyxl", dtype=str)
    except Exception as e:
        logger.error("Impossible de lire %s : %s", path, e)
        raise ValueError(f"Fichier illisible ou corrompu : {e}")

    if df.empty:
        logger.error("Le fichier %s est vide", path)
        raise ValueError("Le fichier est vide.")

    logger.info("Fichier chargé : %s (%d lignes, %d colonnes)", path.name, len(df), len(df.columns))
    return df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Applique les règles de nettoyage. Retourne une COPIE (l'original reste intact)."""
    df = df.copy()

    # Noms de colonnes : sans espaces, en minuscules
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Colonnes texte : espaces en trop, cellules vides
    for col in df.columns:
        if df[col].dtype == "object" or pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].astype("string").str.strip()
            df[col] = df[col].str.replace(r"\s+", " ", regex=True)
            df[col] = df[col].replace("", pd.NA)

    # Règles spécifiques
    if "email" in df.columns:
        df["email"] = df["email"].str.lower()
    for col in ("nom", "prenom"):
        if col in df.columns:
            df[col] = df[col].str.title()

    logger.info("Nettoyage terminé")
    return df


def detect_missing(df: pd.DataFrame) -> dict:
    """Compte les champs (cellules) manquants par colonne."""
    missing = df.isna().sum()
    return {col: int(n) for col, n in missing.items() if n > 0}


def detect_duplicates(df: pd.DataFrame) -> pd.Series:
    """Retourne un masque True pour chaque ligne en doublon (la 1re occurrence est gardée)."""
    return df.duplicated(keep="first")


def detect_invalid_emails(df: pd.DataFrame) -> pd.Series:
    """Retourne un masque True pour chaque e-mail renseigné mais invalide."""
    if "email" not in df.columns:
        logger.warning("Colonne 'email' absente : contrôle des e-mails ignoré")
        return pd.Series(False, index=df.index)

    valid = df["email"].str.match(EMAIL_REGEX).fillna(False).astype(bool)
    return df["email"].notna() & ~valid


def quality_report(df: pd.DataFrame) -> dict:
    """Bilan de qualité des données."""
    duplicates = detect_duplicates(df)
    invalid = detect_invalid_emails(df)
    report = {
        "lignes_total": len(df),
        "champs_manquants": detect_missing(df),
        "nb_doublons": int(duplicates.sum()),
        "nb_emails_invalides": int(invalid.sum()),
        "lignes_emails_invalides": df.index[invalid].tolist(),
    }
    logger.info("Bilan qualité : %s", report)
    return report