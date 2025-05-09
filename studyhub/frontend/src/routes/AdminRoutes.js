import React from 'react';
import { Navigate } from 'react-router-dom';
import AdminLayout from '../components/admin/AdminLayout';
import AdminDashboard from '../components/admin/Dashboard';
import CoursesList from '../components/admin/CoursesList';
import CourseForm from '../components/admin/CourseForm';
import CourseContent from '../components/admin/CourseContent';
import WeekEdit from '../components/admin/WeekEdit';
import LectureForm from '../components/admin/LectureForm';
import UsersList from '../components/admin/UsersList';
import UserForm from '../components/admin/UserForm';
import AssignmentsList from '../components/admin/AssignmentsList';
import AssignmentForm from '../components/admin/AssignmentForm';
import AssignmentView from '../components/admin/assignments/AssignmentView';
import QuestionForm from '../components/admin/QuestionBank/QuestionForm';
import QuestionList from '../components/admin/QuestionBank/QuestionList';
import EnrollStudents from '../components/admin/EnrollStudTA';
import CourseManagement from '../components/admin/CourseManagement';
import CourseContentManagement from '../components/admin/CourseContentManagement';
import  ReportedMessagesList  from '../components/admin/ReportedMessagesList';

const adminRoutes = [
    {
        path: '/admin',
        element: <AdminLayout />,
        children: [
            {
                path: '',
                element: <Navigate to="/admin/dashboard" replace />
            },
            {
                path: 'dashboard',
                element: <AdminDashboard />
            },
            {
                path: 'courses',
                children: [
                    {
                        path: '',
                        element: <CourseManagement />
                    },
                    {
                        path: 'new',
                        element: <CourseForm />
                    },
                    {
                        path: ':courseId/edit',
                        element: <CourseForm />
                    },
                    {
                        path: ':courseId/content',
                        element: <CourseContent />
                    },
                    {
                        path: ':courseId/weeks/:weekId/edit',
                        element: <WeekEdit />
                    },
                    {
                        path: ':courseId/weeks/new',
                        element: <WeekEdit mode="create" />
                    },
                    {
                        path: ':courseId/weeks/:weekId/lectures/new',
                        element: <LectureForm mode="create" />
                    },
                    {
                        path: ':courseId/weeks/:weekId/lectures/:lectureId/edit',
                        element: <LectureForm mode="edit" />
                    },
                    {
                        path: ':courseId/weeks/:weekId/assignments/new',
                        element: <AssignmentForm mode="create" />
                    },
                    {
                        path: ':courseId/manage',
                        element: <CourseContentManagement />
                    }
                ]
            },
            {
                path: 'assignments',
                children: [
                    {
                        path: '',
                        element: <AssignmentsList />
                    },
                    {
                        path: 'new',
                        element: <AssignmentForm mode="create" />
                    },
                    {
                        path: ':assignmentId',
                        element: <AssignmentView />
                    },
                    {
                        path: ':assignmentId/edit',
                        element: <AssignmentForm mode="edit" />
                    }
                ]
            },
            {
                path: 'question-bank',
                children: [
                    {
                        path: '',
                        element: <QuestionList />
                    },
                    {
                        path: 'new',
                        element: <QuestionForm mode="create" />
                    },
                    {
                        path: ':questionId',
                        element: <QuestionForm mode="view" />
                    },
                    {
                        path: ':questionId/edit',
                        element: <QuestionForm mode="edit" />
                    }
                ]
            },
            {
                path: 'users',
                children: [
                    {
                        path: '',
                        element: <UsersList />
                    },
                    {
                        path: 'new',
                        element: <UserForm mode="create" />
                    },
                    {
                        path: ':userId/edit',
                        element: <UserForm mode="edit" />
                    }
                ]
            },
            {
                path: 'enroll',
                element: <EnrollStudents />
            },
            {
                path: 'reported-messages',
                children: [
                    {
                        path: '',
                        element: <ReportedMessagesList />
                    },
                    {
                        path: ':questionId',
                        element: <QuestionForm mode="view" />
                    },
                ]
            },
        ]
    }
];

export default adminRoutes;