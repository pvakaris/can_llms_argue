#!/bin/bash
echo "Cleaning up containers and volumes..."
docker compose -f docker-compose.generated.yml down -v || true
echo "Containers and volumes removed successfully"
