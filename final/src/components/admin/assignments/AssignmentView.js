import React from 'react';
import { FaTrash } from 'react-icons/fa';
import { useParams } from "react-router-dom";

const assignmentData = {
    1: {
        title: 'Practice Assignment 1.1',
        course: 'Introduction to Programming',
        questions: [
            {
                id: 1,
                title: 'What is the output of print(2 + 3 * 4) in Python?',
                type: 'MCQ',
                content: 'Select the correct answer:',
                points: 5,
                options: ['14', '20', '11', 'None of the above'],
                correctAnswer: '14'
            },
            {
                id: 2,
                title: 'Which of the following are valid variable names in Python?',
                type: 'MSQ',
                content: 'Select all that apply:',
                points: 10,
                options: ['my_var', '2nd_var', '_variable', 'class'],
                correctAnswer: ['my_var', '_variable']
            },
            {
                id: 3,
                title: 'What is the integer value of 5 // 2 in Python?',
                type: 'Numeric',
                content: 'Enter the correct numerical answer:',
                points: 5,
                correctAnswer: 2
            }
        ]
    },
    2: {
        title: 'Graded Assignment 1',
        course: 'Introduction to Programming',
        questions: [
            {
                id: 4,
                title: 'Which keyword is used to define a function in Python?',
                type: 'MCQ',
                content: 'Select the correct answer:',
                points: 5,
                options: ['func', 'def', 'define', 'lambda'],
                correctAnswer: 'def'
            },
            {
                id: 5,
                title: 'Which of the following are immutable in Python?',
                type: 'MSQ',
                content: 'Select all that apply:',
                points: 10,
                options: ['List', 'Tuple', 'Dictionary', 'String'],
                correctAnswer: ['Tuple', 'String']
            },
            {
                id: 6,
                title: 'What is the remainder when 15 % 4 is calculated?',
                type: 'Numeric',
                content: 'Enter the correct numerical answer:',
                points: 5,
                correctAnswer: 3
            }
        ]
    },
    3: {
        title: 'Practice Assignment 2.1',
        course: 'Introduction to Programming',
        questions: [
            {
                id: 7,
                title: 'Which of these is used to create a loop in Python?',
                type: 'MCQ',
                content: 'Select the correct answer:',
                points: 5,
                options: ['repeat', 'while', 'for', 'loop'],
                correctAnswer: 'for'
            },
            {
                id: 8,
                title: 'Which of the following are valid Python data types?',
                type: 'MSQ',
                content: 'Select all that apply:',
                points: 10,
                options: ['int', 'char', 'float', 'boolean'],
                correctAnswer: ['int', 'float', 'boolean']
            },
            {
                id: 9,
                title: 'What is the value of 2 ** 3 in Python?',
                type: 'Numeric',
                content: 'Enter the correct numerical answer:',
                points: 5,
                correctAnswer: 8
            }
        ]
    }
};

const AssignmentView = ({ handleRemoveQuestion }) => {
    const { assignmentId } = useParams();
    const assignment = assignmentData[Number(assignmentId)];

    if (!assignment) {
        return (
            <div className="p-6 text-red-500 font-semibold text-center">
                Assignment not found.
            </div>
        );
    }

    return (
        <div className="p-6 bg-gray-900 min-h-screen text-white">
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-yellow-400">{assignment.title}</h1>
                <p className="text-md text-gray-400">{assignment.course}</p>
            </div>

            <div className="bg-gray-800 rounded-lg shadow-md p-6">
                {assignment.questions.map((question, index) => (
                    <div key={question.id} className="p-4 border-b border-gray-600 last:border-b-0">
                        <div className="flex justify-between items-start">
                            <div>
                                <h3 className="font-semibold text-white">
                                    Question {index + 1}: {question.title}
                                </h3>
                                <p className="text-sm text-gray-400 mt-1">
                                    {question.type} • {question.points} points
                                </p>
                            </div>
                            <button
                                onClick={() => handleRemoveQuestion(question.id)}
                                className="text-red-400 hover:text-red-600 transition"
                                title="Remove Question"
                            >
                                <FaTrash />
                            </button>
                        </div>
                        <div className="mt-4">
                            <p className="text-gray-300">{question.content}</p>
                            {question.type === 'MCQ' && (
                                <div className="mt-4 space-y-2">
                                    {question.options.map((option, optionIndex) => (
                                        <div key={optionIndex} className="flex items-center gap-2">
                                            <input type="radio" disabled className="text-yellow-400" />
                                            <span>{option}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                            {question.type === 'MSQ' && (
                                <div className="mt-4 space-y-2">
                                    {question.options.map((option, optionIndex) => (
                                        <div key={optionIndex} className="flex items-center gap-2">
                                            <input type="checkbox" disabled className="text-yellow-400" />
                                            <span>{option}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                            {question.type === 'Numeric' && (
                                <div className="mt-4">
                                    <input
                                        type="text"
                                        disabled
                                        className="w-20 border border-yellow-400 rounded px-2 py-1 text-gray-400 bg-gray-700"
                                        placeholder="Enter number"
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default AssignmentView;
