#!/bin/bash

# Function to check if input is positive
is_positive() {
    local input=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    [[ "$input" =~ ^(yes|y|o|oui|ok|okay|1)$ ]]
}

# Function to get the most recent file for a given depth
get_latest_model_for_depth() {
    local depth=$1
    local latest_file=$(ls -t models/model_depth_${depth}_date_*.pkl 2>/dev/null | head -n 1)
    echo "$latest_file"
}

# Function to get the most recent training log for a given depth
get_latest_training_log_for_depth() {
    local depth=$1
    local latest_file=$(ls -t training_ai/training_depth_${depth}_date_*.log 2>/dev/null | head -n 1)
    echo "$latest_file"
}

# Ask about cleaning logs
read -p "Do you want to clean the logs directory? (yes/no): " clean_logs
if is_positive "$clean_logs"; then
    echo "Cleaning logs directory..."
    rm -rf logs/
    echo "Logs directory cleaned."
fi

# Ask about cleaning checkpoints
read -p "Do you want to clean the checkpoints directory? (yes/no): " clean_checkpoints
if is_positive "$clean_checkpoints"; then
    echo "Cleaning checkpoints directory..."
    rm -rf checkpoints/
    echo "Checkpoints directory cleaned."
fi

# Ask about cleaning models
read -p "Do you want to clean the models directory (keeping only the most recent per depth)? (yes/no): " clean_models
if is_positive "$clean_models"; then
    echo "Cleaning models directory..."
    
    # Get all unique depths
    depths=$(ls models/model_depth_*_date_*.pkl 2>/dev/null | grep -o 'depth_[0-9]*' | sort -u | cut -d'_' -f2)
    
    # For each depth, keep only the most recent model and training log
    for depth in $depths; do
        latest_model=$(get_latest_model_for_depth "$depth")
        latest_training_log=$(get_latest_training_log_for_depth "$depth")
        
        # Remove all models of this depth except the latest
        find models/ -name "model_depth_${depth}_date_*.pkl" -not -name "$(basename "$latest_model")" -delete
        
        # Remove all training logs of this depth except the latest
        find training_ai/ -name "training_depth_${depth}_date_*.log" -not -name "$(basename "$latest_training_log")" -delete
    done
    echo "Models directory cleaned."
fi

# Check for large files that might need git LFS (between 50MB and 2GB)
large_files=$(find . -type f -size +50M -size -2G -not -path "*/\.*" 2>/dev/null)

# Check for files too large even for git LFS (over 2GB)
too_large_files=$(find . -type f -size +2G -not -path "*/\.*" 2>/dev/null)

# Handle files too large for git LFS
if [ ! -z "$too_large_files" ]; then
    echo "Found files too large even for git LFS (over 2GB):"
    echo "$too_large_files"
    echo "These files will be added to .gitignore"
    echo "$too_large_files" | while read -r file; do
        echo "${file#./}" >> .gitignore
    done
fi

# Handle files that can use git LFS
if [ ! -z "$large_files" ]; then
    echo "Found some large files that can use git LFS (between 50MB and 2GB):"
    echo "$large_files"
    read -p "Do you want to use git LFS for these files? (yes/no): " use_lfs
    
    if is_positive "$use_lfs"; then
        # Initialize git LFS if not already initialized
        if ! git lfs install 2>/dev/null; then
            echo "Installing git LFS..."
            git lfs install
        fi
        
        # Track large files with git LFS
        echo "$large_files" | while read -r file; do
            git lfs track "$file"
        done
        
        # Add .gitattributes
        git add .gitattributes
    else
        # Add large files to .gitignore
        echo "$large_files" | while read -r file; do
            echo "${file#./}" >> .gitignore
        done
    fi
fi

# Add all files that should be tracked
git add .

# Get commit message
read -p "Enter commit message: " commit_message
git commit -m "$commit_message"

# Push
git push

echo "Push completed!" 