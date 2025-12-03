#!/bin/bash

set -e

N=$1
MODEL=$2

if [ -z "$N" ] || [ -z "MODEL" ]; then
    echo "Usage: ./run.sh <number_of_agents> <ollama model>"
    exit 1
fi

function cleanup {
    echo "An error occurred. Cleaning up containers..."
    docker compose -f docker-compose.generated.yml down || true
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

echo "Generating docker-compose file with $N agents"
python3 -m discussion_module.generate_docker_compose $N

echo "Deploying containers"
docker compose -f docker-compose.generated.yml up -d

echo "Pulling the specified model"
docker exec ollama1 ollama pull $MODEL

#echo "Starting the discussion framework on the question: $QUESTION"
#python3 orchestrator.py
#
#docker-compose -f docker-compose.generated.yml down

echo "Setup finished successfully"
