#runtime python à utiliser
FROM python:3.12-slim

# éviter les logs bufferisés
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installer curl pour les vérifications de santé
RUN apt-get update && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

COPY app /app/app

# lancer FastAPI via Uvicorn
#on lance l'application avec 4 processus python qui écoutent tous sur le même port
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
