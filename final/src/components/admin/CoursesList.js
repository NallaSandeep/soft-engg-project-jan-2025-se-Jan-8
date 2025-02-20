import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    AcademicCapIcon,
    PencilSquareIcon,
    BookOpenIcon,
    PlusIcon,
    CheckCircleIcon,
    XCircleIcon
} from '@heroicons/react/24/outline';

const mockCourses = [
    { id: 1, name: 'Introduction to Programming', code: 'CS101', enrolled_count: 5, max_students: 30, is_active: true },
    { id: 2, name: 'Data Structures', code: 'CS102', enrolled_count: 5, max_students: 25, is_active: true },
    { id: 3, name: 'Introduction to ML', code: 'ML101', enrolled_count: 5, max_students: 50, is_active: true }
];

const CoursesList = () => {
    const navigate = useNavigate();
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchCourses();
    }, []);

    const fetchCourses = async () => {
        try {
            await new Promise(resolve => setTimeout(resolve, 1000));
            setCourses(mockCourses);
        } catch (err) {
            setError('Failed to load courses');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen bg-zinc-100 dark:bg-zinc-900">
                <div className="text-zinc-600 dark:text-zinc-400">Loading courses...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 text-red-500 dark:text-red-400 text-center">
                {error}
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-100 dark:bg-zinc-900">
            <div className="max-w-7xl mx-auto space-y-8 p-6">
                {/* Header */}
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-zinc-900 dark:text-white">
                            Courses
                        </h1>
                        <p className="mt-2 text-zinc-600 dark:text-zinc-400">
                            Manage your platform's courses
                        </p>
                    </div>
                    <button
                        onClick={() => navigate('/admin/courses/new')}
                        className="flex items-center space-x-2 px-4 py-2 rounded-lg
                                 bg-zinc-800 dark:bg-white
                                 text-white dark:text-zinc-900
                                 hover:bg-zinc-700 dark:hover:bg-zinc-100
                                 transition-colors duration-200"
                    >
                        <PlusIcon className="h-5 w-5" />
                        <span>Create Course</span>
                    </button>
                </div>

                {/* Courses List */}
                <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl 
                              shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                              dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-zinc-200 dark:border-zinc-700">
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Course</th>
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Code</th>
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Students</th>
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Status</th>
                                    <th className="text-right p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {courses.map(course => (
                                    <tr
                                        key={course.id}
                                        onClick={() => navigate(`/admin/courses/${course.id}/content`)}
                                        className="border-b border-zinc-200 dark:border-zinc-700 last:border-0
                                                 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 cursor-pointer
                                                 transition-colors duration-200"
                                    >
                                        <td className="p-4">
                                            <div className="flex items-center space-x-3">
                                                <BookOpenIcon className="h-5 w-5 text-zinc-400 dark:text-zinc-500" />
                                                <span className="font-medium text-zinc-900 dark:text-white">
                                                    {course.name}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="p-4 text-zinc-600 dark:text-zinc-400">
                                            {course.code}
                                        </td>
                                        <td className="p-4 text-zinc-600 dark:text-zinc-400">
                                            {course.enrolled_count} / {course.max_students}
                                        </td>
                                        <td className="p-4">
                                            <div className="flex items-center space-x-2">
                                                {course.is_active ? (
                                                    <>
                                                        <CheckCircleIcon className="h-5 w-5 text-emerald-500" />
                                                        <span className="text-emerald-500">Active</span>
                                                    </>
                                                ) : (
                                                    <>
                                                        <XCircleIcon className="h-5 w-5 text-red-500" />
                                                        <span className="text-red-500">Inactive</span>
                                                    </>
                                                )}
                                            </div>
                                        </td>
                                        <td className="p-4 text-right">
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    navigate(`/admin/courses/${course.id}/edit`);
                                                }}
                                                className="p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-700
                                                         text-zinc-600 dark:text-zinc-400
                                                         transition-colors duration-200"
                                            >
                                                <PencilSquareIcon className="h-5 w-5" />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CoursesList;