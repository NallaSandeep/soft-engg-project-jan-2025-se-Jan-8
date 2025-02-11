## **Authentication & User Management**
### **1. User Authentication**
#### **POST** `/api/auth/register`
- **Description**: Register a new user (Student or TA).
- **Request Body**:
  ```json
  {
    "name": "Name",
    "email": "someuser@example.com",
    "password": "securepassword",
    "role": "student"  // or "ta"
  }
  ```
- **Response**:
  ```json
  {
    "message": "User registered successfully",
    "userId": "123456"
  }
  ```

#### **POST** `/api/auth/login`
- **Description**: Login to get an authentication token.
- **Request Body**:
  ```json
  {
    "email": "someuser@example.com",
    "password": "securepassword"
  }
  ```
- **Response**:
  ```json
  {
    "token": "jwt_token_here",
    "role": "student",
    "userId": "123456"
  }
  ```

#### **POST** `/api/auth/logout`
- **Description**: Logout and invalidate token.
- **Request Body**:
  ```json
  {
    "userId": "123456"
  }
  ```
- **Response**:
  ```json
  {
    "message": "User logged out successfully"
  }
  ```

---

## **Course & Material Management (For TA)**
### **2. Upload Course Material (RAG)**
#### **POST** `/api/courses/{courseId}/upload`
- **Description**: TA uploads course material for RAG.
- **Request Body (multipart/form-data)**:
  ```json
  {
    "file": "course_material.pdf",
    "metadata": {
      "title": "Introduction to AI",
      "description": "AI",
      "tags": ["AI", "Machine Learning"]
    }
  }
  ```
- **Response**:
  ```json
  {
    "message": "File uploaded successfully",
    "fileId": "98765"
  }
  ```

### **3. Get Course Materials**
#### **GET** `/api/courses/{courseId}/materials`
- **Response**:
  ```json
  {
    "courseId": "AI101",
    "materials": [
      {
        "fileId": "98765",
        "title": "Introduction to AI",
        "description": "AI",
        "uploadedBy": "TA"
      }
    ]
  }
  ```

### **4. Delete Course Material**
#### **DELETE** `/api/courses/{courseId}/materials/{fileId}`
- **Response**:
  ```json
  {
    "message": "Material deleted successfully"
  }
  ```

---

## **Agent (Study Help Bot)**
### **5. Ask a Question**
#### **POST** `/api/agent/ask`
- **Description**: Student asks a question to the AI agent.
- **Request Body**:
  ```json
  {
    "userId": "123456",
    "courseId": "AI101",
    "question": "What is supervised learning?"
  }
  ```
- **Response**:
  ```json
  {
    "answer": "Supervised learning is a machine learning technique where models learn from labeled data...",
    "sources": [
      {
        "title": "AI Basics",
        "fileId": "98765",
        "url": "https://moocportal.com/materials/98765"
      }
    ]
  }
  ```

### **6. Get Chat History**
#### **GET** `/api/agent/history/{userId}`
- **Response**:
  ```json
  {
    "userId": "123456",
    "history": [
      {
        "question": "What is supervised learning?",
        "answer": "Supervised learning is a technique...",
        "timestamp": "2025-02-11T12:34:56Z"
      }
    ]
  }
  ```

---

## **Student & TA Interactions**
### **7. List Available Courses**
#### **GET** `/api/courses`
- **Response**:
  ```json
  {
    "courses": [
      {
        "courseId": "AI101",
        "name": "Artificial Intelligence",
        "instructor": "Prof. ABC"
      }
    ]
  }
  ```

### **8. Enroll in a Course**
#### **POST** `/api/courses/enroll`
- **Request Body**:
  ```json
  {
    "userId": "123456",
    "courseId": "AI101"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Enrollment successful"
  }
  ```

### **9. List Enrolled Students (For TA)**
#### **GET** `/api/courses/{courseId}/students`
- **Response**:
  ```json
  {
    "courseId": "AI101",
    "students": [
      {
        "userId": "123456",
        "name": "John Doe",
        "email": "johndoe@example.com"
      }
    ]
  }
  ```
