# chat-cli
Generative AI for the Shell `~/.`

# Usage
After downloading and installing the application, type `clio` to see the usage details like this:
  ```
  chat-cli v0.1 

  Usage: clio [-a] <your query in natural language to generate precise bash commands>
    or 
         chat [-a] <your query in natural language to generate precise bash commands>
  
  Argument: -a (Optional): Prompt the user before running the command (only useful when safety is off. See config.yaml)

  Current configuration per config.yaml:
  * Model        : gpt-3.5-turbo
  * Temperature  : 0
  * Max. Tokens  : 500
  * Safety       : on
  ```
Follow the usage example to generate bash commands from your natural language by starting the prompt with the keywork `chat` or `clio`. The argument `-a` is optional and is useful for prompting the user before running the command when safety is off. Examples:
```bash
clio show me some funny unicode characters

chat what is the time now in Paris

clio -a show me the top three processes that are consuming the most CPU
```

# Local Development Setup
## Initial Setup
To begin the setup for the application, first you need to download the project repository from Github:
- Download the repository:
  ```bash
  git clone git://github.com/adybose/chat-cli.git
  ```
- `cd` into the repository root.
- Update the `config.yaml` configuration file. In this file you can specify which OpenAI model you want to query, and other settings. The safety switch also moved into this configuration file.

  **Note:** For now the default model is still `gpt-3.5-turbo`, but you can update to `gpt-4` if you have gotten access already!
- From the repo root, create a python virtual environment and activate it
  ```bash
  python3 -m venv chatclienv
  source chatclienv/bin/activate
  ```
- Install the latest dependencies from the requirements.txt file:
  ```bash
  pip3 install -r requirements.txt
  ```
## Setup on Linux and MacOS using the Setup script `setup.sh`
After downloading and initial setup as mentioned above, simply run the command `source setup.sh`. This does the following things:
- Copies the necessary files to `~/chat-cli/`
- Creates two aliases `chat` and `clio` pointing to `~/chat-cli/main.py`
- Adds the aliases to the `~/.bash_aliases` or `~/.zshrc` file

Now (after configuring your OpenAI API key for your application as explained), you can start running the program from the command line like so:
```bash
chat what is the time now in Paris
```

## Manually Configuring On Linux and MacOS
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

## OpenAI API Key Configuration
If you have an OpenAI API Key having usage credits, you can configure it for your project on Linux and macOS using any one of the three methods mentioned below:
- You can either `export OPENAI_API_KEY=<yourkey>`, or have a `.env` file in the same directory as `main.py` with `OPENAI_API_KEY="<yourkey>"` as a line
- Create a file at `~/.openai.apikey` with the key in it
- Add the key to the `config.yaml` configuration file


That's all you need to setup your apllication for use on your local Linux or macOS machine.

----
### CAUTION! Disabling the Safety Switch

By default `clio` will prompt the user before executing commands. 

To have clio run commands right away when they come back from ChatGPT change the `safety` in the `config.yaml` to `False`.

If you still want to inspect the command that is executed when safety is off, add the `-a` argument, e.g `clio -a delete the file test.txt`.

Let's go!


# Examples

Here are a couple of example prompts to  on how this utility can be used.

```
clio what is my username
clio whats the time?
clio whats the time in UTC
clio whats the date and time in Vienna Austria
clio show me some unicode characters
clio what is my user name and whats my machine name?
clio is there a nano process running
clio download the homepage of ycombinator.com and store it in index.html
clio find all unique urls in index.html
clio create a file named test.txt and write my user name into it
clio print the contents of the test.txt file
clio -a delete the test.txt file
clio whats the current price of Bitcoin in USD
clio whats the current price of Bitcoin in USD. Ext the price only
clio look at the ssh logs to see if any suspicious logons accured
clio look at the ssh logs and show me all recent logins
clio is the user hacker logged on right now?
clio do i have a firewall running?
clio create a hostnames.txt file and add 10 typical hostnames based on planet names to it, line by line, then show me the contents
clio find any file with the name clio.py. do not show permission denied errors
clio write a new bash script file called scan.sh, with the contents to iterate over hostnames.txt and invokes a default nmap scan on each host. then show me the file. 
clio write a new bash script file called scan.sh, with the contents to iterate over hostnames.txt and invokes a default nmap scan on each host. then show me the file. Make it over multiple lines with comments and annotiations.
clio what is the top cpu consuming process (kanha)
```

# License

MIT.
