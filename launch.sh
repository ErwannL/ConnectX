#!/bin/bash

# Launch script for ConnectX game
# This script handles the game launch with proper Python environment

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed"
    exit 1
fi

# Install/update requirements
echo "Installing/updating requirements..."
pip install -r requirements.txt

echo "Starting ConnectX..."

if [ "$1" = "train" ]; then
    if [ -n "$2" ]; then
        echo "Starting AI training with depth $2..."
        python src/train_ai.py $2
    else
        echo "Starting AI training with default depth..."
        python src/train_ai.py
    fi
elif [ "$1" = "model" ]; then
    if [ -n "$2" ]; then
        echo "Starting game with model: $2..."
        python src/main.py model "$2"
    else
        echo "Error: Please specify a model file for 'model' flag."
    fi
elif [ "$1" = "dev" ]; then
    echo "Starting in development mode..."
    python src/main.py dev
else
    python src/main.py
fi
