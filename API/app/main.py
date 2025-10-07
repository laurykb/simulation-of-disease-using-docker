import os
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, date

# -------- Connexion à la DB --------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@db:5432/base_test")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# -------- App FastAPI --------
app = FastAPI(title="MediComTel API (simple version)")

# -------- Schémas d’entrée ----------
class PatientIn(BaseModel):
    nom: str
    prenom: str
    dob: date
    statut: str | None = None
    type_patient: str | None = "normal"

class TelemetrieIn(BaseModel):
    patient_id: int
    ts: datetime = Field(default_factory=datetime.utcnow)
    hr: int | None = None
    spo2: int | None = None
    temp: float | None = None

class AlerteIn(BaseModel):
    patient_id: int
    type: str
    severity: str
    message: str
    ts: datetime = Field(default_factory=datetime.utcnow)

# -------- Endpoints ----------
@app.post("/patient")
def create_patient(payload: PatientIn):
    sql = """
    INSERT INTO patients (nom, prenom, dob, statut, type_patient)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (payload.nom, payload.prenom, payload.dob, payload.statut, payload.type_patient))
            new_id = cur.fetchone()[0]
            conn.commit()
    return {"id": new_id, "status": "created"}

@app.post("/telemetrie")
def add_telemetry(payload: TelemetrieIn):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM patients WHERE id = %s", (payload.patient_id,))
            if cur.fetchone() is None:
                raise HTTPException(400, "Unknown patient_id")

            cur.execute(
                "INSERT INTO telemetrie (patient_id, ts, hr, temp) VALUES (%s, %s, %s, %s)",
                (payload.patient_id, payload.ts, payload.hr, payload.temp)
            )
            conn.commit()
    return {"status": "ok"}

@app.post("/alertes")
def add_alert(payload: AlerteIn):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM patients WHERE id = %s", (payload.patient_id,))
            if cur.fetchone() is None:
                raise HTTPException(400, "Unknown patient_id")

            cur.execute(
                "INSERT INTO alertes (patient_id, ts, type, severity, message) VALUES (%s, %s, %s, %s, %s)",
                (payload.patient_id, payload.ts, payload.type, payload.severity, payload.message)
            )
            conn.commit()
    return {"status": "ok"}

@app.get("/health")
def health():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return {"status": "up"}
    except Exception as e:
        return {"status": "down", "error": str(e)}

#on liste les patients présents dans la base
@app.get("/patients")
def list_patients():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nom, prenom, statut, type_patient FROM patients;")
            rows = cur.fetchall()
            patients = [
                {"id": r[0], "nom": r[1], "prenom": r[2], "statut": r[3], "type_patient": r[4]}
                for r in rows
            ]
    return patients