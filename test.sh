#!/usr/bin/env bash
set -e

echo " Démarrage DB + API…"
# On scale l'API : on lance 3 conteneurs issus de la même image
docker compose -p medicomtel --profile core up -d --scale api=3 db api

#on démarre nginx
docker compose --profile core --profile lb up -d nginx

echo "Lance le CLI (remplis /patient), Ctrl+D pour quitter"
docker compose --profile cli up -d --build
docker compose --profile core --profile cli run --rm cli

echo "▶️  Démarrage des workers + Grafana…"
docker compose --profile core --profile workers --profile viz up -d --build analyzer simulator grafana

echo "Tout est lancé !"
echo "Grafana : http://localhost:8082"
echo "API (via Nginx LB) : http://localhost:8081"