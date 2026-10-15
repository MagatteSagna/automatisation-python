import logging
import tempfile
import time
from pathlib import Path

from src.data_cleaning import (
    clean_dataframe, export_dataframe, load_file, quality_report, remove_duplicates,
)
from src.file_organizer import organize_files
from src.reports import build_cleaning_report, build_organizing_report, save_report

logger = logging.getLogger(__name__)


def clean_file(path, output_dir="data/output") -> dict:
    """Chaîne complète : lecture, nettoyage, contrôle, export, rapport. Retourne le rapport."""
    start = time.perf_counter()
    logger.info("=== Nettoyage de %s ===", path)
    try:
        df = clean_dataframe(load_file(path))
        quality = quality_report(df)
        df = remove_duplicates(df)
        exported = export_dataframe(df, path, output_dir)
    except Exception as e:
        logger.error("Traitement interrompu : %s", e)
        raise

    report = build_cleaning_report(path, quality, len(df), [exported], time.perf_counter() - start)
    report_path = save_report(report, output_dir)
    logger.info("=== Terminé en %.2f s, rapport : %s ===", report["duree_secondes"], report_path)
    return report


def organize_folder(source_dir, dest_dir="data/output/classes", mode="extension", move=False) -> dict:
    """Chaîne complète de classement d'un dossier. Retourne le rapport."""
    start = time.perf_counter()
    logger.info("=== Classement de %s (mode %s) ===", source_dir, mode)
    try:
        results = organize_files(source_dir, dest_dir, mode=mode, move=move)
    except Exception as e:
        logger.error("Classement interrompu : %s", e)
        raise

    report = build_organizing_report(source_dir, results, mode, time.perf_counter() - start)
    report_path = save_report(report, dest_dir)
    logger.info("=== Terminé en %.2f s, rapport : %s ===", report["duree_secondes"], report_path)
    return report

def clean_upload(filename, content: bytes, output_dir="data/output") -> dict:
    """Nettoie un fichier reçu sous forme d'octets (cas de l'interface web). Retourne le rapport."""
    name = Path(filename).name  # garde seulement le nom, jamais un chemin
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        path.write_bytes(content)
        return clean_file(path, output_dir)