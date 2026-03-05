
# Ce Document explique l'avancée du projet Medicomtel

**Composants**

Postgres (db):
Base de données relationnelle (3 tables : patients, telemetrie, alertes).
Initialisée avec un script SQL dans db/init/.

FastAPI (api):
Backend exposant une API REST simple pour gérer :

/patient : ajout de patients

/telemetrie : envoi de mesures de télémétrie

/alertes : ajout manuel d’alertes

/health : endpoint de santé

Grafana (grafana):
Dashboard connecté à Postgres pour :

afficher l’évolution du rythme cardiaque des patients
visualiser les dossiers "pending" des clients
Afficher les alertes depuis la database


Simulator (simulator):
Script Python qui génère des données fictives de télémétrie (hr + temp) et les envoie périodiquement à l’API.

Analyseur : Analyse la table "télémétrie" de la database pour détecter des alertes et les ajouter a la table "alertes" via l'api.


**Démarage**

*sudo docker compose up -d* depuis le dossier Medicomtel ajouter *--build* pour build l'image la premiere fois

Le volume de la database est persistant, il faut penser à le supprimer pour reinitialiser la base si besoin.

**Usage de l'API**
ATTENTION CHANGER "localhost" par "api" et "8080" par "8000" si vous faites l'appel depuis un conteneur

Vérifier l'êtat de santé de l'api : 
curl http://localhost:8080/health 

Ajouter un patient:
curl -X POST http://localhost:8080/patient \
  -H "Content-Type: application/json" \
  -d '{"nom":"Dupont","prenom":"Alice","dob":"1990-04-12","statut":"active"}'

Ajouter une donnée télémetrique:
curl -X POST http://localhost:8080/telemetrie \
  -H "Content-Type: application/json" \
  -d '{"patient_id":1,"hr":80,"temp":37.1}'

Ajouter une alerte:
curl -X POST http://localhost:8080/alertes \
  -H "Content-Type: application/json" \
  -d '{"patient_id":1,"type":"tachycardie","severity":"high","message":"HR=180 bpm"}'




**Base de donnée**

Pour accéder au contenu, voir avec psql en se connectant au conteneur ou sinon par grafana c'est plus simple une fois que la base de donnée est connectée.



**Grafana**

Y acceder par http://Localhost:8081

A la premiere connexion ajouter une datasource : Postgres ; db:4321 ; db_test ; admin; admin; refresh time = 2sec ; 

et importer les dashboards dans le sous dossier "grafana" avec la fonction d'import dans la categorie dashboard.

