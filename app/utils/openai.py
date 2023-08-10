#!/usr/bin/env python3
# System and Core dependencies
import os
import platform
import sys

# Read environment variables and config
import dotenv 

# Read OS distro information
import distro

# OpenAI
import openai

# Formatting and colorization
import colorama
from termcolor import colored


#Enable color output on Windows using colorama
colorama.init() 


# Set OpenAI API key
def set_api_key(config):
    """
    This method searches for the OpenAI API key from one of the available locations
    and sets it to the openai module to communicate to the remote OpenAI LLM service.
    There are 2 options for the user to specify they openai api key:
    - Place a ".env" file in same directory as this with the line
    - Simply save the API key in the config.yaml configuration file
    """
    #1: Place a ".env" file in same directory as this with the line:
    #   OPENAI_API_KEY="<yourkey>"
    #   or do `export OPENAI_API_KEY=<yourkey>` before use  
    dotenv.load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    #2. Simply add the key in the config.yaml file
    #   openai_apikey: <yourkey>
    if not openai.api_key:  
        openai.api_key = config["openai_api_key"]


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
    prompt_file = os.path.join(prompt_path, "clio_prompt.txt")
    pre_prompt = open(prompt_file,"r").read()
    pre_prompt = pre_prompt.replace("{shell}", shell)
    pre_prompt = pre_prompt.replace("{os}", get_os_friendly_name())
    prompt = pre_prompt + user_prompt

    # format the entered prompt to make it a question
    if prompt[-1:] != "?" and prompt[-1:] != ".":
        prompt+="?"

    return prompt


# Call OpenAI using the OpenAI API key with the composed prompt
def call_open_ai(query, shell, config):  
    # do we have a prompt from the user?
    if query == "":
        print ("No user prompt specified.")
        sys.exit(-1)
        # TODO: Even if there is no user prompt, we need to check for more args like --help
 
    # Load the correct prompt based on Shell and OS and append the user's prompt
    prompt = get_full_prompt(query, shell)

    # Make the first line also the system prompt
    system_prompt = prompt[1]
    #print(prompt)

    # Call the ChatGPT API
    response = openai.ChatCompletion.create(
        model = config["model"],
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature = config["temperature"],
        max_tokens = config["max_tokens"],
    )
 
    return response.choices[0].message.content.strip()
