# StudyHub Submodule

## Overview

The StudyHub submodule is the core component of the StudyHub platform, providing backend and frontend services for course management and student interaction.

## Tech Stack

- **Backend**: Flask
- **Frontend**: React
- **Database**: SQLite (default)

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python scripts/init_db.py
   ```

5. Run the Flask server:
   ```bash
   flask run
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the required packages:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Testing

- Run backend tests:
  ```bash
  cd backend
  pytest
  ```

- Run frontend tests:
  ```bash
  cd frontend
  npm test
  ```
