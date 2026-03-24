#!/usr/bin/env bash
set -euo pipefail

PROJECT="${COMPOSE_PROJECT_NAME:-medicomtel}"
export COMPOSE_PROJECT_NAME="$PROJECT"

echo "→ Démarrage DB + API (scale api=3)…"
docker compose --profile core up -d --build --scale api=3 db api

echo "→ Nginx (reverse proxy)…"
docker compose --profile core --profile lb up -d nginx

echo "→ CLI interactif (créer un patient statut=cli), Ctrl+D pour terminer la session"
docker compose --profile core --profile cli run --rm --build cli

echo "→ Workers + Grafana…"
docker compose --profile core --profile workers --profile viz up -d --build analyzer simulator grafana

echo ""
echo "Terminé."
echo "  Grafana (admin / voir GRAFANA_ADMIN_PASSWORD) : http://localhost:8082"
echo "  API via Nginx : http://localhost:8081"
