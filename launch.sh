#!/bin/bash

echo "Installing required packages..."
pip install -r requirements.txt

echo "Starting ConnectX..."

if [ "$1" = "train" ]; then
    if [ -n "$2" ]; then
        echo "Starting AI training with depth $2..."
        python train_ai.py train $2
    else
        echo "Starting AI training with default depth..."
        python train_ai.py train
    fi
elif [ "$1" = "model" ]; then
    if [ -n "$2" ]; then
        echo "Starting game with model: $2..."
        python main.py model "$2"
    else
        echo "Error: Please specify a model file for 'model' flag."
    fi
elif [ "$1" = "dev" ]; then
    echo "Starting in development mode..."
    python main.py dev
else
    python main.py
fi
