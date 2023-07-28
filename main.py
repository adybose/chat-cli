#!/usr/bin/env python3
# System and Core dependencies
import os
import platform
import subprocess
import sys

# OpenAI dependency
import openai


# Print the usage information upon base command invokation
def print_usage():
  print("clio v0.1")
  print()
  print("Usage: clio [-a] list the current directory information")
  print("Argument: -a: Prompt the user before running the command (only useful when safety is off)")
  print()
  print("Current configuration per config.yaml:")
  print("* Model        : gpt-3.5-turbo")
  print("* Temperature  : 0")
  print("* Max. Tokens  : 500")
  print("* Safety       : On")


# Driver code
if __name__ == "__main__":
  print_usage()
