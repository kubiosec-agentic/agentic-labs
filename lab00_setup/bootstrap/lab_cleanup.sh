# Cleanup 
export LAB=".$(basename "$PWD")"
echo "================================================================================"
echo "Cleaning up $LAB environment"
echo "================================================================================"
rm -rf $LAB
if [ -f "requirements.txt" ]; then
    echo "================================================================================"
    echo -e "Cleanup complete. Run \033[31mdeactivate\033[0m to deactivate the virtual environment"
    echo "================================================================================"
else
    echo "================================================================================"
    echo "requirements.txt not found, skipping python virtual env deactvation"
    echo "================================================================================"
fi
