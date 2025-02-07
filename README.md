# StudyHub

StudyHub is a SEEK-like learning management system that provides a comprehensive platform for academic course management and student learning. The platform enables:

- **Admins & TAs**: Create and manage courses, materials, and assignments
- **Students**: Access course materials, complete assignments, and track academic progress
- **AI-Powered Learning**: Chat with an AI assistant about courses, FAQs, and general queries
- **Personal Knowledge Base**: Students can create and reference their own study notes through the chat interface

## Tech Stack

### Backend
- Python 3.x
- Flask
- SQLAlchemy
- PostgreSQL
- Flask-JWT-Extended for authentication
- Flask-Migrate for database migrations

### Frontend
- React 18
- React Router v6
- Tailwind CSS
- Axios for API calls
- React Icons and HeroIcons
- React Hot Toast for notifications

## Prerequisites

Make sure you have the following installed:
- Python 3.x
- Node.js (v14 or higher)
- npm (comes with Node.js)
- Git
- PostgreSQL (optional - SQLite is used by default in development)

## Installation

### Clone the Repository

```bash
git clone https://github.com/NallaSandeep/soft-engg-project-jan-2025-se-Jan-8.git
cd soft-engg-project-jan-2025-se-Jan-8
git checkout michael-beta
```

### Backend Setup

1. Create and activate a virtual environment:
```bash
cd backend
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Configure your database and other settings in `.env`

4. Initialize the database and load sample data:
```bash
python scripts/init_db.py
```
This step is crucial as it sets up:
- Initial database schema
- Admin and TA accounts
- Sample courses and materials
- Test student accounts
- Example assignments

5. Start the backend server:
```bash
# Option 1: Using Flask
flask run

# Option 2: Using WSGI
python wsgi.py
```

The backend server will start at `http://localhost:5000`

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend application will start at `http://localhost:3000`

## Development

### Backend Development
- The backend uses Flask blueprints for modular organization
- Database migrations are handled with Flask-Migrate
- Configuration settings are in `config.py`
- Environment variables are set in `.env`
- API endpoints are organized by feature in `app/routes/`
- Authentication is handled via JWT tokens

### Frontend Development
- React components are in `src/components`
- API services are in `src/services`
- Styling is done with Tailwind CSS
- Routes are defined in `src/App.js`
- State management uses React Context
- Chat interface components in `src/components/chat`

## Testing

### Backend Tests
```bash
cd backend
python run_tests.py
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Default Accounts

After initializing the database, you can log in with these sample accounts:

- Admin: admin@studyhub.com / admin123
- Student: student@studyhub.com / student123
- TA: ta@studyhub.com / ta123 (interface not ready yet)