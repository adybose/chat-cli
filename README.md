# chat-cli
A friendly AI programming assistant right in your Shell `~/.`


# License
[MIT](LICENSE)


> **DISCLAIMER!!** This software is currently in an early alpha stage. Use with Caution ⚠️
>
> We welcome you to take it for a spin, but we do not guarantee the application running completely as per the usage guidelines.


# Usage
There are two base commands available for using the application: 
`chat`, and `clio`.

> **Note:** The command `clio` is an acronym which stands for **Command Line Input Output**. We just coined it because we wanted a friendly, relatable name for such a general-purpose CLI application as this. You can create your own aliases to invoke the application.

Just say `clio` to see the detailed usage information like shown below:
```
chat-cli v0.1
A friendly AI programming assistant right in your Shell

Usage: clio [OPTIONS] PROMPT

Options:
  -a, --ask        Pauses to ask the user's confirmation before executing any command (Only available with PROMPT and Safety config is Off)

* Model        : gpt-3.5-turbo
* Temperature  : 0
* Max. Tokens  : 500
* Safety       : On
```
This is the default Inline Mode available out of the box. Check out some of the usage examples below:
```bash
clio what is the time now in Paris

clio show me some funny unicode characters

clio show me the top three processes consuming the most CPU
```


# Local Development Setup

## Initial Setup (Step 1/2)
To begin the setup for the application, first you need to download the project repository from Github:
- Download the repository:
  ```bash
  git clone git://github.com/adybose/chat-cli.git
  ```
- `cd` into the repository root:
  ```bash
  cd chat-cli
  ```
- From the repo root, create a python virtual environment and activate it:
  ```bash
  python3 -m venv chatclienv
  source chatclienv/bin/activate
  ```
- Install the latest dependencies from the requirements.txt file:
  ```bash
  pip3 install -r requirements.txt
  ```

- Create a **config.yaml** configuration file from **config.yaml.example** template file. You can specify which OpenAI model you want to query, and other settings in this file. The safety switch can also be found in this configuration file.
- Create a **.env** file from the **.env.example** file to store environment variables that you want for this application.


> ### Important: OpenAI API Key Configuration
>
> If you have an OpenAI API Key with usage credits, you can configure it for your project on Linux and macOS using any one of these two methods mentioned below:
> - You can either `export OPENAI_API_KEY=<yourkey>`, or have a `.env` file in the same directory as `main.py` with `OPENAI_API_KEY="<yourkey>"` as a line
> - Add the key to the `config.yaml` configuration file


## Further Setup (Step 2/2)
After fetching the repository and setting up a Python environment with all the dependencies installed, complete the setup of the application using on of the below ways:

### 1. Setup on Linux and MacOS using the Setup script `setup.sh`
After downloading and initial setup as mentioned above, simply run the command `source setup.sh`. This does the following things:
- Copies the necessary files to `~/chat-cli/`
- Creates two aliases `chat` and `clio` pointing to `~/chat-cli/main.py`
- Adds the aliases to the `~/.bash_aliases` or `~/.zshrc` file

Now (after configuring your OpenAI API key for your application as explained), you can start running the program from the command line like so:
```bash
clio what is the time now in Paris
```

### 2. Manually Configuring On Linux and MacOS
If you want to manually complete the setup after completing the Initial Setup without using the `setup.sh` script, follow the steps below:
- Make the main.py file executable:
  ```bash
  chmod +x main.py
  ```
- Create an alias to invoke the main.py executable file without using the file name `main.py`:
  ```
  alias chat=$(pwd)/main.py
  alias clio=$(pwd)/main.py #optional
  ```
- Now (after configuring your OpenAI API key for your application as explained), you can call the program from the repo root using the alias followed by your natural language query from the shell like below:
  ```
  clio what is the time now in Paris
  ```


> ### CAUTION!! Disabling the Safety Switch
>
> By default `clio` will prompt the user before executing commands. 
>
> To have clio run commands right away when they come back from ChatGPT, change the `safety` in the `config.yaml` to `false`.

If you still want to inspect the command that is executed when safety is off, add the `-a` argument, Example:
```bash
clio -a delete the file test.txt
```

That's all you need to start using **chat-cli** on your local Linux or macOS machine.

May the _force_ be with you ⚡

---
#### ©️ 2023 [chat-cli](https://github.com/adybose/chat-cli/) | Made with  ❤️  in  🇮🇳
