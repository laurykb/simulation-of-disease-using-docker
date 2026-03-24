-- MediComTel — schéma initial (réinitialiser le volume db_data si vous changez ce fichier après coup)

CREATE TABLE IF NOT EXISTS patients (
  id SERIAL PRIMARY KEY,
  nom TEXT NOT NULL,
  prenom TEXT NOT NULL,
  dob DATE NOT NULL,
  statut TEXT NOT NULL DEFAULT 'cli',
  type_patient TEXT NOT NULL DEFAULT 'normal',
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS telemetrie (
  id BIGSERIAL PRIMARY KEY,
  patient_id INT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  ts TIMESTAMP NOT NULL DEFAULT NOW(),
  hr INT,
  spo2 INT,
  temp NUMERIC(4,1)
);

CREATE TABLE IF NOT EXISTS alertes (
  id BIGSERIAL PRIMARY KEY,
  patient_id INT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  ts TIMESTAMP NOT NULL DEFAULT NOW(),
  type TEXT NOT NULL,
  severity TEXT NOT NULL,
  message TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tel_patient_ts ON telemetrie (patient_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_alertes_patient_ts ON alertes (patient_id, ts DESC);
