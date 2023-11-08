#!/bin/sh

printf '\033c'; clear;

rm ./data/*.csv;

#  brew install pipx
#  pipx install poetry

# Check if a Python package is installed
function check_package() {
    python -c "import $1" 2> /dev/null && echo "$1 is installed" || echo "$1 is not installed"
}

# Install a Python package if it is not installed
function ensure_package() {
    python -c "import $1" 2> /dev/null || pip install $2
}

# Check and ensure required packages
echo "Checking dependencies..."
while IFS= read -r line; do
    # Extract the package name (before '==') and full dependency string
    pkg_name=$(echo $line | cut -d'=' -f1)
    full_dependency=$line

    # Check and ensure the package is installed
    check_package $pkg_name
    ensure_package $pkg_name $full_dependency
done < requirements.txt

python src/playlist_save.py && 
python src/playlist_sort.py && 
python src/playlist_reorder.py;