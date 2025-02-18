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

    if (!course) return <div className="text-center text-yellow-400 p-4">Course not found</div>;

    return (
        <div className="flex h-screen bg-gray-900 text-white">
            {/* Left Sidebar - Course Structure */}
            <div className="w-64 bg-gray-800 shadow-lg overflow-y-auto">
                <div className="p-4 border-b border-gray-700">
                    <h2 className="text-lg font-semibold text-yellow-400">{course.code}</h2>
                    <p className="text-sm text-gray-400">{course.name}</p>
                </div>
                <nav className="p-2">
                    <button
                        onClick={() => setActiveSection('introduction')}
                        className={`w-full text-left p-2 rounded ${
                            activeSection === 'introduction' ? 'bg-yellow-500 text-black' : 'hover:bg-gray-700'
                        }`}
                    >
                        📖 Course Introduction
                    </button>

                    {course.weeks?.map(week => (
                        <div key={week.id} className="mb-2">
                            <div className="p-2 bg-gray-700 text-yellow-300 font-medium">
                                Week {week.number}: {week.title}
                            </div>
                            {week.lectures?.map(lecture => (
                                <button
                                    key={lecture.id}
                                    onClick={() => navigate(`/courses/${courseId}/lectures/${lecture.id}`)}
                                    className="w-full text-left p-2 pl-6 text-sm hover:bg-gray-700"
                                >
                                    🎥 {lecture.title}
                                </button>
                            ))}
                            {week.assignments?.map(assignment => (
                                <button
                                    key={assignment.id}
                                    onClick={() => navigate(`/courses/${courseId}/assignments/${assignment.id}`)}
                                    className="w-full text-left p-2 pl-6 text-sm text-green-500 hover:bg-gray-700"
                                >
                                    📝 {assignment.title}
                                </button>
                            ))}
                        </div>
                    ))}
                </nav>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 overflow-y-auto p-6">
                {activeSection === 'introduction' ? (
                    <div className="max-w-4xl mx-auto bg-gray-800 rounded-lg shadow-sm p-6">
                        <h1 className="text-3xl font-bold text-yellow-400 mb-4">{course.name}</h1>
                        <div className="mb-6">
                            <span className="bg-yellow-500 text-black px-3 py-1 rounded-full text-sm">
                                {course.code}
                            </span>
                        </div>

                        <div className="grid grid-cols-2 gap-6 mb-8">
                            <div>
                                <h3 className="text-lg font-semibold mb-2 text-yellow-300">Course Faculty</h3>
                                <p className="text-gray-400">{course.created_by}</p>
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold mb-2 text-yellow-300">Course Duration</h3>
                                <p className="text-gray-400">
                                    {course.start_date} - {course.end_date}
                                </p>
                            </div>
                        </div>

                        <div className="prose max-w-none text-gray-300">
                            <h2 className="text-xl font-semibold mb-4 text-yellow-300">Course Description</h2>
                            <ReactMarkdown>{course.description}</ReactMarkdown>
                        </div>

                        <div className="mt-8">
                            <h2 className="text-xl font-semibold mb-4 text-yellow-300">Course Structure</h2>
                            <div className="space-y-4">
                                {course.weeks?.map(week => (
                                    <div key={week.id} className="border border-gray-700 rounded-lg p-4">
                                        <h3 className="font-medium mb-2 text-yellow-400">
                                            Week {week.number}: {week.title}
                                        </h3>
                                        <p className="text-gray-400 text-sm mb-2">{week.description}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                ) : null}
            </div>
        </div>
    );
};

export default CourseView;
