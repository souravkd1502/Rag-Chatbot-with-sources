#!/bin/bash

# Script version
VERSION=0.1

# Function to display help message
print_help() {
    echo "Usage: hugging-dl.sh [model_path|model_url] [output_dir]"
    echo ""
    echo "Options:"
    echo "  -h, --help: Print help message and exit."
    echo "  -v, --version: Print version and exit."
    echo ""
    echo "Example:"
    echo "  hugging-dl.sh meta-llama/Llama-2-70b-chat-hf /path/to/save/model"
    echo "  hugging-dl.sh https://huggingface.co/meta-llama/Llama-2-70b-chat-hf /path/to/save/model"
    echo ""
    echo "For more information, please visit: https://github.com/wsvn53/hugging-dl"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            print_help
            exit 0
            ;;
        -v|--version)
            echo "hugging-dl version: $VERSION"
            exit 0
            ;;
        *)
            hugging_url_or_path=$1
            shift
            path_to_save_model=$1
            shift
            ;;
    esac
done

# Check if model path/url is provided
if [[ -z "$  " ]]; then
    echo "[FAILED] No huggingface model url or repo path specified!"
    exit 2
fi

# Determine save path
if [[ -z "$path_to_save_model" ]]; then
    path_to_save_model=$(basename "$hugging_url_or_path")
fi
echo "→ Path to save model files: $path_to_save_model"
mkdir -p "$path_to_save_model"

# Change to output directory
cd "$path_to_save_model" || {
    echo "[ERROR] Can't change directory to $path_to_save_model, please check permissions."
    exit 3
}

# Download model files using huggingface_hub CLI
echo "⬇️ Downloading model..."
echo $hugging_url_or_path
huggingface-cli download "$hugging_url_or_path" --local-dir "$path_to_save_model"  --token "$token" 

echo "✅ Model download completed and saved in $path_to_save_model"