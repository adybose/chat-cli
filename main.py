#!/usr/bin/env python3
# System and Core dependencies
import os
import platform
import subprocess
import sys

# Read OS distro information
import distro

# Read environment variables and config
import dotenv 
import yaml

# Copy-Paste clipboard functionality
import pyperclip

# OpenAI
import openai

# Formatting and colorization
import colorama
from termcolor import colored


#Enable color output on Windows using colorama
colorama.init() 


# Read the configuration file
def read_config() -> any:
  """
    Find the executing directory (e.g. in case an alias is set)
    so that we can find the config file
  """
  clio_path = os.path.abspath(__file__)
  prompt_path = os.path.dirname(clio_path)

  config_file = os.path.join(prompt_path, "config.yaml")
  with open(config_file, 'r') as file:
    return yaml.safe_load(file)


# Set OpenAI API key
def set_api_key():
  """
    This method searches for the OpenAI API key from one of the available locations
    and sets it to the openai module to communicate to the remote OpenAI LLM service.
    There are 3 options for the user to specify they openai api key:
    - Place a ".env" file in same directory as this with the line
    - Place a ".openai.apikey" in the home directory that holds the line
    - Simply save the API key in the config.yaml configuration file
  """
  #1: Place a ".env" file in same directory as this with the line:
  #   OPENAI_API_KEY="<yourkey>"
  #   or do `export OPENAI_API_KEY=<yourkey>` before use
  dotenv.load_dotenv()
  openai.api_key = os.getenv("OPENAI_API_KEY")
  
  #2: Place a ".openai.apikey" in the home directory that holds the line:
  #   <yourkey>
  #   Note: This options will likely be removed in the future
  if not openai.api_key:  #If statement to avoid "invalid filepath" error
    home_path = os.path.expanduser("~")
    openai.api_key_path = os.path.join(home_path,".openai.apikey")

  #3. Final option is to simply add the key in the config.yaml file
  #   openai_apikey: <yourkey>
  if not openai.api_key:  
    openai.api_key = config["openai_api_key"]


# Call OpenAI using the OpenAI API key with the composed prompt
def call_open_ai(query):  
  # do we have a prompt from the user?
  if query == "":
      print ("No user prompt specified.")
      sys.exit(-1)
 
  # Load the correct prompt based on Shell and OS and append the user's prompt
  prompt = get_full_prompt(query, shell)

  # Make the first line also the system prompt
  system_prompt = prompt[1]
  #print(prompt)

  # Call the ChatGPT API
  response = openai.ChatCompletion.create(
    model=config["model"],
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ],
    temperature=config["temperature"],
    max_tokens=config["max_tokens"],
  )
 
  return response.choices[0].message.content.strip()


# Print the usage information upon base command invokation
def print_usage():
  print("clio v0.1")
  print()
  print("Usage: clio [-a] list the current directory information")
  print("Argument: -a: Prompt the user before running the command (only useful when safety is off)")
  print()
  print("Current configuration per config.yaml:")
  print("* Model        : " + str(config["model"]))
  print("* Temperature  : " + str(config["temperature"]))
  print("* Max. Tokens  : " + str(config["max_tokens"]))
  print("* Safety       : On" if bool(config["safety"]) is True else "* Safety       : Off")


# Get Friendly Name of OS
def get_os_friendly_name():
  os_name = platform.system()
  
  if os_name == "Linux":
    return "Linux/" + distro.name(pretty=True)
  elif os_name == "Windows":
    return os_name
  elif os_name == "Darwin":
    return "Darwin/macOS"
  else:
    return os_name


# Construct the full prompt input
def get_full_prompt(user_prompt, shell):
  ## Find the executing directory (e.g. when alias is set)
  ## so that we can find the prompt.txt file
  clio_path = os.path.abspath(__file__)
  prompt_path = os.path.dirname(clio_path)

  ## Load the base prompt and prepare it
  prompt_file = os.path.join(prompt_path, "prompt.txt")
  pre_prompt = open(prompt_file,"r").read()
  pre_prompt = pre_prompt.replace("{shell}", shell)
  pre_prompt = pre_prompt.replace("{os}", get_os_friendly_name())
  prompt = pre_prompt + user_prompt
  
  # format the entered prompt to make it a question
  if prompt[-1:] != "?" and prompt[-1:] != ".":
    prompt+="?"

  return prompt


# Handle issues with executing the request 
def check_for_issue(response):
  prefixes = ("Sorry", "I'm sorry", "Sorry, but the question is not clear", "I'm", "I am")
  if response.lower().startswith(prefixes):
    print(colored("There was an issue: " + response, 'red'))
    sys.exit(-1)


# Handle issue when response returned is in Markdown format
def check_for_markdown(response):
  # odd corner case, sometimes ChatCompletion returns markdown
  if response.count("```",2):
    print(colored("The proposed command contains markdown, so I did not execute the response directly: \n", 'red')+response)
    sys.exit(-1)


# Check if POSIX display exists
def missing_posix_display():
  display = subprocess.check_output("echo $DISPLAY", shell=True)
  return display == b'\n'


# Display generated shell command/script from the user's input prompt
def prompt_user_input(response):
  print("Command: " + colored(response, 'blue'))
  #print(config["safety"])

  if bool(config["safety"]) == True or ask_flag == True:
    prompt_text = "Execute command? [Y]es [n]o [m]odify [c]opy to clipboard ==> "
    if os.name == "posix" and missing_posix_display():
        prompt_text =  "Execute command? [Y]es [n]o [m]odify ==> "
    print(prompt_text, end = '')
    user_input = input()
    return user_input 
  
  if config["safety"] == False:
     return "Y"


def evaluate_input(user_input, command):
  if user_input.upper() == "Y" or user_input == "":
    if shell == "powershell.exe":
      subprocess.run([shell, "/c", command], shell=False)  
    else: 
      # Unix: /bin/bash /bin/zsh: uses -c both Ubuntu and macOS should work, others might not
      subprocess.run([shell, "-c", command], shell=False)
  
  if user_input.upper() == "M":
    print("Modify prompt: ", end = '')
    modded_query = input()
    modded_response = call_open_ai(modded_query)
    check_for_issue(modded_response)
    check_for_markdown(modded_response)
    modded_user_input = prompt_user_input(modded_response)
    print()
    evaluate_input(modded_user_input, modded_response)
  
  if user_input.upper() == "C":
      if os.name == "posix" and missing_posix_display():
        return
      pyperclip.copy(command) 
      print("Copied command to clipboard.")


# Driver code
if __name__ == "__main__":
  config = read_config()
  set_api_key()

  # Unix based SHELL (/bin/bash, /bin/zsh), otherwise assuming it's Windows
  shell = os.environ.get("SHELL", "powershell.exe") 
  
  command_start_idx  = 1     # Question starts at which argv index?
  ask_flag = False           # safety switch -a command line argument
  clio = ""                  # user's answer to safety switch (-a) question y/n

  # Parse arguments and make sure we have at least a single word
  if len(sys.argv) < 2:
    print_usage()
    sys.exit(-1)
  
  # Safety switch via argument -a (local override of global setting)
  # Force Y/n questions before running the command
  if sys.argv[1] == "-a":
    ask_flag = True
    command_start_idx = 2
  
  # To allow easy/natural use we don't require the input to be a 
  # single string. So, the user can just type clio what is my name?
  # without having to put the question between ''
  arguments = sys.argv[command_start_idx:]
  user_prompt = " ".join(arguments)

  res_command = call_open_ai(user_prompt) 
  check_for_issue(res_command)
  check_for_markdown(res_command)
  user_input = prompt_user_input(res_command)
  print()
  evaluate_input(user_input, res_command)
