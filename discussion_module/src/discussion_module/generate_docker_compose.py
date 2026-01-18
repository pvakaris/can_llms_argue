import yaml

from discussion_module.discussion_config import BASE_PORT, PARTICIPANTS

def generate_docker_compose(n):
    print(f"Generating docker-compose with {n} agents.")
    compose = {"services": {}}
    base_port = BASE_PORT
    for i in range(n):
        service_name = f"ollama{i+1}"
        compose["services"][service_name] = {
            "image": "ollama/ollama:latest",
            "container_name": f"ollama{i+1}",
            "restart": "unless-stopped",
            "ports": [f"{base_port + i}:11434"],
            "volumes": ["ollama_shared:/root/.ollama/models", f"ollama{i+1}_data:/root/.ollama"],
        }
    compose["volumes"] = {"ollama_shared": {}}
    for i in range(n):
        compose["volumes"][f"ollama{i+1}_data"] = {}
    with open("docker-compose.generated.yml", "w") as f:
        yaml.dump(compose, f, sort_keys=False)
    print(f"Generated docker-compose.generated.yml with {n} agents.")

def main():
    generate_docker_compose(PARTICIPANTS)

if __name__ == "__main__":
    main()
