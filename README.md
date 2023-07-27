# chat-cli aka clio
A friendly AI programming assistant right in your `~/.`


# License
[MIT](LICENSE)



# Usage
There are two main commands for using the application:
- `clio`: The base command to run the application in Inline Mode
- `chat`: The base command to run the application in Interactive Shell Mode.

**Note: [WIP]** The application is currently works only in Inline Mode

Just say `clio` to see its detailed usage information like this:
```
clio v0.1
A friendly AI programming assistant right in your `~/.`

Usage: clio [COMMANDS] [OPTIONS] PROMPT

Run chat-cli in Inline Mode
Prompts only work when you are not executing any command

COMMANDS:
  agent               Show the current Agent. Available OPTIONS are: -c, --help, -u
  agents              List out all available Agents. Available OPTIONS are: -c, --help
  model               Displays the details of the currently active Model. Available OPTIONS are: -c, --help, -u
  models              List out all available Models. Available OPTIONS are: -c, --help
  history             Show the history of prompts and their resultant commands in the Inline Mode
  version             Show the version information and exit

OPTIONS:
  -c, --config        Open the app settings or the settings of any command
  -i                  Opens clio in the Interactive Shell mode. Same as starting the app using the main command 'chat'
  -a, --ask           Pauses to ask the user's confirmation before executing any command (Only useful when there is a PROMPT and Safety is Off)
  --help              Show Help Menu for any command
  -u, --use           Switch the current Model or Agent being used for response generation. The current model is displayed below the OPTIONS

* Model        : gpt-3.5-turbo
* Temperature  : 0
* Max. Tokens  : 500
* Safety       : On
```
Some usage examples of Inline Mode:
```bash
clio what is the time now in Paris

clio show me some funny unicode characters

clio show me the top three processes consuming the most CPU
```

Type `chat` to start the application in the Interactive Shell mode like below, where you can have longer conversations with the AI to solve more complex problems. Type `exit` from to return to your main terminal.
```
chat-cli ~ Agent: clio | Model: gpt-3.5-turbo | Type your query after the >>> prompt. Press Esc for Help
>>> How many files are in this current directory?
[clio] Sure, counting the files in the current directory... Loading Response...

COMMAND: echo hello (executes the command response below without asking for confirmation in the chat mode, and waits for the next input prompt)
hello
>>> exit
```


# Local Development Setup

## Initial Setup (Step 1/2)
To begin the setup for the application, first you need to download the project repository from Github:
- Download the repository:
  ```bash
  git clone git://github.com/adybose/chat-cli.git
  ```
- `cd` into the repository root
  ```bash
  cd chat-cli
  ```
- From the repo root, create a python virtual environment and activate it
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


## Improtant: OpenAI API Key Configuration
If you have an OpenAI API Key having usage credits, you can configure it for your project on Linux and macOS using any one of the three methods mentioned below:
- You can either `export OPENAI_API_KEY=<yourkey>`, or have a `.env` file in the same directory as `main.py` with `OPENAI_API_KEY="<yourkey>"` as a line
- Create a file at `~/.openai.apikey` with the key in it
- Add the key to the `config.yaml` configuration file

## Further Setup (Step 2/2)
After fetching the repository and setting up a Python environment with all the dependencies installed, complete the setup of the application using on of the below ways:

### 1. Setup on Linux and MacOS using the Setup script `setup.sh`
After downloading and initial setup as mentioned above, simply run the command `source setup.sh`. This does the following things:
- Copies the necessary files to `~/chat-cli/`
- Creates two aliases `chat` and `clio` pointing to `~/chat-cli/main.py`
- Adds the aliases to the `~/.bash_aliases` or `~/.zshrc` file

Now (after configuring your OpenAI API key for your application as explained), you can start running the program from the command line like so:
```bash
chat what is the time now in Paris
```

### 2. Manually Configuring On Linux and MacOS
If you want to manually complete the setup after completing the Initial Setup without using the `setup.sh` script, follow the steps below:
- Make the main.py file executable
  ```bash
  chmod +x main.py
  ```
- Create an alias to invoke the main.py executable file without using the file name `main.py`
  ```
  alias chat=$(pwd)/main.py
  alias clio=$(pwd)/main.py #optional
  ```
- Now (after configuring your OpenAI API key for your application as explained), you can call the program from the repo root using the alias followed by your natural language query from the shell like:
  ```
  clio what is the time now in Paris
  ```


## CAUTION!! Disabling the Safety Switch
By default `clio` will prompt the user before executing commands. 

To have clio run commands right away when they come back from ChatGPT change the `safety` in the `config.yaml` to `false`.

If you still want to inspect the command that is executed when safety is off, add the `-a` argument, Example:
```bash
clio -a delete the file test.txt
```

That's all you need to start using `clio` on your local Linux or macOS machine.

May the force be with you ⚡

---
#### ©️ 2023 [adybose](https://twitter.com/adybose) | Made with  ❤️  in  🇮🇳
