import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { questionBankApi } from '../../services/apiService';
import { 
    PencilIcon, 
    TrashIcon,
    EyeIcon,
    PlusIcon,
    AdjustmentsHorizontalIcon,
    MagnifyingGlassIcon,
    QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';

const QuestionBank = () => {
    const navigate = useNavigate();
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({
        type: '',
        difficulty: '',
        search: ''
    });
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const itemsPerPage = 10;


    useEffect(() => {
        fetchQuestions();
    }, [currentPage, filters]);

    const fetchQuestions = async () => {
        try {
            setLoading(true);
            const response = await questionBankApi.getQuestions({
                page: currentPage,
                limit: itemsPerPage,
                ...filters
            });

            setQuestions(response.data || []);
            setTotalPages(Math.ceil((response.total || 0) / itemsPerPage));
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
            await questionBankApi.deleteQuestion(questionId);
            fetchQuestions(); // Refresh the list
        } catch (err) {
            console.error('Error deleting question:', err);
            setError('Failed to delete question');
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

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading questions...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4">
                    {error}
                </div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Question Bank</h1>
                <button
                    onClick={() => navigate('/admin/question-bank/new')}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                    Create Question
                </button>
            </div>

            {/* Filters */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Question Type
                        </label>
                        <select
                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
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
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Difficulty
                        </label>
                        <select
                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
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
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Search
                        </label>
                        <input
                            type="text"
                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
                            placeholder="Search questions..."
                            value={filters.search}
                            onChange={(e) => handleFilterChange('search', e.target.value)}
                        />
                    </div>
                </div>
            </div>

            {/* Questions Grid */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Question
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Type
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Difficulty
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Points
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {questions.map(question => (
                            <tr key={question.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4">
                                    <div className="text-sm text-gray-900">
                                        {question.text || question.title || 'No content'}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-500">
                                        {getQuestionTypeLabel(question.type)}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                        {
                                            'easy': 'bg-green-100 text-green-800',
                                            'medium': 'bg-yellow-100 text-yellow-800',
                                            'hard': 'bg-red-100 text-red-800'
                                        }[question.difficulty] || 'bg-gray-100 text-gray-800'
                                    }`}>
                                        {question.difficulty ? 
                                            question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1)
                                            : 'Not Set'
                                        }
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-500">
                                        {question.points || 0} pts
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button
                                        onClick={() => navigate(`/admin/question-bank/${question.id}`)}
                                        className="text-blue-600 hover:text-blue-900 mx-2"
                                        title="View"
                                    >
                                        <FaEye />
                                    </button>
                                    <button
                                        onClick={() => navigate(`/admin/question-bank/${question.id}/edit`)}
                                        className="text-indigo-600 hover:text-indigo-900 mx-2"
                                        title="Edit"
                                    >
                                        <FaEdit />
                                    </button>
                                    <button
                                        onClick={() => handleDelete(question.id)}
                                        className="text-red-600 hover:text-red-900 mx-2"
                                        title="Delete"
                                    >
                                        <FaTrash />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            <div className="flex justify-between items-center mt-6">
                <div className="text-sm text-gray-700">
                    Showing page {currentPage} of {totalPages}
                </div>
                <div className="flex space-x-2">
                    <button
                        onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                        disabled={currentPage === 1}
                        className={`px-4 py-2 border rounded-lg ${
                            currentPage === 1
                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                : 'bg-white text-gray-700 hover:bg-gray-50'
                        }`}
                    >
                        Previous
                    </button>
                    <button
                        onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                        disabled={currentPage === totalPages}
                        className={`px-4 py-2 border rounded-lg ${
                            currentPage === totalPages
                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                : 'bg-white text-gray-700 hover:bg-gray-50'
                        }`}
                    >
                        Next
                    </button>
                </div>
            </div>
        </div>
    );
};

export default QuestionBank; 