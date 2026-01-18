#!/bin/bash

set -e

MODULE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$MODULE_DIR"

# Default model is gemma3 the same as in discussion_config.py. Override in .env
MODEL="${MODEL:-gemma3}"

AUTO_LAUNCH=false
if [ "$1" == "auto-launch" ]; then
    AUTO_LAUNCH=true
fi

function cleanup {
    echo "An error occurred. Cleaning up containers and volumes..."
    docker compose -f docker-compose.generated.yml down -v || true
    exit 1
}

trap cleanup ERR

echo "Checking if Docker is running..."

if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running, starting Docker Desktop..."
    open -a Docker
    echo "Waiting for Docker to start..."
    while ! docker info > /dev/null 2>&1; do
        sleep 1
    done
    echo "Docker is now running"
else
    echo "Docker is already running"
fi

echo "Installing Python dependencies"
pip install .

python -m discussion_module.generate_docker_compose

echo "Deploying containers"
docker compose -f docker-compose.generated.yml up -d

echo "Pulling the model: $MODEL"
docker exec ollama1 ollama pull "$MODEL"

echo "Setup finished successfully"

if [ "$AUTO_LAUNCH" = true ]; then
    echo "Auto-launch is enabled. Launching the discussion module..."
    python -m discussion_module.orchestrator
    echo "Deconstructing the Docker network and removing the volumes"
    docker compose -f docker-compose.generated.yml down -v || true
fi
