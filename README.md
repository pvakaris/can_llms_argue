# The LLM discussion and argument mapping framework

This project contains code that allows for machine-to-machine debates between LLMs and then maps those discussions to AIF argument maps.

---

## Subprojects

### Discussion module

Contains code that facilitates the discussions between LLMs and exports the discussion in .txt format. For more information see the other [README](discussion_module/README.md).

### Oracle

Contains code for running different oracle models as well as a tool to test the output of the models against benchmarks. For more information see the other [README](oracle/README.md).


### Shared library

Contains shared resources, utilities and models. For more information see the other [README](shared/README.md).

---

## How to run the framework as a whole

1. **Create a virtual environment**

       python -m venv .venv

2. **Activate the virtual environment**
   - macOS / Linux:
   
         source .venv/bin/activate

3. **Install dependencies**
   - First, install the `shared` package (required by the other two modules):

         pip install ./shared

   - Then, install the `oracle` package:

         pip install ./oracle
   
   - Lastly, install the `discussion_module` package:

         pip install ./discussion_module

4. **Run modules**

    Run the following in the terminal or create run configurations to do that automatically. If you are using PyCharm, example configurations are provided [here](helpers/pycharmConfigurations).

   - Run the Llama oracle:

         python -m oracle model -m llama 
   
   - Run the GPT-5 oracle (needs OPENAI_API_KEY provided in .env file):

         python -m oracle model -m gpt 
   
   - Run the UvA oracle (needs UVA_AI_API_KEY provided in .env file):

         python -m oracle model -m uva 
   
   - Run the oracle result analyser:

         python -m oracle analyse
   
   - Run the oracle benchmark test:

         python -m oracle test
   
   - Run the discussion_module:

         ./start.sh auto-launch

5. Optionally, run SonarQube to perform code analysis. For that, refer to [here](helpers/sonarqube_test.txt).

---

**Author**: Vakaris Paulavičius