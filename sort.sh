#!/bin/sh

printf '\033c';clear;

# Check if a Python package is installed
function check_package() {
    python -c "import $1" 2> /dev/null && echo "$1 is installed" || echo "$1 is not installed"
}

# Install a Python package if it is not installed
function ensure_package() {
    python -c "import $1" 2> /dev/null || pip install $1
}

# Check and ensure required packages
echo "Checking dependencies..."
for pkg in numpy python_tsp spotipy pandas tqdm signal; do
    check_package $pkg
    ensure_package $pkg
done

python save_playlist_features.py && 
python sort_playlist.py && 
python reorder_playlist.py