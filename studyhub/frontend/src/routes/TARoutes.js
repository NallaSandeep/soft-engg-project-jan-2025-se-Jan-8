import React from 'react';
import TADashboard from '../components/ta/TADashboard';
import Dashboard from '../components/ta/Dashboard';
import TaLayout from '../components/ta/TaLayout';
import CourseForm from '../components/ta/CourseForm';
import CourseContent from '../components/ta/CourseContent';
import WeekEdit from '../components/ta/WeekEdit';
import LectureForm from '../components/ta/LectureForm';
import AssignmentsList from '../components/ta/AssignmentsList';
import AssignmentForm from '../components/ta/AssignmentForm';
import AssignmentView from '../components/ta/assignments/AssignmentView';
import QuestionForm from '../components/ta/QuestionBank/QuestionForm';
import QuestionList from '../components/ta/QuestionBank/QuestionList';
import CourseManagement from '../components/ta/CourseManagement';
import CourseContentManagement from '../components/ta/CourseContentManagement';

const taRoutes = [
    {
        path: '/ta',
        element: <TaLayout />,
        children: [
            {
                path: 'dashboard',
                element: <Dashboard />
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
        ]
    }
];

export default taRoutes; 