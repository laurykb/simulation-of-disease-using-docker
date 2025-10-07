# CLI.py
import requests
import os 
API_URL = os.getenv("API_URL", "http://localhost:8081")

def creer_patient():
    print("\n=== Création d’un dossier patient ===")
    nom = input("Nom : ").strip()
    prenom = input("Prénom : ").strip()
    dob = input("Date de naissance (YYYY-MM-DD) : ").strip()
    statut = input("Statut (vide = cli) : ").strip() or "cli" # Par défaut "cli"
    print("\nType de patient :")
    print("1) normal")
    print("2) unstable (tachy/brady)")
    choix_type = input("Choix (1/2) : ").strip()
    type_patient = "unstable" if choix_type == "2" else "normal"

    data = {
        "nom": nom, 
        "prenom": prenom, 
        "dob": dob, 
        "statut": statut,
        "type_patient": type_patient
    }
    r = requests.post(f"{API_URL}/patient", json=data)
    if r.ok:
        print("Réponse API :", r.json())
    else:
        print("Erreur:", r.status_code, r.text)

def main():

    print("CLI version 2025-10-06 v3")
    while True:
        print("\n=== MediComTel CLI ===")
        print("1) Créer un dossier patient")
        print("2) Quitter")
        c = input("Choix : ").strip()
        if c == "1":
            creer_patient()
        elif c == "2":
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    main()