
# Multi-Agent LLM Orchestrator

## About

This project is a simple multi-agent LLM system where multiple Ollama servers (e.g., Llama 3 instances) are deployed as containers. Each of them behave as separate language models and participate in a discussion coordinated by the orchestrator.
The orchestrator distributes a question to the agents, lets them discuss in multiple turns, and saves the conversation to a text file for later analysis.

---

## How to Run Locally

### Requirements

- Docker Desktop
- Python 3.9

### Quick Start

```bash
# Run the orchestrator with desired number of agents and a question
./start.sh <number_of_agents> <ollama_model>

# Example:
./start.sh 3 gemma3
```

### Additional information

The port numbers begin at 11434 and rise depending on the number of model containers.

For instance, to check what models are installed on any of the models, we can simply query them using CURL. For the first model that would look like this:

    curl -s http://localhost:11434/v1/models

Note that the containers use the same shared storage to store their model instances. This saves time and memory, since the model has to be downloaded only once with no regard to how many containers will use its instance in the future. However, the data of each container is stored separately because they behave as separate unrelated entities.