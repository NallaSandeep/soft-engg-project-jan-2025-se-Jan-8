import pytest
import os
from pathlib import Path
import shutil

# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_UPLOAD_DIR = Path(__file__).parent / "test_uploads"
TEST_CHROMA_DIR = Path(__file__).parent / "test_chroma"

@pytest.fixture(scope="session", autouse=True)
def setup_test_directories():
    """Create and clean up test directories"""
    # Create directories
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    os.makedirs(TEST_UPLOAD_DIR, exist_ok=True)
    os.makedirs(TEST_CHROMA_DIR, exist_ok=True)
    
    # Set environment variables for testing
    os.environ["UPLOAD_DIR"] = str(TEST_UPLOAD_DIR)
    os.environ["CHROMA_DIR"] = str(TEST_CHROMA_DIR)
    os.environ["TESTING"] = "true"
    
    yield
    
    # Cleanup after tests
    if TEST_UPLOAD_DIR.exists():
        shutil.rmtree(TEST_UPLOAD_DIR)
    if TEST_CHROMA_DIR.exists():
        shutil.rmtree(TEST_CHROMA_DIR)

@pytest.fixture(scope="function")
def test_document():
    """Create a test document for upload tests"""
    doc_path = TEST_DATA_DIR / "test_document.pdf"
    if not doc_path.exists():
        with open(doc_path, "w") as f:
            f.write("This is a test document for API testing.\nIt contains some sample content.")
    return doc_path 