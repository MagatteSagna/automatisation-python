import os
from datetime import datetime
from pathlib import Path

dossier = Path("data/input/fichiers_a_classer")
dossier.mkdir(parents=True, exist_ok=True)

# (nom du fichier, date de dernière modification)
fichiers = [
    ("Liste Clients.xlsx", "2026-09-12"),
    ("liste_clients.xlsx", "2026-09-12"),   # même nom une fois renommé : test de collision
    ("rapport.pdf", "2026-09-30"),
    ("notes.txt", "2026-10-02"),
    ("Photo Equipe.PNG", "2026-10-10"),
    ("LISEZMOI", "2026-10-14"),             # fichier sans extension
]

for nom, date in fichiers:
    chemin = dossier / nom
    chemin.write_text(f"Contenu fictif de {nom}", encoding="utf-8")
    ts = datetime.strptime(date, "%Y-%m-%d").timestamp()
    os.utime(chemin, (ts, ts))

print(f"{len(fichiers)} fichiers créés dans {dossier}")