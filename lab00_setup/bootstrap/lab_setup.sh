# Setup

# Define a portable echo alias for colored output
if [[ "$OSTYPE" == "darwin"* ]]; then
    alias cecho='echo'
else
    alias cecho='echo -e'
fi

export LAB=".$(basename "$PWD")"
echo "================================================================================"
echo "Setting up $LAB"
echo "================================================================================"
python3 -m venv $LAB
source $LAB/bin/activate
if [ -f "requirements.txt" ]; then
    python3 -m venv $LAB
    source $LAB/bin/activate
    pip3 install -r requirements.txt
    echo "================================================================================"
    cecho "Use \033[31msource $LAB/bin/activate\033[0m to activate the virtual environment"
    echo "================================================================================"
else
    echo "================================================================================"
    echo "requirements.txt not found, skipping python virtual env creation"
    echo "================================================================================"
fi
echo "$LAB setup complete"

echo "================================================================================"
cecho "Don't forget the export your OPENAI API key \033[31mexport OPENAI_API_KEY=\"xxxxxxxxx\"\033[0m to activate the virtual environment"
echo "================================================================================"
