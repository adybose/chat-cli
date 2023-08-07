#!/usr/bin/env python3

# System and Core dependencies
import os
import sys

# Read config
import yaml

# Formatting and colorization
import colorama

from app.utils.formatting import  check_for_issue, check_for_markdown, evaluate_input, prompt_user_input
from app.utils.openai import call_open_ai, set_api_key


#Enable color output on Windows using colorama
colorama.init() 


# Print the usage information upon base command invokation
def print_usage():
    # print()
    print("chat-cli v0.1")
    # print()
    print("AI Superpowers in your Terminal >_")
    print()
    print()
    print("Basic Usage:             [ALIAS] [-p] [PROMPT] [--help]")
    print()
    print("  Aliases:")
    print("    clio                 The default Agent available universally out of the box. Expert in executing tasks in *nix Operating Systems")
    print()
    print("  Options:")
    print("    -p, --pause          Pauses to ask for user confirmation before executing any command. Used only after the alias name and before PROMPT along with Safety config set to 'Off'")
    print("        --help           Used only at the end of an Inline Mode usage to print the detailed usage guide for the current agent, or explanation for the generated response on an inline prompt")
    print()
    print("  [ALIAS] --help' will display the Detailed Usage of the Agent along with Help Docs on using and updating the different configurations/settings of the Agent")
    print()
    # print()
    print("Interactive Usage:       chat [-p] [--help]")
    print()
    print("  Options:")
    print("    -p, --pause          Pauses to ask for user confirmation before executing any command. Used only after the alias name and before PROMPT along with Safety config set to 'Off'")
    print()
    print("  Type 'chat --help' to display the complete Usage Docs containing the detailed usage guide of different modules and entities of the application")
    print()
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
    # import ipdb;ipdb.set_trace()
    clio_path = os.path.abspath(__file__)
    prompt_path = os.path.dirname(clio_path)

    config_file = os.path.join(prompt_path, "config.yaml")
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)
    

# Main Driver Code
if __name__ == "__main__":
    config = read_config()
    set_api_key(config)

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
    if sys.argv[1] == "-p" or sys.argv[1] == "--pause":
        ask_flag = True
        command_start_idx = 2
  
    # To allow easy/natural use we don't require the input to be a 
    # single string. So, the user can just type clio what is my name?
    # without having to put the question between ''
    arguments = sys.argv[command_start_idx:]
    user_prompt = " ".join(arguments)

    response_command = call_open_ai(user_prompt, shell, config) 
    check_for_issue(response_command)
    check_for_markdown(response_command)
    user_input = prompt_user_input(response_command, config, ask_flag)
    print()
    evaluate_input(user_input, response_command, shell, config)
