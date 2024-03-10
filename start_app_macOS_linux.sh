#!/bin/bash
echo "Initializing, please stand by..."

cd "$(dirname "$0")"
source $(python -m poetry env info --path)/bin/activate

streamlit run webui.py
read -p "Press any key to continue ..."
