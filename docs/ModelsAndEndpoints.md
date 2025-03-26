# StudyHub Models and Endpoints Documentation

## Core Models

### 1. User Model (`user.py`)
**Purpose**: Core user management and authentication
- **Key Fields**: id, username, email, password_hash, role, first_name, last_name, is_active
- **Relationships**:
  - courses_created (Course) - One-to-Many
  - course_enrollments (CourseEnrollment) - One-to-Many
  - resources_uploaded (Resource) - One-to-Many
  - questions_created (Question) - One-to-Many
  - submissions/submissions_graded (Submission) - One-to-Many
  - assignment_submissions (AssignmentSubmission) - One-to-Many
  - personal_resources (PersonalResource) - One-to-Many

### 2. Course Model (`course.py`)
**Purpose**: Course management and organization
- **Key Fields**: id, code, name, description, created_by_id, start_date, end_date, is_active
- **Relationships**:
  - created_by (User) - Many-to-One
  - enrollments (CourseEnrollment) - One-to-Many
  - resources (Resource) - One-to-Many
  - personal_resources (PersonalResource) - One-to-Many
  - weeks (Week) - One-to-Many

### 3. CourseEnrollment Model (`course.py`)
**Purpose**: Manages student and TA enrollments in courses
- **Key Fields**: course_id, user_id, role, status, enrolled_at
- **Relationships**:
  - course (Course) - Many-to-One
  - user (User) - Many-to-One

### 4. Week Model (`course_content.py`)
**Purpose**: Organizes course content by weeks
- **Key Fields**: course_id, number, title, description, is_published
- **Relationships**:
  - course (Course) - Many-to-One
  - lectures (Lecture) - One-to-Many
  - assignments (Assignment) - One-to-Many
  - resources (Resource) - One-to-Many

### 5. Lecture Model (`course_content.py`)
**Purpose**: Manages course lectures and content
- **Key Fields**: week_id, lecture_number, title, content_type, youtube_url, file_path
- **Relationships**:
  - week (Week) - Many-to-One
  - progress_records (LectureProgress) - One-to-Many

### 6. LectureProgress Model (`course_content.py`)
**Purpose**: Tracks student progress in lectures
- **Key Fields**: lecture_id, user_id, completed, completed_at
- **Relationships**:
  - lecture (Lecture) - Many-to-One
  - user (User) - Many-to-One

### 7. Assignment Model (`assignment.py`)
**Purpose**: Manages course assignments
- **Key Fields**: week_id, title, type, start_date, due_date, points_possible
- **Relationships**:
  - week (Week) - Many-to-One
  - questions (AssignmentQuestion) - One-to-Many
  - submissions (AssignmentSubmission) - One-to-Many

### 8. Question Model (`question.py`)
**Purpose**: Question bank for assignments
- **Key Fields**: title, content, type, question_options, correct_answer, points
- **Relationships**:
  - created_by (User) - Many-to-One
  - assignments (AssignmentQuestion) - One-to-Many

### 9. AssignmentSubmission Model (`assignment.py`)
**Purpose**: Manages student assignment submissions
- **Key Fields**: assignment_id, user_id, answers, score, status
- **Relationships**:
  - assignment (Assignment) - Many-to-One
  - student (User) - Many-to-One

### 10. PersonalResource Model (`personal_resource.py`)
**Purpose**: Manages student-specific resources
- **Key Fields**: user_id, course_id, name, description, settings
- **Relationships**:
  - user (User) - Many-to-One
  - course (Course) - Many-to-One
  - files (ResourceFile) - One-to-Many

### 11. ResourceFile Model (`personal_resource.py`)
**Purpose**: Manages files for personal resources
- **Key Fields**: resource_id, name, type, content, file_path
- **Relationships**:
  - resource (PersonalResource) - Many-to-One

## Unused Models

1. **Resource Model** (`resource.py`) - Marked as "NOT USED"
   - Originally designed for course resources
   - Replaced by PersonalResource for better organization

## API Endpoints

### 1. Auth Endpoints (`auth_bp`)
- `/register` - User registration
- `/login` - User authentication
- Uses: User model

### 2. Users Endpoints (`users_bp`)
- `/me` - Current user details
- Uses: User model

### 3. Courses Endpoints (`courses_bp`)
- Course CRUD operations
- Week and lecture management
- Progress tracking
- Uses: Course, Week, Lecture, LectureProgress models

### 4. Assignments Endpoints (`assignments_bp`)
- Assignment management
- Submission handling
- Uses: Assignment, Question, AssignmentSubmission models

### 5. Question Bank Endpoints (`question_bank_bp`)
- Question management
- Uses: Question model

### 6. Resources Endpoints (`resources_bp`)
- Resource management
- File uploads
- Uses: PersonalResource, ResourceFile models

### 7. Admin Endpoints (`admin_bp`)
- Dashboard statistics
- System management
- Uses: All models for statistics

## Key Features

1. **Course Management**
   - Course creation and enrollment
   - Week and lecture organization
   - Progress tracking

2. **Assignment System**
   - Multiple question types
   - Automated grading
   - Progress tracking

3. **Resource Management**
   - Personal resource organization
   - File upload and management
   - Course-specific resources

4. **Progress Tracking**
   - Lecture completion tracking
   - Assignment submission tracking
   - Course progress calculation

## Security Features

1. **Authentication**
   - JWT-based authentication
   - Password hashing
   - Token expiration

2. **Authorization**
   - Role-based access control
   - Course enrollment checks
   - Resource access control

3. **File Security**
   - File type validation
   - Size limits
   - Secure storage

## Database Relationships Overview

```
User
├── courses_created (Course)
├── course_enrollments (CourseEnrollment)
├── questions_created (Question)
├── assignment_submissions (AssignmentSubmission)
└── personal_resources (PersonalResource)

Course
├── created_by (User)
├── enrollments (CourseEnrollment)
├── weeks (Week)
└── personal_resources (PersonalResource)

Week
├── course (Course)
├── lectures (Lecture)
└── assignments (Assignment)

Assignment
├── week (Week)
├── questions (AssignmentQuestion)
└── submissions (AssignmentSubmission)

PersonalResource
├── user (User)
├── course (Course)
└── files (ResourceFile)
``` 