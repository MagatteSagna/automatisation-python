import pandas as pd

# Jeu de démonstration fictif : 20 lignes avec des erreurs volontaires
data = {
    "nom": [
        "diop", "FALL", " Ndiaye ", "Ndiaye", "Sow", "BA", "Gueye", "SARR", "Diallo", "  Thiam",
        "Cissé", "Ndoye", "FAYE", "Mbaye", "Seck", "Sy", "KANE", "Diouf", "Sagna", "Sagna",
    ],
    "prenom": [
        "Awa", "moussa", "Fatou", "Fatou", "CHEIKH", "Aminata", "Ibrahima", "Khady", "Mamadou", "Rokhaya",
        "Ousmane", "Astou", "Pape", "Marième", "Modou", "Bineta", "Lamine", "Coumba", "Maguette", "Maguette",
    ],
    "email": [
        "awa.diop@gmail.com", "moussa.fall@gmail", "Fatou.Ndiaye@Gmail.COM", "fatou.ndiaye@gmail.com",
        "cheikh.sow@yahoo.fr", None, "ibrahima.gueye@gmail.com", "khady.sarr@@gmail.com",
        "mamadou.diallo@orange.sn", "rokhaya.thiam@gmail.com", "ousmane.cisse@gmail.com", "astou.ndoye@gmail",
        "pape.faye@gmail.com", "marieme.mbaye@gmail.com", None, "bineta.sy@gmail.com",
        "lamine.kane@yahoo.fr", "coumba.diouf@gmail.com", "maguette.sagna@gmail.com", "maguette.sagna@gmail.com",
    ],
    "telephone": [
        "771234567", "770000000", "781112223", "781112223", None, "761234567", "771110000", "772223333",
        "773334444", None, "774445555", "775556666", "776667777", "777778888", None, "778889999",
        "779990000", "770001111", "771112222", "771112222",
    ],
}

df = pd.DataFrame(data)
df.to_excel("data/input/clients_demo.xlsx", index=False)
df.to_csv("data/input/clients_demo.csv", index=False)
print(f"Jeu de démonstration créé : {len(df)} lignes")