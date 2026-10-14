import logging

from src.data_cleaning import load_file, clean_dataframe, remove_duplicates, export_dataframe
from src.file_organizer import organize_files

logging.basicConfig(level=logging.INFO)

# 1) Export du fichier nettoyé
source = "data/input/clients_test.csv"
df = load_file(source)
df = remove_duplicates(clean_dataframe(df))
print("Fichier exporté :", export_dataframe(df, source))

# 2) Classement par extension, puis par date
for mode in ("extension", "date"):
    print(f"\n--- Classement par {mode} ---")
    for op in organize_files("data/input/fichiers_a_classer", f"data/output/classes_par_{mode}", mode=mode):
        print(op["source"], "->", op["destination"], f"[{op['statut']}]")