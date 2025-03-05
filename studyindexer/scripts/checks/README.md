# StudyIndexer Check Scripts

This directory contains scripts for checking the status and functionality of various components of the StudyIndexer application.

## Scripts

- `check_chroma.py`: Checks the connection to ChromaDB and verifies that collections are accessible.
- `chroma_check.py`: Alternative script for checking ChromaDB functionality with more detailed diagnostics.

## Usage

These scripts can be run locally or copied to the Docker container:

```bash
# Run locally
python studyindexer/scripts/checks/check_chroma.py

# Or copy to container and run there
docker cp check_chroma.py studyhub-indexer:/app/check_chroma.py
docker exec studyhub-indexer python /app/check_chroma.py
```

## Notes

- These scripts are useful for diagnosing issues with the StudyIndexer application.
- They provide detailed information about the state of various components.
- The scripts assume that the ChromaDB service is running and accessible. 