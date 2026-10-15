import logging
from pathlib import Path


def unique_path(path) -> Path:
    """Retourne un chemin libre : ajoute _1, _2... si le fichier existe déjà (jamais d'écrasement)."""
    path = Path(path)
    if not path.exists():
        return path
    i = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{i}{path.suffix}")
        if not candidate.exists():
            return candidate
        i += 1

_logging_ready = False


def setup_logging(log_dir="logs", level=logging.INFO) -> Path:
    """Branche le journal sur logs/automatisation.log (appel sans danger plusieurs fois)."""
    global _logging_ready
    log_file = Path(log_dir) / "automatisation.log"
    if _logging_ready:
        return log_file

    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
    _logging_ready = True
    return log_file