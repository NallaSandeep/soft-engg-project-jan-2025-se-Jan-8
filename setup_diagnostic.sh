#!/bin/bash

echo "Running diagnostic script in existing studyindexer environment..."
cd $(dirname "$0")
python3 diagnostic_chroma.py
echo ""
echo "Diagnostic complete. Check the output above for details." 