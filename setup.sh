#!/bin/bash

# Exit on error
set -e

echo "Starting setup process..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Create and activate virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "Ollama installed successfully!"
fi

# Get model name from .env file
MODEL_NAME=$(grep MODEL_NAME .env | cut -d '=' -f2)

# Pull the model
echo "Pulling Ollama model: $MODEL_NAME"
ollama pull "$MODEL_NAME"

echo "Setup complete! You can now run start.sh to execute the pipeline."

# Deactivate virtual environment
deactivate 