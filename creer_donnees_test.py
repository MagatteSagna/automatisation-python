import pandas as pd

data = {
    "nom": ["  diop ", "FALL", "Ndiaye", "Ndiaye", "Sow", "Ba", None],
    "prenom": ["Awa", "moussa", "Fatou", "Fatou", "  Cheikh", "Aminata", "Omar"],
    "email": [
        "awa.diop@gmail.com",
        "moussa.fall@gmail",       # invalide : pas de .com
        "Fatou@GMail.COM",
        "Fatou@GMail.COM",         # doublon
        "cheikh.sow@gmail.com",
        None,                     # manquant
        "omar@@gmail.com",         # invalide
    ],
    "telephone": ["771234567", "770000000", "781112223", "781112223", None, "761234567", "770001111"],
}

df = pd.DataFrame(data)
df.to_csv("data/input/clients_test.csv", index=False)
df.to_excel("data/input/clients_test.xlsx", index=False)
print("Fichiers de test créés.")