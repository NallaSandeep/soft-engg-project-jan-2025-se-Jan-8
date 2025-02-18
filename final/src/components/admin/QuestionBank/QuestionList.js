import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';

const placeholderQuestions = [
    {
        id: 1,
        title: 'What is the capital of France?',
        type: 'MCQ',
        points: 1,
        status: 'active',
        options: ['London', 'Paris', 'Berlin', 'Madrid']
    },
    {
        id: 2,
        title: 'Which of these are programming languages?',
        type: 'MSQ',
        points: 2,
        status: 'active',
        options: ['Python', 'Coffee', 'Java', 'Tea']
    },
    {
        id: 3,
        title: 'What is 2 + 2?',
        type: 'NUMERIC',
        points: 1,
        status: 'inactive'
    }
];

const QuestionList = () => {
    const [filters, setFilters] = useState({ status: '', type: '' });
    const navigate = useNavigate();

    // Function to update filters when user selects options
    const handleFilterChange = (field, value) => {
        setFilters(prev => ({ ...prev, [field]: value }));
    };

    // Apply filters to the question list
    const filteredQuestions = placeholderQuestions.filter(question => {
        return (
            (filters.status === '' || question.status === filters.status) &&
            (filters.type === '' || question.type === filters.type)
        );
    });

    return (
        <div className="container-fluid py-5 text-white" style={{ backgroundColor: '#1E1E1E', minHeight: '100vh' }}>
            <h1 className="text-warning mb-4 text-center">Question Bank</h1>

            {/* Filters & Add Button */}
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div className="d-flex gap-3">
                    {/* Status Filter */}
                    <select
                        value={filters.status}
                        onChange={(e) => handleFilterChange('status', e.target.value)}
                        className="form-select bg-dark text-white border-warning"
                    >
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                        <option value="draft">Draft</option>
                    </select>

                    {/* Type Filter */}
                    <select
                        value={filters.type}
                        onChange={(e) => handleFilterChange('type', e.target.value)}
                        className="form-select bg-dark text-white border-warning"
                    >
                        <option value="">All Types</option>
                        <option value="MCQ">Multiple Choice</option>
                        <option value="MSQ">Multiple Select</option>
                        <option value="NUMERIC">Numeric</option>
                    </select>
                </div>

                <button
                    onClick={() => navigate('/admin/question-bank/new')}
                    className="btn btn-warning fw-bold shadow-sm"
                    style={{ transition: '0.3s' }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#FFC107'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#FFD700'}
                >
                    Add Question
                </button>
            </div>

            {/* No Questions Found */}
            {filteredQuestions.length === 0 ? (
                <div className="bg-dark text-white p-4 rounded text-center border border-warning">
                    <p>No questions match your filters.</p>
                </div>
            ) : (
                <div className="list-group">
                    {filteredQuestions.map((question) => (
                        <div
                            key={question.id}
                            className="list-group-item bg-dark text-white border-warning"
                            onClick={() => navigate(`/admin/question-bank/${question.id}`)}
                            style={{
                                cursor: 'pointer',
                                transition: '0.3s',
                                borderRadius: '8px',
                                marginBottom: '10px'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2A2A2A'}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#1E1E1E'}
                        >
                            <div className="d-flex justify-content-between align-items-center">
                                <div>
                                    <h5 className="mb-1 text-warning">{question.title}</h5>
                                    <small className="text-muted">{question.type} • {question.points} points</small>
                                    <div className="mt-2">
                                        {question.type === 'MCQ' && question.options && (
                                            <ul className="list-unstyled">
                                                {question.options.map((option, index) => (
                                                    <li key={index} className="text-white">
                                                        <input type="radio" disabled className="me-2" /> {option}
                                                    </li>
                                                ))}
                                            </ul>
                                        )}
                                        {question.type === 'MSQ' && question.options && (
                                            <ul className="list-unstyled">
                                                {question.options.map((option, index) => (
                                                    <li key={index} className="text-white">
                                                        <input type="checkbox" disabled className="me-2" /> {option}
                                                    </li>
                                                ))}
                                            </ul>
                                        )}
                                        {question.type === 'NUMERIC' && (
                                            <input
                                                type="number"
                                                disabled
                                                placeholder="Enter numeric value"
                                                className="form-control bg-dark text-white border-warning mt-2"
                                            />
                                        )}
                                    </div>
                                </div>
                                <span className={`badge ${question.status === 'active' ? 'bg-success' : 'bg-danger'}`}>
                                    {question.status}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default QuestionList;
