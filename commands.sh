#!/bin/bash
rm -rf .diana-tts
python -m venv .diana-tts
# pip freeze > requirements
pip install -r requirements
