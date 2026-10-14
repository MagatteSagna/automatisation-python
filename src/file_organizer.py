import logging
import re
import shutil
from datetime import datetime
from pathlib import Path

from src.utils import unique_path

logger = logging.getLogger(__name__)

# Détecte un nom qui commence déjà par une date (AAAA-MM-JJ_)
DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}_")


def _normalize_stem(stem: str) -> str:
    """Nom en minuscules, espaces remplacés par des underscores."""
    return re.sub(r"\s+", "_", stem.strip().lower())


def organize_files(source_dir, dest_dir, mode="extension", rename=True, move=False) -> list:
    """Classe (et renomme) les fichiers d'un dossier.

    mode   : "extension" (un dossier par type) ou "date" (un dossier par mois AAAA-MM)
    rename : applique la convention AAAA-MM-JJ_nom_du_fichier.ext
    move   : False = copie (originaux intacts), True = déplacement
    Retourne la liste des opérations effectuées (pour le rapport).
    """
    source_dir = Path(source_dir)
    dest_dir = Path(dest_dir)

    if not source_dir.is_dir():
        logger.error("Dossier source introuvable : %s", source_dir)
        raise FileNotFoundError(f"Dossier source introuvable : {source_dir}")
    if mode not in ("extension", "date"):
        raise ValueError("Mode inconnu : utiliser 'extension' ou 'date'.")

    files = sorted(f for f in source_dir.iterdir() if f.is_file() and not f.name.startswith("."))
    if not files:
        logger.warning("Aucun fichier à classer dans %s", source_dir)
        raise ValueError("Le dossier ne contient aucun fichier à classer.")

    results = []
    for f in files:
        try:
            modified = datetime.fromtimestamp(f.stat().st_mtime)

            if mode == "extension":
                folder = f.suffix.lower().lstrip(".") or "sans_extension"
            else:
                folder = modified.strftime("%Y-%m")

            new_name = f.name
            if rename:
                stem = _normalize_stem(f.stem)
                if not DATE_PREFIX.match(stem):
                    stem = f"{modified.strftime('%Y-%m-%d')}_{stem}"
                new_name = f"{stem}{f.suffix.lower()}"

            target_dir = dest_dir / folder
            target_dir.mkdir(parents=True, exist_ok=True)
            target = unique_path(target_dir / new_name)  # évite les collisions de noms

            if move:
                shutil.move(str(f), str(target))
            else:
                shutil.copy2(f, target)

            logger.info("%s -> %s", f.name, target.relative_to(dest_dir))
            results.append({"source": f.name, "destination": str(target.relative_to(dest_dir)), "statut": "ok"})
        except Exception as e:
            logger.error("Échec pour %s : %s", f.name, e)
            results.append({"source": f.name, "destination": "", "statut": f"erreur : {e}"})

    return results