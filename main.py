import argparse
import sys

from src.pipeline import clean_file, organize_folder
from src.reports import format_report
from src.utils import setup_logging


def main():
    parser = argparse.ArgumentParser(description="Outil d'automatisation des tâches administratives")
    sub = parser.add_subparsers(dest="commande", required=True)

    p1 = sub.add_parser("nettoyer", help="Nettoyer un fichier .csv ou .xlsx")
    p1.add_argument("fichier")
    p1.add_argument("--sortie", default="data/output", help="Dossier de sortie")

    p2 = sub.add_parser("classer", help="Classer et renommer les fichiers d'un dossier")
    p2.add_argument("dossier")
    p2.add_argument("--mode", choices=["extension", "date"], default="extension")
    p2.add_argument("--sortie", default="data/output/classes", help="Dossier de destination")
    p2.add_argument("--deplacer", action="store_true", help="Déplacer au lieu de copier")

    args = parser.parse_args()
    log_file = setup_logging()

    try:
        if args.commande == "nettoyer":
            report = clean_file(args.fichier, args.sortie)
        else:
            report = organize_folder(args.dossier, args.sortie, args.mode, args.deplacer)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERREUR : {e}")
        print(f"Détails dans le journal : {log_file}")
        sys.exit(1)

    print(format_report(report))


if __name__ == "__main__":
    main()