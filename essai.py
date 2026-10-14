import logging

from src.data_cleaning import load_file, clean_dataframe, quality_report

logging.basicConfig(level=logging.INFO)

df = load_file("data/input/clients_test.csv")
print("--- AVANT ---")
print(df)

df_propre = clean_dataframe(df)
print("--- APRÈS ---")
print(df_propre)

print("--- BILAN ---")
print(quality_report(df_propre))