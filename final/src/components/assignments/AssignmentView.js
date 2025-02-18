import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { FaClock, FaCheckCircle, FaTimesCircle, FaInfoCircle } from 'react-icons/fa';

// Static assignment data (no backend calls)
const assignmentData = {
    301: {
        title: 'Practice Assignment 1.1',
        course: 'Introduction to Programming',
        type: 'practice',
        points_possible: 20,
        due_date: null,
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
    302: {
        title: 'Graded Assignment 1',
        course: 'Introduction to Programming',
        type: 'graded',
        points_possible: 20,
        due_date: '2025-02-25T23:59:00Z',
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
    303: {
        title: 'Practice Assignment 2.1',
        course: 'Introduction to Programming',
        type: 'practice',
        points_possible: 20,
        due_date: null,
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

const AssignmentView = () => {
    const { assignmentId } = useParams();
    const navigate = useNavigate();
    const assignment = assignmentData[assignmentId];

    const [answers, setAnswers] = useState(() =>
        assignment.questions.reduce((acc, q) => {
            acc[q.id] = q.type === 'MSQ' ? [] : '';
            return acc;
        }, {})
    );

    const [submitting, setSubmitting] = useState(false);

    const handleAnswerChange = (questionId, value) => {
        setAnswers(prev => ({
            ...prev,
            [questionId]: value
        }));
    };

    const handleSubmit = () => {
        setSubmitting(true);
        setTimeout(() => {
            toast.success(
                <div>
                    <div>Assignment submitted successfully!</div>
                    <div className="text-sm">Your responses have been recorded.</div>
                    {assignment.type === 'practice' && (
                        <div className="text-sm">You can try again to improve your score.</div>
                    )}
                </div>
            );
            setSubmitting(false);
        }, 1000);
    };

    if (!assignment) {
        return <div className="text-yellow-500 text-center mt-10">Assignment not found.</div>;
    }

    return (
        <div className="max-w-4xl mx-auto p-6 bg-gray-900 text-white min-h-screen">
            {/* Assignment Header */}
            <div className="bg-gray-800 rounded-lg shadow-md p-6 mb-6 border border-yellow-500">
                <h1 className="text-2xl font-bold text-yellow-400">{assignment.title}</h1>
                <p className="text-gray-300">{assignment.course}</p>
                <div className="grid grid-cols-2 gap-4 text-sm mt-4">
                    <div>
                        <span className="font-medium text-yellow-400">Type: </span>
                        <span className="px-2 py-1 rounded-full text-xs bg-yellow-600 text-black">
                            {assignment.type.charAt(0).toUpperCase() + assignment.type.slice(1)}
                        </span>
                    </div>
                    <div>
                        <span className="font-medium text-yellow-400">Due Date: </span>
                        {assignment.due_date ? new Date(assignment.due_date).toLocaleString() : 'No due date'}
                    </div>
                    <div>
                        <span className="font-medium text-yellow-400">Total Points: </span>
                        {assignment.points_possible}
                    </div>
                </div>
            </div>

            {/* Questions */}
            <div className="space-y-6">
                {assignment.questions.map((question, index) => (
                    <div key={question.id} className="bg-gray-800 rounded-lg shadow-md p-6 border border-yellow-500">
                        <h3 className="text-lg font-medium text-yellow-400">
                            Question {index + 1}: {question.title}
                            <span className="ml-2 text-sm text-gray-400">({question.points} points)</span>
                        </h3>
                        <p className="text-gray-300 mb-4">{question.content}</p>

                        {/* MCQ */}
                        {question.type === 'MCQ' && (
                            <div className="space-y-2">
                                {question.options.map((option, optionIndex) => (
                                    <label key={optionIndex} className="flex items-center space-x-3 p-2 rounded hover:bg-gray-700">
                                        <input
                                            type="radio"
                                            name={`question-${question.id}`}
                                            value={option}
                                            checked={answers[question.id] === option}
                                            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                                            className="text-yellow-500"
                                        />
                                        <span>{option}</span>
                                    </label>
                                ))}
                            </div>
                        )}

                        {/* MSQ */}
                        {question.type === 'MSQ' && (
                            <div className="space-y-2">
                                {question.options.map((option, optionIndex) => (
                                    <label key={optionIndex} className="flex items-center space-x-3 p-2 rounded hover:bg-gray-700">
                                        <input
                                            type="checkbox"
                                            value={option}
                                            checked={answers[question.id].includes(option)}
                                            onChange={(e) => {
                                                const value = e.target.value;
                                                handleAnswerChange(
                                                    question.id,
                                                    e.target.checked
                                                        ? [...answers[question.id], value]
                                                        : answers[question.id].filter(v => v !== value)
                                                );
                                            }}
                                            className="text-yellow-500"
                                        />
                                        <span>{option}</span>
                                    </label>
                                ))}
                            </div>
                        )}

                        {/* Numeric */}
                        {question.type === 'Numeric' && (
                            <div>
                                <input
                                    type="number"
                                    value={answers[question.id]}
                                    onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                                    className="w-full max-w-xs rounded-lg border-gray-600 bg-gray-700 text-white p-2"
                                    step="any"
                                    placeholder="Enter your answer..."
                                />
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* Submit Button - Fixed at bottom */}
            <div className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-yellow-500 p-4">
                <div className="max-w-4xl mx-auto flex justify-between items-center">
                    <div className="text-sm text-gray-400">
                        {assignment.type === 'practice' && "This is a practice assignment. You can submit multiple times."}
                    </div>
                    <button
                        onClick={handleSubmit}
                        disabled={submitting}
                        className={`px-6 py-2 bg-yellow-500 text-black font-bold rounded-lg hover:bg-yellow-400 
                            ${submitting ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                        {submitting ? 'Submitting...' : 'Submit Assignment'}
                    </button>
                </div>
            </div>

            {/* Padding for button spacing */}
            <div className="h-20"></div>
        </div>
    );
};

export default AssignmentView;
