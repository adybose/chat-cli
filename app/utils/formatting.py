#!/usr/bin/env python3

# System and Core dependencies
import os
import subprocess
import sys

# Formatting and colorization
import colorama
from termcolor import colored

# Copy-Paste clipboard functionality
import pyperclip

from app.utils.openai import call_open_ai



def check_for_issue(response):
    """
      Check for issues with executing the request
      If a response is received, checks if the response is a valid command by calling get_valid_shell_commands()
    """
    prefixes = ("Sorry", "I'm sorry", "Sorry, but the question is not clear", "I'm", "I am")
    if response.lower().startswith(prefixes):
        print(colored("Failed: " + response, 'red'))
        sys.exit(-1)


def check_for_markdown(response):
    """
      Handle issue when response returned is in Markdown format
      Odd corner case, sometimes ChatCompletion returns markdown
    """
    if response.count("```", 2):
        print(colored("The proposed command contains markdown, hence did not execute the response directly: \n", 'red') + response)
        sys.exit(-1)



def missing_posix_display():
    """
      Check if POSIX display exists
    """
    display = subprocess.check_output("echo $DISPLAY", shell=True)
    return display == b'\n'


def evaluate_input(user_input, command, shell, config, ask_flag=False):
    """
      Evaluate the user_input after the command response is displayed.
      Based on the user_input from the displayed options, 
    """
    if user_input.upper() == "Y" or user_input == "":
        if shell == "powershell.exe":
            subprocess.run([shell, "/c", command], shell=False)  
        else:  # Unix: /bin/bash /bin/zsh: uses -c both Ubuntu and macOS should work, others might not
            subprocess.run([shell, "-c", command], shell=False)
  
    if user_input.upper() == "M":
        print("Modify prompt (just type your prompt without alias or ask flag): ", end = '')  # modify the prompt and not the response command
        modded_query = input()
        modded_response = call_open_ai(modded_query, shell, config)
        check_for_issue(modded_response)  # should check if the response command is valid and doesn't produce errors
        check_for_markdown(modded_response)
        modded_user_input = display_response_command_and_prompt_user_input(modded_response, config, ask_flag)  # response_command, config, ask_flag
        print()
        evaluate_input(modded_user_input, modded_response, shell, config, ask_flag)
  
    if user_input.upper() == "C":
        if os.name == "posix" and missing_posix_display():
            return
        pyperclip.copy(command)
        print(f"Copied Command {command} to clipboard")


def display_response_command_and_prompt_user_input(response, config={}, ask_flag=False):
    """
      Display generated shell command/script from the user's input prompt
      Does not execute the command, but optionally displays a prompt
      Asking the user for confirmation before executing any command
      Returns user_input as Y, N, or M
    """
    print("Command: " + colored(response, 'blue'))

    if bool(config["safety"]) == True or ask_flag == True:
        prompt_text = "Execute command? [Y]es [n]o [c]opy to clipboard [m]odify ==> "
        if os.name == "posix" and missing_posix_display():
            prompt_text =  "Execute command? [Y]es [n]o [m]odify ==> "
        print(prompt_text, end = '')
        user_input = input()
        return user_input 
    
    if config["safety"] == False:
        return "Y"
