#!/usr/bin/env python3

# System and Core dependencies
import os
import sys

# Read config
import yaml

# Formatting and colorization
import colorama

from app.utils.formatting import  check_for_issue, check_for_markdown, display_response_command_and_prompt_user_input, evaluate_input
from app.utils.openai import call_open_ai, set_api_key


#Enable color output on Windows using colorama
colorama.init() 


# Print the usage information upon base command invokation
def print_usage():
    print()
    print("chat-cli v0.1")
    print("AI Superpowers in your Terminal >_")
    print()
    print("Usage:                   [ALIAS] [OPTION] [PROMPT]")
    print()
    print("  Aliases:")
    print("    chat                 The default alias available universally out of the box.")
    print("                         Expert in executing tasks in *nix Operating Systems")
    print("    clio                 The default Agent alias available universally out of the box.")
    print("                         Expert in executing tasks in *nix Operating Systems")
    print()
    print("  Options:")
    print("    -a, --ask            Ask the user for confirmation before executing any command.")
    print("                         Used only after the alias name and before PROMPT along with Safety config set to 'Off'")
    print()
    print("* Model        : " + str(config["model"]))
    print("* Temperature  : " + str(config["temperature"]))
    print("* Max. Tokens  : " + str(config["max_tokens"]))
    print("* Safety       : On" if bool(config["safety"]) is True else "* Safety       : Off")
    print()


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
    

# Main Driver Code
if __name__ == "__main__":
    """
    Entry point of the application in the inline mode
    """
    config = read_config()
    set_api_key(config)

    # Unix based SHELL (/bin/bash, /bin/zsh), otherwise assuming it's Windows
    shell = os.environ.get("SHELL", "powershell.exe") 
    
    command_start_idx  = 1     # Question starts at which argv index?
    ask_flag = False           # safety switch -a command line argument
    clio = ""                  # user's answer to safety switch (-a) question y/n

    # Parse arguments and make sure we have at least a single word
    if len(sys.argv) < 2:
        # TODO: if it is a single word 'chat', open app in shell mode
        print_usage()
        sys.exit(-1)
  
    # Safety switch via argument -a (local override of global setting)
    # Force Y/n questions before running the command
    if sys.argv[1] == "-a" or sys.argv[1] == "--ask":
        ask_flag = True
        command_start_idx = 2
  
    # To allow easy/natural use we don't require the input to be a 
    # single string. So, the user can just type clio what is the time
    # without having to put the question between ''
    arguments = sys.argv[command_start_idx:]  # arguments are the final set of words that are sent to OpenAI as final prompt
    user_prompt = " ".join(arguments)

    response_command = call_open_ai(user_prompt, shell, config)  # the response as shell command that comes back from OpenAI
    check_for_issue(response_command)  # should check if the response command is valid and doesn't produce errors
    check_for_markdown(response_command)
    user_input = display_response_command_and_prompt_user_input(response_command, config, ask_flag)  # prompt asking the user for confirmation before executing any command
    print()  # prints a new line before the result of the final command executed
    evaluate_input(user_input, response_command, shell, config, ask_flag)  # evaluate/execute the command
