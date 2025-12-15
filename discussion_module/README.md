
# Multi-Agent LLM Orchestrator

## About

This project is a simple multi-agent LLM system where multiple Ollama servers are deployed as containers. Each of them run separate language models and behave as participants in a discussion coordinated by the orchestrator.
The orchestrator distributes a question to the agents, lets them discuss in multiple turns, and saves the conversation to text and JSON files for later analysis.

---

## How to Run Locally

### Requirements

- Docker Desktop
- Python 3.9

### Quick Start

```bash
# Start the dockerized network of LLM participants
./start.sh

# Then run the discussion managed by the orchestrator separately
python -m discussion_module.orchestrator

# Deconstruct the dockerized network
./stop.sh
```

This way the network is launched first and then as many discussions as wanted can be run sequentially without having to reboot the network. However, make sure to turn off the network afterward.

Alternatively, you can use the `auto-launch` function that boots-up the dockerized network, runs a single discussion, saves the results and then deconstructs the Docker network in one command:

```bash
./start.sh auto-launch
```

### Additional information

By default, port numbers begin at 11434 and rise depending on the number of model containers.

For instance, to check what models are installed on any of the models, we can simply query them using CURL. For the first model that would look like this:

    curl -s http://localhost:11434/v1/models

Note that the containers use the same shared storage to store their model instances. This saves time and memory, since the model has to be downloaded only once with no regard to how many containers will use its instance in the future. However, the data of each container is stored separately because they behave as separate unrelated entities.

All the configuration params in `src/discussion_module/discussion_config.py` can be overridden in an .env file. Create one in the root directory of the module (where this README.md is located).