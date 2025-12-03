import argparse
from langchain_ollama import OllamaLLM
import requests
import time

def pull_model_on_all(ports, model="llama3"):
    for port in ports:
        print(f"Pulling model on Agent at port {port} ...")
        r = requests.post(f"http://localhost:{port}/api/pull", json={"name": model})

        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to pull model on port {port}: {r.text}"
            ) from e

        print(f"Agent {port} acknowledged model pull.")


def wait_for_agents(ports, timeout=300):
    start_time = time.time()
    while True:
        all_ready = True
        for port in ports:
            try:
                r = requests.get(f"http://localhost:{port}/api/tags", timeout=3)
                if r.status_code != 200:
                    all_ready = False
                    break
            except Exception:
                all_ready = False
                break
        if all_ready:
            print("All agents are ready.")
            return
        if time.time() - start_time > timeout:
            raise TimeoutError("Timed out waiting for agents.")
        time.sleep(2)

class LLMContainerAgent:
    def __init__(self, name, model, base_url):
        self.name = name
        self.llm = OllamaLLM(base_url=base_url, model=model)

    def respond(self, message):
        response = self.llm.invoke(message)
        return response

def run_discussion(agents, question, turns=5):
    print(f"=== Starting discussion on: {question} ===")
    message = question
    for i in range(turns):
        agent = agents[i % len(agents)]
        response = agent.respond(message)
        print(f"\n[{agent.name}]: {response}")
        message = response
    print("\n=== Discussion ended ===")

def main(n, question):
    agents = []
    ports = []
    base_port = 11434
    for i in range(n):
        port = base_port + i
        agents.append(LLMContainerAgent(
            name=f"Agent_{i+1}",
            model="llama3",
            base_url=f"http://localhost:{port}"
        ))
        ports.append(port)

    wait_for_agents(ports)
    pull_model_on_all(ports)
    run_discussion(agents, question)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--question", type=str, required=True)
    args = parser.parse_args()
    main(args.n, args.question)
