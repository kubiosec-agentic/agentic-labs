# Cleanup

# Define a portable cecho function for colored output
cecho() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "$@"
    else
        echo -e "$@"
    fi
}

# export LAB=".$(basename "$PWD")"
export LAB=".$(basename "$PWD" | cut -c1-6)"
echo "================================================================================"
echo "Cleaning up $LAB"
echo "================================================================================"
if [ -f "requirements.txt" ]; then
    rm -rf "$LAB"
    cecho "Removed virtual environment: \033[31m$LAB\033[0m. Please run \033[31mdeactivate\033[0m"
else
    cecho "\033[33mNo virtual environment found to remove: $LAB\033[0m"
fi
echo "================================================================================"
cecho "\033[32mCleanup complete for $LAB\033[0m"
echo "================================================================================"


