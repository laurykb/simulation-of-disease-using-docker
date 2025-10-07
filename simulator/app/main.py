import requests
import random
import time
import math
import os

# URL de base de ton API
API_BASE = os.getenv("API_BASE", "http://api:8000")
API_HEALTH = f"{API_BASE}/health"
API_PATIENTS = f"{API_BASE}/patients"
API_TELEMETRIE = f"{API_BASE}/telemetrie"

#fonction pour vérifier que l'API est prête
def wait_for_api(timeout=120):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            r = requests.get(API_HEALTH, timeout=2)
            if r.ok and r.json().get("status") == "up":
                print("API prête")
                return True
        except requests.RequestException:
            pass
        print("⏳ Attente API…")
        time.sleep(2)
    print("API non joignable")
    return False

def get_cli_patients():
    """Récupère les patients avec statut 'cli' depuis l'API"""
    try:
        r = requests.get(API_PATIENTS, timeout=5)
        r.raise_for_status()
        patients = r.json()
        cli_patients = [p for p in patients if p["statut"] == "cli"]
        print(f"{len(cli_patients)} patients CLI trouvés :", cli_patients)
        return cli_patients
    except Exception as e:
        print(f" Impossible de récupérer les patients :", e)
        return []


def generate_hr(patient_type, t):
    if patient_type == "normal":
        base = 85 + 5 * math.sin(t / 20)
        noise = random.uniform(-8, 8)
        return int(max(60, min(120, base + noise)))
    elif patient_type == "unstable":
        cycle_duration = 10
        total_cycle = int(t / cycle_duration) % 3
        if total_cycle == 0:
            return random.randint(75, 100)
        elif total_cycle == 1:
            return random.randint(185, 190)
        else:
            return random.randint(40, 45)
    return random.randint(70, 100)

def send_data():
    if not wait_for_api():
        return
    
    patients = get_cli_patients()
    if not patients:
        print("⚠️ Aucun patient 'cli'.")
        return

    print("Simulation active sur :", [p["id"] for p in patients])
    t0 = time.time()

    while True:
        t = time.time() - t0
        for p in patients:
            patient_type = p.get("type_patient", "normal")  # <-- récupère le type
            hr = generate_hr(patient_type, t)
            data = {
                "patient_id": p["id"],
                "hr": hr,
                "temp": round(random.uniform(36.0, 38.5), 1)
            }
            try:
                r = requests.post(API_TELEMETRIE, json=data, timeout=5)
                if r.status_code == 200:
                    print(f"{patient_type} #{p['id']} ({p['nom']}) : HR={hr}")
                else:
                    print(f"Erreur {r.status_code}: {r.text}")
            except Exception as e:
                print(f"⚠️ Patient {p['id']} : {e}")
        time.sleep(3)


if __name__ == "__main__":
    print("🚀 Simulator démarré…")
    send_data()