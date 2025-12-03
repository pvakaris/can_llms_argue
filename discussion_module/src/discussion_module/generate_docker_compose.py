import sys
import yaml

def generate_docker_compose(n):
    compose = {"services": {}}
    base_port = 11434
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
    if len(sys.argv) != 2:
        print("Usage: python generate_docker_compose.py <n>")
        sys.exit(1)
    n = int(sys.argv[1])
    generate_docker_compose(n)

if __name__ == "__main__":
    main()
