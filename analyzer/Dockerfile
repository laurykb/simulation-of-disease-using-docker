#runtime python à utiliser
FROM python:3.12-slim

WORKDIR /app

# Installer dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier ton code Python
COPY app/ /app/

# Lancer ton script
CMD ["python", "main.py"]
