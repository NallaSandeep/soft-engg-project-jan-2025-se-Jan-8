import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { PlusCircleIcon, PencilSquareIcon, EyeIcon, TrashIcon } from '@heroicons/react/24/outline';

const QuestionBank = () => {
    const navigate = useNavigate();
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({
        type: '',
        difficulty: '',
        course_id: '',
        search: ''
    });
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchQuestions();
    }, [filters, currentPage]);

    const fetchQuestions = async () => {
        try {
            setLoading(true);
            const response = await courseApi.getQuestions({
                page: currentPage,
                ...filters
            });
            if (response.success) {
                setQuestions(response.data.items || []);
                setTotalPages(response.data.total_pages || 1);
            } else {
                setError(response.message || 'Failed to load questions');
            }
        } catch (err) {
            console.error('Error fetching questions:', err);
            setError('Failed to load questions');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (questionId) => {
        if (!window.confirm('Are you sure you want to delete this question?')) {
            return;
        }

        try {
            const response = await courseApi.deleteQuestion(questionId);
            if (response.success) {
                setQuestions(questions.filter(q => q.id !== questionId));
            } else {
                alert(response.message || 'Failed to delete question');
            }
        } catch (err) {
            console.error('Error deleting question:', err);
            alert('Failed to delete question');
        }
    };

    const handleFilterChange = (name, value) => {
        setFilters(prev => ({ ...prev, [name]: value }));
        setCurrentPage(1); // Reset to first page when filters change
    };

    const getQuestionTypeLabel = (type) => {
        const types = {
            'MCQ': 'Multiple Choice',
            'MSQ': 'Multiple Select',
            'NUMERIC': 'Numeric'
        };
        return types[type] || type;
    };

    const handleSearch = (e) => {
        e.preventDefault();
        handleFilterChange('search', searchTerm);
    };

    if (loading && questions.length === 0) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-lg p-4">
                    {error}
                </div>
            </div>
        );
    }

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Question Bank</h1>
                <button
                    onClick={() => navigate('/admin/question-bank/new')}
                    className="btn-primary flex items-center gap-2"
                >
                    <PlusCircleIcon className="h-5 w-5" />
                    <span>Create Question</span>
                </button>
            </div>

            {/* Filters */}
            <div className="glass-card p-6 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Search
                        </label>
                        <form onSubmit={handleSearch} className="flex">
                            <input
                                type="text"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                placeholder="Search questions..."
                                className="input-field rounded-r-none"
                            />
                            <button 
                                type="submit"
                                className="px-4 py-2 bg-zinc-200 dark:bg-zinc-700 text-zinc-800 dark:text-zinc-200 rounded-r-lg hover:bg-zinc-300 dark:hover:bg-zinc-600"
                            >
                                Search
                            </button>
                        </form>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Question Type
                        </label>
                        <select
                            className="input-field"
                            value={filters.type}
                            onChange={(e) => handleFilterChange('type', e.target.value)}
                        >
                            <option value="">All Types</option>
                            <option value="MCQ">Multiple Choice</option>
                            <option value="MSQ">Multiple Select</option>
                            <option value="NUMERIC">Numeric</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Difficulty
                        </label>
                        <select
                            className="input-field"
                            value={filters.difficulty}
                            onChange={(e) => handleFilterChange('difficulty', e.target.value)}
                        >
                            <option value="">All Difficulties</option>
                            <option value="easy">Easy</option>
                            <option value="medium">Medium</option>
                            <option value="hard">Hard</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Course
                        </label>
                        <select
                            className="input-field"
                            value={filters.course_id}
                            onChange={(e) => handleFilterChange('course_id', e.target.value)}
                        >
                            <option value="">All Courses</option>
                            {/* Add course options here */}
                        </select>
                    </div>
                </div>
            </div>

            {/* Questions Table */}
            <div className="glass-card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-zinc-200 dark:divide-zinc-700">
                        <thead className="bg-zinc-50 dark:bg-zinc-800">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Question
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Type
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Difficulty
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Course
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Status
                                </th>
                                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-zinc-900 divide-y divide-zinc-200 dark:divide-zinc-700">
                            {questions.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="px-6 py-4 text-center text-zinc-500 dark:text-zinc-400">
                                        No questions found. Try adjusting your filters or create a new question.
                                    </td>
                                </tr>
                            ) : (
                                questions.map(question => (
                                    <tr key={question.id} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/50">
                                        <td className="px-6 py-4">
                                            <div className="text-sm text-zinc-900 dark:text-zinc-100">
                                                {question.title || question.content || 'No content'}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-zinc-500 dark:text-zinc-400">
                                                {getQuestionTypeLabel(question.type)}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                                {
                                                    'easy': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
                                                    'medium': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
                                                    'hard': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                                                }[question.difficulty] || 'bg-zinc-100 text-zinc-800 dark:bg-zinc-700 dark:text-zinc-300'
                                            }`}>
                                                {question.difficulty ? 
                                                    question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1)
                                                    : 'Not Set'
                                                }
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-zinc-500 dark:text-zinc-400">
                                                {question.course?.name || 'Not assigned'}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                                {
                                                    'active': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
                                                    'draft': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
                                                    'inactive': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                                                }[question.status] || 'bg-zinc-100 text-zinc-800 dark:bg-zinc-700 dark:text-zinc-300'
                                            }`}>
                                                {question.status ? 
                                                    question.status.charAt(0).toUpperCase() + question.status.slice(1)
                                                    : 'Not Set'
                                                }
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <div className="flex justify-end space-x-2">
                                                <button
                                                    onClick={() => navigate(`/admin/question-bank/view/${question.id}`)}
                                                    className="text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-200"
                                                    title="View"
                                                >
                                                    <EyeIcon className="h-5 w-5" />
                                                </button>
                                                <button
                                                    onClick={() => navigate(`/admin/question-bank/edit/${question.id}`)}
                                                    className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300"
                                                    title="Edit"
                                                >
                                                    <PencilSquareIcon className="h-5 w-5" />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(question.id)}
                                                    className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300"
                                                    title="Delete"
                                                >
                                                    <TrashIcon className="h-5 w-5" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="px-6 py-3 flex items-center justify-between border-t border-zinc-200 dark:border-zinc-700">
                        <div className="flex-1 flex justify-between sm:hidden">
                            <button
                                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                                disabled={currentPage === 1}
                                className={`relative inline-flex items-center px-4 py-2 border border-zinc-300 dark:border-zinc-600 text-sm font-medium rounded-md ${
                                    currentPage === 1
                                        ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-400 dark:text-zinc-500'
                                        : 'bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800'
                                }`}
                            >
                                Previous
                            </button>
                            <button
                                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                                disabled={currentPage === totalPages}
                                className={`ml-3 relative inline-flex items-center px-4 py-2 border border-zinc-300 dark:border-zinc-600 text-sm font-medium rounded-md ${
                                    currentPage === totalPages
                                        ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-400 dark:text-zinc-500'
                                        : 'bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800'
                                }`}
                            >
                                Next
                            </button>
                        </div>
                        <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                            <div>
                                <p className="text-sm text-zinc-700 dark:text-zinc-300">
                                    Showing page <span className="font-medium">{currentPage}</span> of <span className="font-medium">{totalPages}</span>
                                </p>
                            </div>
                            <div>
                                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                                    <button
                                        onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                                        disabled={currentPage === 1}
                                        className={`relative inline-flex items-center px-2 py-2 rounded-l-md border border-zinc-300 dark:border-zinc-600 text-sm font-medium ${
                                            currentPage === 1
                                                ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-400 dark:text-zinc-500'
                                                : 'bg-white dark:bg-zinc-900 text-zinc-500 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800'
                                        }`}
                                    >
                                        <span className="sr-only">Previous</span>
                                        <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                            <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                                        </svg>
                                    </button>
                                    
                                    {/* Page numbers would go here */}
                                    <span className="relative inline-flex items-center px-4 py-2 border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-900 text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                        {currentPage}
                                    </span>
                                    
                                    <button
                                        onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                                        disabled={currentPage === totalPages}
                                        className={`relative inline-flex items-center px-2 py-2 rounded-r-md border border-zinc-300 dark:border-zinc-600 text-sm font-medium ${
                                            currentPage === totalPages
                                                ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-400 dark:text-zinc-500'
                                                : 'bg-white dark:bg-zinc-900 text-zinc-500 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800'
                                        }`}
                                    >
                                        <span className="sr-only">Next</span>
                                        <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                                        </svg>
                                    </button>
                                </nav>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default QuestionBank; 