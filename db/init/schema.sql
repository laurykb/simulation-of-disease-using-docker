-- Table Patients : chaque patient est unique
CREATE TABLE IF NOT EXISTS patients (
  id SERIAL PRIMARY KEY,
  nom TEXT NOT NULL,
  prenom TEXT NOT NULL,
  dob DATE NOT NULL,        -- date de naissance
  statut TEXT NOT NULL,               -- Statut du dossier
  created_at TIMESTAMP DEFAULT NOW()
);

-- Table Telemetrie : mesures en temps réel
CREATE TABLE IF NOT EXISTS telemetrie (
  id BIGSERIAL PRIMARY KEY,
  patient_id INT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  ts TIMESTAMP NOT NULL DEFAULT NOW(),
  hr INT,                   -- heart rate
  temp NUMERIC(4,1)         -- température
);

-- Table Alertes : messages déclenchés par l’analyzer
CREATE TABLE IF NOT EXISTS alertes (
  id BIGSERIAL PRIMARY KEY,
  patient_id INT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  ts TIMESTAMP NOT NULL DEFAULT NOW(),
  type TEXT NOT NULL,       -- ex: tachycardie
  severity TEXT NOT NULL,   -- low|medium|high
  message TEXT NOT NULL
);

-- Indices pour accélérer les recherches par patient + date
CREATE INDEX IF NOT EXISTS idx_tel_patient_ts ON telemetrie (patient_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_alertes_patient_ts ON alertes (patient_id, ts DESC);

