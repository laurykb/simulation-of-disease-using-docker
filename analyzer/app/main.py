# analyzer/main.py
import os
import time
import logging
from datetime import datetime, timedelta, timezone

import psycopg2
import psycopg2.extras
import requests

# --- Config ---
DB_NAME = os.getenv("DB_NAME", "base_test")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "admin")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

API_URL = os.getenv("API_URL", "http://api:8000/alertes")  # FastAPI /alertes
LOOKBACK_SECONDS = int(os.getenv("LOOKBACK_SECONDS", "15"))  # fenêtre d'analyse
SLEEP_SECONDS = float(os.getenv("SLEEP_SECONDS", "2"))       # intervalle de scan

# --- Logs non-bufferisés (voir tout de suite dans docker logs) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ [analyzer] %(levelname)s: %(message)s",
)
logging.Formatter.converter = time.gmtime
log = logging.getLogger("analyzer")

# garde le dernier ts traité par patient pour éviter les doublons
last_ts_by_patient: dict[int, datetime] = {}

def get_conn():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
        connect_timeout=5,
    )

def wait_for_db(timeout=120):
    """Attend que la DB réponde avant de démarrer la boucle principale."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute("SELECT 1")
                log.info("✅ DB prête")
                return True
        except Exception as e:
            log.warning("⏳ DB pas prête (%s), on réessaie…", e)
            time.sleep(2)
    log.error(" DB non joignable après %ss", timeout)
    return False

def fetch_recent_rows():
    """Récupère les mesures récentes (évite TOP 10 statique)."""
    since = datetime.now(timezone.utc) - timedelta(seconds=LOOKBACK_SECONDS)
    sql = """
        SELECT id, patient_id, ts, hr, temp
        FROM telemetrie
        WHERE ts > %s
        ORDER BY ts ASC
    """
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql, (since,))
        rows = cur.fetchall()
        return rows

def send_alert(patient_id: int, alert_type: str, severity: str, message: str, ts: datetime):
    payload = {
        "patient_id": patient_id,
        "type": alert_type,
        "severity": severity,
        "message": message,
        "ts": ts.isoformat(),
    }
    try:
        r = requests.post(API_URL, json=payload, timeout=5)
        log.info("[ALERTE] pid=%s %s/%s %s → status=%s",
                 patient_id, alert_type, severity, message, r.status_code)
    except Exception as e:
        log.error("[ERROR] POST /alertes échoué: %s", e)

def process_rows(rows):
    """Dédup + génération d’alertes sur nouvelles mesures uniquement."""
    count = 0
    for row in rows:
        pid = int(row["patient_id"])
        ts  = row["ts"] if isinstance(row["ts"], datetime) else datetime.fromisoformat(row["ts"])
        hr  = row["hr"]

        # dédup : ne traite pas un ts déjà vu pour ce patient
        last_ts = last_ts_by_patient.get(pid)
        if last_ts is not None and ts <= last_ts:
            continue
        last_ts_by_patient[pid] = ts

        if hr is None:
            continue

        if hr > 180:
            send_alert(pid, "tachycardie", "high", f"HR={hr} bpm détecté", ts)
            count += 1
        elif hr < 50:
            send_alert(pid, "bradycardie", "high", f"HR={hr} bpm détecté", ts)
            count += 1
    return count

def main_loop():
    if not wait_for_db():
        return
    log.info("🩺 Analyzer started (lookback=%ss, period=%ss)", LOOKBACK_SECONDS, SLEEP_SECONDS)

    while True:
        try:
            rows = fetch_recent_rows()
            if rows:
                alerted = process_rows(rows)
                log.debug("Scan: %s lignes lues, %s alertes envoyées", len(rows), alerted)
            time.sleep(SLEEP_SECONDS)
        except Exception as e:
            # On log et on continue (évite de crasher)
            log.exception("Boucle analyzer: exception: %s", e)
            time.sleep(2)

if __name__ == "__main__":
    main_loop()