import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { toast } from 'react-hot-toast';

const QuestionForm = ({ mode = 'create' }) => {
    const navigate = useNavigate();
    const { questionId } = useParams();
    const isEditMode = mode === 'edit';
    const isViewMode = mode === 'view';

    const [loading, setLoading] = useState(isEditMode || isViewMode);
    const [error, setError] = useState(null);
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [selectedWeek, setSelectedWeek] = useState(null);
    const [formData, setFormData] = useState({
        title: '',
        content: '',
        type: 'MCQ',
        options: ['', '', '', ''],
        correct_answer: { answer: 0 },
        points: 2,
        difficulty: 'medium',
        explanation: '',
        course_id: '',
        week_id: '',
        lecture_id: ''
    });

    useEffect(() => {
        fetchCourses();
        if (isEditMode || isViewMode) {
            fetchQuestion();
        }
    }, [questionId]);

    const fetchCourses = async () => {
        try {
            const response = await courseApi.getCourses();
            if (response.success) {
                setCourses(response.data || []);
            }
        } catch (err) {
            console.error('Error fetching courses:', err);
        }
    };

    const fetchQuestion = async () => {
        try {
            const response = await courseApi.getQuestion(questionId);
            if (response.success) {
                const question = response.data;
                setFormData({
                    title: question.title,
                    content: question.content,
                    type: question.type,
                    options: JSON.parse(question.options),
                    correct_answer: JSON.parse(question.correct_answer),
                    points: question.points,
                    difficulty: question.difficulty,
                    explanation: question.explanation,
                    course_id: question.course_id,
                    week_id: question.week_id,
                    lecture_id: question.lecture_id
                });
                // Find and set the course and week
                const course = courses.find(c => c.id === question.course_id);
                if (course) {
                    setSelectedCourse(course);
                    const week = course.weeks?.find(w => w.id === question.week_id);
                    if (week) {
                        setSelectedWeek(week);
                    }
                }
            } else {
                setError(response.message || 'Failed to load question');
            }
        } catch (err) {
            console.error('Error fetching question:', err);
            setError('Failed to load question');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleOptionChange = (index, value) => {
        setFormData(prev => ({
            ...prev,
            options: prev.options.map((opt, i) => i === index ? value : opt)
        }));
    };

    const handleCorrectAnswerChange = (value) => {
        setFormData(prev => ({
            ...prev,
            correct_answer: { answer: value }
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (isViewMode) return;
        
        setError(null);

        try {
            const questionData = {
                ...formData,
                options: JSON.stringify(formData.options),
                correct_answer: JSON.stringify(formData.correct_answer)
            };

            const response = isEditMode
                ? await courseApi.updateQuestion(questionId, questionData)
                : await courseApi.createQuestion(questionData);

            if (response.success) {
                toast.success(`Question ${isEditMode ? 'updated' : 'created'} successfully!`);
                navigate('/admin/question-bank');
            } else {
                setError(response.message || `Failed to ${isEditMode ? 'update' : 'create'} question`);
            }
        } catch (err) {
            console.error('Error saving question:', err);
            setError(err.message || `Failed to ${isEditMode ? 'update' : 'create'} question`);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading question...</div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="max-w-3xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold text-gray-900">
                        {isViewMode ? 'View Question' : isEditMode ? 'Edit Question' : 'Create Question'}
                    </h1>
                    <button
                        onClick={() => navigate('/admin/question-bank')}
                        className="text-gray-600 hover:text-gray-800"
                    >
                        Cancel
                    </button>
                </div>

                {error && (
                    <div className="mb-6 bg-red-50 border border-red-200 text-red-600 rounded-lg p-4">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="grid grid-cols-1 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Title
                                </label>
                                <input
                                    type="text"
                                    name="title"
                                    value={formData.title}
                                    onChange={handleChange}
                                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                    required
                                    disabled={isViewMode}
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Question Text
                                </label>
                                <textarea
                                    name="content"
                                    value={formData.content}
                                    onChange={handleChange}
                                    rows={4}
                                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                    required
                                    disabled={isViewMode}
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Question Type
                                    </label>
                                    <select
                                        name="type"
                                        value={formData.type}
                                        onChange={handleChange}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        disabled={isViewMode}
                                    >
                                        <option value="MCQ">Multiple Choice</option>
                                        <option value="MSQ">Multiple Select</option>
                                        <option value="NUMERIC">Numeric</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Points
                                    </label>
                                    <input
                                        type="number"
                                        name="points"
                                        value={formData.points}
                                        onChange={handleChange}
                                        min={1}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        required
                                        disabled={isViewMode}
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Difficulty
                                    </label>
                                    <select
                                        name="difficulty"
                                        value={formData.difficulty}
                                        onChange={handleChange}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        disabled={isViewMode}
                                    >
                                        <option value="easy">Easy</option>
                                        <option value="medium">Medium</option>
                                        <option value="hard">Hard</option>
                                    </select>
                                </div>
                            </div>

                            {formData.type !== 'NUMERIC' && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Options
                                    </label>
                                    <div className="space-y-3">
                                        {formData.options.map((option, index) => (
                                            <div key={index} className="flex items-center space-x-3">
                                                <input
                                                    type={formData.type === 'MCQ' ? 'radio' : 'checkbox'}
                                                    name="correct_answer"
                                                    checked={
                                                        formData.type === 'MCQ'
                                                            ? formData.correct_answer.answer === index
                                                            : formData.correct_answer.answer.includes(index)
                                                    }
                                                    onChange={() => handleCorrectAnswerChange(index)}
                                                    className="h-4 w-4"
                                                    disabled={isViewMode}
                                                />
                                                <input
                                                    type="text"
                                                    value={option}
                                                    onChange={(e) => handleOptionChange(index, e.target.value)}
                                                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2"
                                                    placeholder={`Option ${index + 1}`}
                                                    required
                                                    disabled={isViewMode}
                                                />
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Explanation
                                </label>
                                <textarea
                                    name="explanation"
                                    value={formData.explanation}
                                    onChange={handleChange}
                                    rows={3}
                                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                    placeholder="Explain the correct answer..."
                                    disabled={isViewMode}
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Course
                                    </label>
                                    <select
                                        name="course_id"
                                        value={formData.course_id}
                                        onChange={(e) => {
                                            const course = courses.find(c => c.id === parseInt(e.target.value));
                                            setSelectedCourse(course);
                                            setSelectedWeek(null);
                                            setFormData(prev => ({
                                                ...prev,
                                                course_id: e.target.value,
                                                week_id: '',
                                                lecture_id: ''
                                            }));
                                        }}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        required
                                        disabled={isViewMode}
                                    >
                                        <option value="">Select Course</option>
                                        {courses.map(course => (
                                            <option key={course.id} value={course.id}>
                                                {course.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Week
                                    </label>
                                    <select
                                        name="week_id"
                                        value={formData.week_id}
                                        onChange={(e) => {
                                            const week = selectedCourse?.weeks?.find(w => w.id === parseInt(e.target.value));
                                            setSelectedWeek(week);
                                            setFormData(prev => ({
                                                ...prev,
                                                week_id: e.target.value,
                                                lecture_id: ''
                                            }));
                                        }}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        required
                                        disabled={!selectedCourse || isViewMode}
                                    >
                                        <option value="">Select Week</option>
                                        {selectedCourse?.weeks?.map(week => (
                                            <option key={week.id} value={week.id}>
                                                Week {week.number}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Lecture
                                    </label>
                                    <select
                                        name="lecture_id"
                                        value={formData.lecture_id}
                                        onChange={handleChange}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        required
                                        disabled={!selectedWeek || isViewMode}
                                    >
                                        <option value="">Select Lecture</option>
                                        {selectedWeek?.lectures?.map(lecture => (
                                            <option key={lecture.id} value={lecture.id}>
                                                {lecture.title}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>

                    {!isViewMode && (
                        <div className="flex justify-end space-x-4">
                            <button
                                type="button"
                                onClick={() => navigate('/admin/question-bank')}
                                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                                {isEditMode ? 'Update Question' : 'Create Question'}
                            </button>
                        </div>
                    )}
                </form>
            </div>
        </div>
    );
};

export default QuestionForm; 