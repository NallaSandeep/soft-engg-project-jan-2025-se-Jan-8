import React from 'react';
import { useParams } from 'react-router-dom';

const courseData = {
    1: {
        title: 'Introduction to Programming',
        lectures: [
            { id: 1, title: 'Lecture 1: Basics of Python' },
            { id: 2, title: 'Lecture 2: Control Flow Statements' },
            { id: 3, title: 'Lecture 3: Functions and Modules' }
        ],
        assignments: [
            { id: 1, title: 'Practice Assignment 1.1' },
            { id: 2, title: 'Graded Assignment 1' }
        ]
    },
    2: {
        title: 'Data Structures & Algorithms',
        lectures: [
            { id: 4, title: 'Lecture 1: Arrays and Strings' },
            { id: 5, title: 'Lecture 2: Stacks and Queues' },
            { id: 6, title: 'Lecture 3: Linked Lists' }
        ],
        assignments: [
            { id: 3, title: 'Practice Assignment 2.1' }
        ]
    }
};

const CourseDetails = () => {
    const { courseId } = useParams();
    const course = courseData[Number(courseId)];

    if (!course) {
        return (
            <div className="p-6 text-red-500 font-semibold text-center">
                Course not found.
            </div>
        );
    }

    return (
        <div className="p-6 bg-gray-900 min-h-screen text-white">
            <h1 className="text-3xl font-bold text-yellow-400">{course.title}</h1>

            <div className="mt-6 bg-gray-800 rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-yellow-300">Lectures</h2>
                {course.lectures.length > 0 ? (
                    <ul className="mt-4 space-y-2">
                        {course.lectures.map((lecture) => (
                            <li key={lecture.id} className="p-2 border-b border-gray-600 last:border-b-0">
                                {lecture.title}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-gray-400 mt-2">No lectures available.</p>
                )}
            </div>

            <div className="mt-6 bg-gray-800 rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-yellow-300">Assignments</h2>
                {course.assignments.length > 0 ? (
                    <ul className="mt-4 space-y-2">
                        {course.assignments.map((assignment) => (
                            <li key={assignment.id} className="p-2 border-b border-gray-600 last:border-b-0">
                                {assignment.title}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-gray-400 mt-2">No assignments available.</p>
                )}
            </div>
        </div>
    );
};

export default CourseDetails;
