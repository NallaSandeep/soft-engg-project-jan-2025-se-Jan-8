#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Run the application
python -m uvicorn main:app --reload 