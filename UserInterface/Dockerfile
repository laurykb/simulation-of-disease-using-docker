#on déclare le python à utiliser
FROM python:3.12-slim

WORKDIR /app

# Installer les dépendances
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# Copier le code de l'application
COPY CLI.py .

# Définir la commande par défaut pour exécuter l'application
CMD ["python", "CLI.py"]