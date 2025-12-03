# The Oracle

This subproject contains code for running oracle models and also running tests on the oracle outputs

---
## Setup

1. **Create a virtual environment**

       python -m venv .venv

2. **Activate the virtual environment**
   - macOS / Linux:
   
         source .venv/bin/activate

3. **Install dependencies**
   - First, install the `shared` package (required by the oracle):

         pip install ../shared

   - Then, install the `oracle` package:

         pip install .
---

## How to run

### Run the Graph Comparison Tool

    python -m oracle test

This runs the `oracle.test.graph_comparison` tool to perform graph comparisons on graphs inside of a directory referenced
by `oracle.test.test_config.RESOURCES_DIR`. It will compare pairs of .json files of AIF format.

### Run the Oracle

- Run the LLama oracle:

      python -m oracle model -m llama

- Run the GPT-5 oracle:

      python -m oracle model -m gpt

