#!/bin/sh
echo "Initializing, please stand by..."

cd "$(dirname "$0")"
git pull
source $(python3 -m poetry env info --path)/bin/activate

streamlit run webui.py