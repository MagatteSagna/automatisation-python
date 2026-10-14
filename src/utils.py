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