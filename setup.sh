# Simple installer for clio in the user's home directory

echo "Hello Terminal >_"
echo "Running chat-cli setup.sh ..."
echo "Installing clio..."
echo
echo "- Creating chat-cli/ in home directory..."
TARGET_DIR=~/chat-cli
TARGET_FULLPATH=$TARGET_DIR/main.py
mkdir -p $TARGET_DIR

echo "- Copying files..."
cp main.py prompt.txt config.yaml $TARGET_DIR
chmod +x $TARGET_FULLPATH

# Creates two aliases for use
echo "- Creating aliases chat and clio..."
alias chat=$TARGET_FULLPATH
alias clio=$TARGET_FULLPATH

# Add the aliases to the logon scripts
# Depends on your shell
if [[ "$SHELL" == "/bin/bash" ]]; then
  echo "- Adding aliases to ~/.bash_aliases"
  [ "$(grep '^alias chat=' ~/.bash_aliases)" ]     && echo "alias chat already created"     || echo "alias chat=$TARGET_FULLPATH"     >> ~/.bash_aliases
  [ "$(grep '^alias clio=' ~/.bash_aliases)" ] && echo "alias clio already created" || echo "alias clio=$TARGET_FULLPATH" >> ~/.bash_aliases
elif [[ "$SHELL" == "/bin/zsh" ]]; then
  echo "- Adding aliases to ~/.zshrc"
  [ "$(grep '^alias chat=' ~/.zshrc)" ]     && echo "alias chat already created"     || echo "alias chat=$TARGET_FULLPATH"     >> ~/.zshrc 
  [ "$(grep '^alias clio=' ~/.zshrc)" ] && echo "alias clio already created" || echo "alias clio=$TARGET_FULLPATH" >> ~/.zshrc
else
  echo "Note: Shell was not bash or zsh."
  echo "      Consider configuring aliases (like chat and/or clio) manually by adding them to your login script, e.g:"
  echo "      alias chat=$TARGET_FULLPATH     >> <your_logon_file>"
fi

echo
echo "Setup Complete! Successfully installed chat-cli v0.1"
echo "Run this script when there is a new update. Follow https://github.com/adybose/chat-cli"
echo
echo "Make sure you have the OpenAI API key set via one of these options:" 
echo "  - environment variable"
echo "  - .env or an ~/.openai.apikey file or in"
echo "  - config.yaml"
echo
echo "May the Force be with You!"
