from datetime import datetime
from pathlib import Path

from src.utils import unique_path


def build_cleaning_report(source, quality: dict, rows_exported: int, generated_files: list, duration: float) -> dict:
    """Rapport d'un nettoyage de fichier de données."""
    source = Path(source)
    return {
        "type": "nettoyage",
        "nom_base": source.stem,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fichier_source": source.name,
        "lignes_lues": quality["lignes_total"],
        "lignes_exportees": rows_exported,
        "doublons_supprimes": quality["nb_doublons"],
        "champs_manquants": quality["champs_manquants"],
        "emails_invalides": quality["nb_emails_invalides"],
        # +2 : numéro de ligne tel qu'on le voit dans Excel (ligne 1 = en-têtes)
        "lignes_emails_invalides": [i + 2 for i in quality["lignes_emails_invalides"]],
        "fichiers_generes": [str(p) for p in generated_files],
        "duree_secondes": round(duration, 2),
    }


def build_organizing_report(source_dir, results: list, mode: str, duration: float) -> dict:
    """Rapport d'un classement de fichiers (results vient de organize_files)."""
    source_dir = Path(source_dir)
    ok = [r for r in results if r["statut"] == "ok"]
    errors = [r for r in results if r["statut"] != "ok"]
    return {
        "type": "classement",
        "nom_base": source_dir.name,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dossier_source": str(source_dir),
        "mode": mode,
        "fichiers_traites": len(results),
        "fichiers_classes": len(ok),
        "erreurs": [f"{r['source']} : {r['statut']}" for r in errors],
        "fichiers_generes": [r["destination"] for r in ok],
        "duree_secondes": round(duration, 2),
    }


def format_report(report: dict) -> str:
    """Met le rapport en texte lisible."""
    lines = ["=== RAPPORT DE TRAITEMENT ===", f"Date : {report['date']}"]

    if report["type"] == "nettoyage":
        lines += [
            f"Fichier source : {report['fichier_source']}",
            f"Lignes lues : {report['lignes_lues']}",
            f"Lignes exportées : {report['lignes_exportees']}",
            f"Doublons supprimés : {report['doublons_supprimes']}",
        ]
        missing = report["champs_manquants"]
        if missing:
            detail = ", ".join(f"{col} : {n}" for col, n in missing.items())
            lines.append(f"Champs manquants : {sum(missing.values())} ({detail})")
        else:
            lines.append("Champs manquants : 0")
        lines.append(f"E-mails invalides : {report['emails_invalides']}")
        if report["lignes_emails_invalides"]:
            lignes = ", ".join(str(n) for n in report["lignes_emails_invalides"])
            lines.append(f"  (lignes Excel : {lignes})")
    else:
        lines += [
            f"Dossier source : {report['dossier_source']}",
            f"Mode de classement : {report['mode']}",
            f"Fichiers traités : {report['fichiers_traites']}",
            f"Fichiers classés : {report['fichiers_classes']}",
            f"Erreurs : {len(report['erreurs'])}",
        ]
        lines += [f"  - {e}" for e in report["erreurs"]]

    lines.append("Fichiers générés :")
    lines += [f"  - {f}" for f in report["fichiers_generes"]] or ["  (aucun)"]
    lines.append(f"Durée du traitement : {report['duree_secondes']} s")
    return "\n".join(lines)


def save_report(report: dict, output_dir="data/output") -> Path:
    """Enregistre le rapport en .txt (sans écraser) et l'ajoute à la liste des fichiers générés."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    target = unique_path(output_dir / f"{report['nom_base']}_rapport.txt")
    report["fichiers_generes"].append(str(target))
    target.write_text(format_report(report), encoding="utf-8")
    return target