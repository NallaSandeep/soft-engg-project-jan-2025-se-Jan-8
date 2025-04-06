# StudyHub TA Module Implementation Guide

## Current Setup

StudyHub has 3 user types right now:
- Students (normal users who take courses)
- Admins (full access to manage everything)
- Teachers (exists in DB but not really used in the interface)

The system already has:

1. **User model with role field**
```python
# app/models/user.py
class User(BaseModel):
    # ...
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, student, ta
    # ...
```

2. **Authorization decorators**
```python
# app/decorators.py
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims or claims.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def admin_or_ta_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims or claims.get('role') not in ['admin', 'ta']:
            return jsonify({'message': 'Admin or TA access required'}), 403
        return f(*args, **kwargs)
    return decorated_function
```

3. **Login system that handles roles**
```javascript
// Current login flow (simplified)
const login = async (credentials) => {
    try {
        const response = await authApi.login(credentials);
        if (response.success) {
            const { access_token, user } = response.data;
            setToken(access_token);
            setUser(user);
            
            if (user.role === 'admin') {
                navigate('/admin/dashboard');
            } else {
                navigate('/student/dashboard');
            }
        }
    } catch (error) {
        // Error handling
    }
};
```

4. **TA routes defined but not fully implemented**
```javascript
// src/routes/TARoutes.js
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import TADashboard from '../components/ta/Dashboard';
import LectureManagement from '../components/ta/LectureManagement';
import AssignmentManagement from '../components/ta/AssignmentManagement';
import QuestionBank from '../components/ta/QuestionBank';
import SystemLogs from '../components/ta/SystemLogs';

const TARoutes = () => {
    return (
        <Routes>
            <Route path="dashboard" element={<TADashboard />} />
            <Route path="lectures" element={<LectureManagement />} />
            <Route path="assignments" element={<AssignmentManagement />} />
            <Route path="question-bank" element={<QuestionBank />} />
            <Route path="system-logs" element={<SystemLogs />} />
            <Route path="" element={<Navigate to="dashboard" replace />} />
        </Routes>
    );
};

export default TARoutes;
```

## What Needs To Be Done

We want TAs to be a subset of admin functionality - let them access almost everything admins can, but with some restrictions. Here's what we need to change:

### 1. Backend Changes

The backend already has `admin_or_ta_required` decorator. We just need to use this decorator instead of `admin_required` for routes that TAs should access:

```python
# Before
@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    # ...

# After
@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_or_ta_required
def get_dashboard_stats():
    # ...
```

Some routes will need additional checks to restrict TAs to only their courses:

```python
@courses_bp.route('/<int:course_id>/content', methods=['GET'])
@admin_or_ta_required
def get_course_content(course_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Admin can access everything
    if user.role == 'admin':
        # Get course content without restrictions
        pass
    else:
        # For TAs, check if they're assigned to this course
        enrollment = CourseEnrollment.query.filter_by(
            course_id=course_id,
            user_id=user_id,
            role='ta',
            status='active'
        ).first()
        
        if not enrollment:
            return jsonify({"message": "Not authorized to access this course"}), 403
        
    # Rest of the function for both admin and TA
    # ...
```

### 2. Frontend Changes

#### Update Login Logic

```javascript
// hooks/useAuth.js
const login = async (credentials) => {
    try {
        const response = await authApi.login(credentials);
        if (response.success) {
            const { access_token, user } = response.data;
            setToken(access_token);
            setUser(user);
            
            // Add TA handling
            if (user.role === 'admin') {
                navigate('/admin/dashboard');
            } else if (user.role === 'ta') {
                navigate('/ta/dashboard');
            } else {
                navigate('/student/dashboard');
            }
        }
    } catch (error) {
        // Error handling
    }
};
```

#### Update App.js to Include TA Routes

```javascript
// App.js
// Change this:
const taRoutes = [
    {
        path: '/ta',
        children: [
            { path: 'dashboard', element: <TADashboard /> },
            // ...
        ]
    }
];

// And properly include it in Routes like this:
<Routes>
    {/* Public Routes */}
    <Route path="/login" element={<Login />} />
    {/* ... */}
    
    {/* Protected Routes */}
    <Route element={<Layout />}>
        {/* ... */}
        
        {/* TA Routes */}
        <Route path="/ta">
            <Route path="dashboard" element={<TADashboard />} />
            <Route path="courses" element={<TACourses />} />
            <Route path="assignments" element={<TAAssignments />} />
            {/* Add more TA routes */}
            <Route path="" element={<Navigate to="dashboard" replace />} />
        </Route>
    </Route>
</Routes>
```

#### Create a Navigation Component for TAs

```javascript
// components/navigation/TANavigation.js
import React from 'react';
import { NavLink } from 'react-router-dom';

const TANavigation = () => {
    return (
        <nav>
            <ul>
                <li><NavLink to="/ta/dashboard">Dashboard</NavLink></li>
                <li><NavLink to="/ta/courses">Courses</NavLink></li>
                <li><NavLink to="/ta/assignments">Assignments</NavLink></li>
                <li><NavLink to="/ta/question-bank">Question Bank</NavLink></li>
            </ul>
        </nav>
    );
};

export default TANavigation;
```

#### Update Main Navigation Component

```javascript
// components/navigation/Navigation.js
import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import AdminNavigation from './AdminNavigation';
import TANavigation from './TANavigation';
import StudentNavigation from './StudentNavigation';

const Navigation = () => {
    const { user } = useAuth();
    
    if (user.role === 'admin') {
        return <AdminNavigation />;
    } else if (user.role === 'ta') {
        return <TANavigation />;
    } else {
        return <StudentNavigation />;
    }
};
```

#### TA Dashboard Component

We can either create new TA components or reuse admin components with restrictions. Here's an approach with a new TA Dashboard:

```javascript
// components/ta/Dashboard.js
import React, { useState, useEffect } from 'react';
import { adminApi } from '../../services/apiService';

const TADashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        const fetchData = async () => {
            try {
                // Use the same API that admins use - backend will filter data
                const response = await adminApi.getDashboardStats();
                setStats(response.data);
            } catch (error) {
                console.error('Error loading dashboard:', error);
            } finally {
                setLoading(false);
            }
        };
        
        fetchData();
    }, []);
    
    if (loading) return <div>Loading...</div>;
    
    return (
        <div>
            <h1>TA Dashboard</h1>
            <div className="stats-grid">
                <div className="stat-card">
                    <h3>Courses</h3>
                    <p>{stats?.stats?.totalCourses || 0}</p>
                </div>
                <div className="stat-card">
                    <h3>Assignments</h3>
                    <p>{stats?.stats?.totalAssignments || 0}</p>
                </div>
                {/* More stat cards */}
            </div>
            
            <h2>Recent Courses</h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Code</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {stats?.recentCourses?.map(course => (
                        <tr key={course.id}>
                            <td>{course.name}</td>
                            <td>{course.code}</td>
                            <td>
                                <button>View</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default TADashboard;
```

#### Reusing Admin Components with Role Checks

For components that will be used by both admins and TAs:

1. **Course Management**
   - TAs can view and edit course content
   - TAs cannot delete courses or change enrollment type

2. **Assignment Management**
   - TAs can create and grade assignments
   - TAs cannot delete assignment types

3. **Question Bank**
   - TAs can add and edit questions
   - TAs cannot delete question categories

## Testing Steps

1. Create a TA user
```sql
-- If using PostgreSQL/MySQL:
UPDATE users SET role = 'ta' WHERE id = 123;  -- Change an existing user
-- OR
INSERT INTO users (username, email, password_hash, role) VALUES ('ta_user', 'ta@example.com', 'hashed_password', 'ta');  -- Create new
```

2. Enroll the TA in some courses
```sql
INSERT INTO course_enrollments (course_id, user_id, role, status)
VALUES (1, 123, 'ta', 'active');
```

3. Log in with TA credentials and test:
   - Login redirects to TA dashboard
   - TA can access their assigned courses
   - TA can create/edit content but not delete courses
   - Admin-only features are hidden

## Summary

We're basically taking the admin interface and making a restricted version for TAs. The backend already has most of what we need - we just need to:

1. Use the right decorators (`admin_or_ta_required`)
2. Add role checks where needed
3. Set up the frontend routes for TAs
4. Handle login redirects for TAs
5. Add role-based conditional rendering to hide admin-only features

This approach gives us a working TA module quickly with minimal code changes.
