CURRENT SYSTEM ARCHITECTURE
============================
Backend (Flask)
Entry Point: wsgi.py - Configures and runs the Flask application
Configuration: Uses .env for environment variables and config.py for app settings
Database: SQLAlchemy with PostgreSQL/SQLite support

Structure:
app/models/ - Database models (User, Course, Assignment, etc.)
app/api/v1/ - REST API endpoints
app/utils/ - Helper functions
app/services/ - Business logic
Frontend (React)
Entry Point: index.js and App.js
Structure:
src/components/ - UI components
src/routes/ - Route definitions
src/contexts/ - State management
src/hooks/ - Custom React hooks
src/services/ - API integration

Module Integration
Authentication Flow
Frontend login form → Backend /auth endpoint
JWT token generation and storage
Role-based route protection (Admin/Teacher/Student)
Course Management
Admin/Teacher creates courses → Backend validates and stores
Students can view and enroll in courses
Course content organized by weeks and lectures
Assignment System
Two types: Practice and Graded
Question types: MCQ, MSQ, Numeric
Automatic grading and score calculation
Completed Features
Backend/API (Completed)
Authentication & Authorization
[x] User login/logout
[x] Role-based access control
[x] JWT token management
Course Management
[x] CRUD operations for courses
[x] Course enrollment
[x] Week/lecture organization
[x] Course content management
Assignment System
[x] Assignment creation and management
[x] Multiple question types (MCQ, MSQ, Numeric)
[x] Assignment submission handling
[x] Automatic grading
[x] Practice vs Graded assignments
User Management
[x] User creation and role assignment
[x] Profile management
[x] Student enrollment tracking
Frontend (Implemented)
Authentication
[x] Login interface
[x] Role-based navigation
[x] Session management
Admin Dashboard
[x] Course overview
[x] User management
[x] Assignment tracking
[x] Question bank
Student Interface
[x] Course enrollment
[x] Assignment submission
[x] Progress tracking
[x] Course content viewing
Course Content
[x] Week/lecture organization
[x] Video lecture integration
[x] Resource management
[x] Assignment access

