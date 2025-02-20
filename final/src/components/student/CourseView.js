import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

const coursesData = {
    1: {
        name: 'Introduction to Programming',
        code: 'CS101',
        description: 'Learn the basics of Python programming.',
        created_by: 'Prof. John Doe',
        start_date: "Jan 10, 2025",
        end_date: "Apr 30, 2025",
        weeks: [
            {
                id: 101,
                number: 1,
                title: 'Getting Started with Python',
                description: 'Introduction to Python syntax, variables, and data types.',
                lectures: [
                    { id: 201, title: 'Introduction to Python', description: 'Understanding basic Python syntax.' },
                    { id: 202, title: 'Control Flow in Python', description: 'If statements, loops, and logical operators.' }
                ],
                assignments: [
                    { id: 301, title: 'Practice Assignment 1.1', due_date: '2025-01-20' },
                    { id: 302, title: 'Graded Assignment 1', due_date: '2025-01-25' },
                    { id: 303, title: 'Practice Assignment 2.1', due_date: '2025-02-05' }
                ]
            }
        ]
    },
    2: {
        name: 'Data Structures & Algorithms',
        code: 'CS102',
        description: 'Understand fundamental data structures and algorithms.',
        created_by: 'Prof. Alice Smith',
        start_date: "Aug 15, 2024",
        end_date: "Dec 10, 2024",
        weeks: [
            {
                id: 102,
                number: 1,
                title: 'Introduction to Data Structures',
                description: 'Arrays, Linked Lists, and Stack basics.',
                lectures: [
                    { id: 203, title: 'Understanding Arrays', description: 'Basic operations and implementations.' },
                    { id: 204, title: 'Linked Lists Explained', description: 'Singly and Doubly Linked Lists.' }
                ],
                assignments: [
                    { id: 304, title: 'DSA Practice Problems', due_date: '2024-08-30' }
                ]
            }
        ]
    },
    3: {
        name: 'Introduction to Machine Learning',
        code: 'ML101',
        description: 'A beginner-friendly course on the fundamentals of Machine Learning.',
        created_by: 'Prof. Michael Brown',
        start_date: "Jan 15, 2025",
        end_date: "May 5, 2025",
        weeks: [
            {
                id: 103,
                number: 1,
                title: 'Machine Learning Basics',
                description: 'Understanding Supervised and Unsupervised Learning.',
                lectures: [
                    { id: 205, title: 'What is Machine Learning?', description: 'Overview and applications.' },
                    { id: 206, title: 'Linear Regression Explained', description: 'Introduction to linear models.' }
                ],
                assignments: [
                    { id: 305, title: 'Basic ML Exercises', due_date: '2025-02-01' }
                ]
            }
        ]
    }
};

const CourseView = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const [activeSection, setActiveSection] = useState('introduction');

    const course = coursesData[Number(courseId)];

    if (!course) {
        return <div className="text-center text-zinc-900 dark:text-white p-4">Course not found</div>;
    }

    return (
        <div className="flex h-screen bg-zinc-50 dark:bg-zinc-900">
            {/* Left Sidebar - Course Structure */}
            <div className="w-72 bg-white/80 dark:bg-zinc-800/80 backdrop-blur-sm 
                border-r border-zinc-200/30 dark:border-zinc-700/30 overflow-y-auto">
    <div className="p-6 border-b border-zinc-200/30 dark:border-zinc-700/30">
                    <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">{course.code}</h2>
                    <p className="text-sm text-zinc-600 dark:text-zinc-400">{course.name}</p>
                </div>
                <nav className="p-4 space-y-4">
                    <button
                        onClick={() => setActiveSection('introduction')}
                        className={`w-full text-left px-4 py-2 rounded-lg text-sm font-medium transition-colors
                            ${activeSection === 'introduction' 
                                ? 'bg-zinc-900 dark:bg-white text-zinc-100 dark:text-zinc-900'
                                : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-700/50'
                            }`}
                    >
                        📖 Course Introduction
                    </button>

                    {course.weeks?.map(week => (
                        <div key={week.id} className="space-y-2">
                            <div className="px-4 py-2 text-sm font-medium text-zinc-900 dark:text-white">
                                Week {week.number}: {week.title}
                            </div>
                            <div className="space-y-1">
                                {week.lectures?.map(lecture => (
                                    <button
                                        key={lecture.id}
                                        onClick={() => navigate(`/courses/${courseId}/lectures/${lecture.id}`)}
                                        className="w-full text-left px-4 py-2 text-sm rounded-lg
                                                 text-zinc-600 dark:text-zinc-400 pl-8
                                                 hover:bg-zinc-100 dark:hover:bg-zinc-700/50 transition-colors"
                                    >
                                        🎥 {lecture.title}
                                    </button>
                                ))}
                                {week.assignments?.map(assignment => (
                                    <button
                                        key={assignment.id}
                                        onClick={() => navigate(`/courses/${courseId}/assignments/${assignment.id}`)}
                                        className="w-full text-left px-4 py-2 text-sm rounded-lg
                                                 text-zinc-600 dark:text-zinc-400 pl-8
                                                 hover:bg-zinc-100 dark:hover:bg-zinc-700/50 transition-colors"
                                    >
                                        📝 {assignment.title}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ))}
                </nav>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 overflow-y-auto p-6 bg-zinc-100 dark:bg-zinc-900">
                {activeSection === 'introduction' && (
                    <div className="max-w-4xl mx-auto space-y-6">
                        <div className="bg-white/80 dark:bg-zinc-800/80 rounded-xl p-6 
                                      backdrop-blur-sm shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                                      dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                            <h1 className="text-3xl font-bold text-zinc-900 dark:text-white mb-4">
                                {course.name}
                            </h1>
                            <div className="mb-6">
                                <span className="bg-zinc-900 dark:bg-white text-zinc-100 dark:text-zinc-900 
                                               px-3 py-1 rounded-full text-sm font-medium">
                                    {course.code}
                                </span>
                            </div>

                            <div className="grid grid-cols-2 gap-6 mb-8">
                                <div>
                                    <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-white">
                                        Course Faculty
                                    </h3>
                                    <p className="text-zinc-600 dark:text-zinc-400">{course.created_by}</p>
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-white">
                                        Course Duration
                                    </h3>
                                    <p className="text-zinc-600 dark:text-zinc-400">
                                        {course.start_date} - {course.end_date}
                                    </p>
                                </div>
                            </div>

                            <div className="prose prose-zinc dark:prose-invert max-w-none">
                                <h2 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">
                                    Course Description
                                </h2>
                                <ReactMarkdown>{course.description}</ReactMarkdown>
                            </div>
                        </div>

                        <div className="bg-white/80 dark:bg-zinc-800/80 rounded-xl p-6 
                                      backdrop-blur-sm shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                                      dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                            <h2 className="text-xl font-semibold mb-6 text-zinc-900 dark:text-white">
                                Course Structure
                            </h2>
                            <div className="space-y-4">
                                {course.weeks?.map(week => (
                                    <div key={week.id} 
                                    className="p-4 rounded-lg">
                                   <h3 className="font-medium text-zinc-900 dark:text-white mb-2">
                                       Week {week.number}: {week.title}
                                   </h3>
                                   <p className="text-zinc-600 dark:text-zinc-400 text-sm">
                                       {week.description}
                                   </p>
                               </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CourseView;