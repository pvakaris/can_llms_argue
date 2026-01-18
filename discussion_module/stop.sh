#!/bin/bash

MODULE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$MODULE_DIR" || exit 1

if [[ "$1" == "delete" ]]; then
    echo "Deleting containers and volumes..."
    docker compose -f docker-compose.generated.yml down -v || true
    echo "Containers and volumes removed successfully"
else
    echo "Stopping containers (no deletion)..."
    docker compose -f docker-compose.generated.yml stop || true
    echo "Containers stopped successfully"
fi
