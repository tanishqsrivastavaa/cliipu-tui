#!/bin/bash

# 1. Define the directory
PD="/home/khost/Documents/work/clippy-tui"

# 2. Run kitty
# We tell kitty to run bash. 
# Bash then: changes directory (cd) -> runs python -> waits for input (read)
kitty --class clipui --title "Clipboard Manager" bash -c "cd $PD && ./.venv/bin/python tui.py || read -p 'Error occurred. Press Enter...'"`