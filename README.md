# chat-cli
Generative AI for the Shell `~/.`

# Usage
Create a prompt by simply invoking the AI using the keyword `clio` or `chat`, followed by your intent of execution using just natural language.

Follow the usage examples below to generate bash commands and scripts just using natural language.
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

# License
[MIT](LICENSE)


Made with  ❤️  in  🇮🇳