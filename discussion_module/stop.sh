#!/bin/bash

MODULE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$MODULE_DIR"

echo "Cleaning up containers and volumes..."
docker compose -f docker-compose.generated.yml down -v || true
echo "Containers and volumes removed successfully"
