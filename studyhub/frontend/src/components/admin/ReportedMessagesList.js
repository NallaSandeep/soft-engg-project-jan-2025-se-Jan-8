import React, { useState, useEffect } from 'react';
import { chatAPI } from '../../services/chatService';
import { EyeIcon, ExclamationTriangleIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

const ReportedMessagesList = () => {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({
        status: '',
    });
    const [selectedReport, setSelectedReport] = useState(null);
    const [showModal, setShowModal] = useState(false);

    const filteredReports = reports
    .sort((a, b) => {
        if (a.status === 'pending' && b.status !== 'pending') return -1;
        if (a.status !== 'pending' && b.status === 'pending') return 1;
        return new Date(b.reported_at) - new Date(a.reported_at);
    })
    .filter(report => !filters.status || report.status === filters.status);

    useEffect(() => {
        fetchReports();
    }, [filters]);

    const truncateText = (text, maxLength = 100) => {
        if (text.length <= maxLength) return text;
        return text.slice(0, maxLength) + '...';
    };

    const fetchReports = async () => {
        try {
            setLoading(true);
            const response = await chatAPI.getReportedMessages(filters);
            console.log(response)
            if (response) {
                const res = response.map(report => ({
                    id: report.report_id,
                    reported_at: report.report_timestamp || new Date().toISOString(),
                    status: report.status || 'pending',
                    message_content: report.message || 'No message content available',
                    reporter_name: report.user_id || 'Unknown',
                }));
                const sortedReports = [...res].sort((a, b) => {
                    if (a.status === 'pending' && b.status !== 'pending') return -1;
                    if (a.status !== 'pending' && b.status === 'pending') return 1;
                    return new Date(b.reported_at) - new Date(a.reported_at);
                });
                setReports(sortedReports || []);
            } else {
                setError(response.message || 'Failed to load reported messages');
            }
        } catch (err) {
            console.error('Error fetching reports:', err);
            setError('Failed to load reported messages');
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (name, value) => {
        setFilters(prev => ({ ...prev, [name]: value }));
        
    };

    const handleResolve = async (reportId, action) => {
        try {
            await chatAPI.updateReport(reportId, {
                    op: "replace", 
                    path: "/status", 
                    value: action
                  });
            fetchReports();
        } catch (error) {
            console.error('Error resolving report:', error);
        }
    };

    if (loading && reports.length === 0) {
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
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Reported Messages</h1>
            </div>

            {/* Filters */}
            <div className="glass-card p-6 mb-6">
                <div>
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                        Filter by Status
                    </label>
                    <div className="flex flex-wrap gap-2">
                        <button
                            onClick={() => handleFilterChange('status', '')}
                            className={`px-3 py-1.5 text-sm font-medium rounded-full transition-colors ${
                                filters.status === ''
                                    ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900'
                                    : 'bg-zinc-100 text-zinc-700 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700'
                            }`}
                        >
                            All
                        </button>
                        <button
                            onClick={() => handleFilterChange('status', 'pending')}
                            className={`px-3 py-1.5 text-sm font-medium rounded-full transition-colors ${
                                filters.status === 'pending'
                                    ? 'bg-yellow-500 text-white'
                                    : 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:hover:bg-yellow-900/50'
                            }`}
                        >
                            Pending
                        </button>
                        <button
                            onClick={() => handleFilterChange('status', 'reviewed')}
                            className={`px-3 py-1.5 text-sm font-medium rounded-full transition-colors ${
                                filters.status === 'reviewed'
                                    ? 'bg-green-500 text-white'
                                    : 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400 dark:hover:bg-green-900/50'
                            }`}
                        >
                            Reviewed
                        </button>
                        <button
                            onClick={() => handleFilterChange('status', 'dismissed')}
                            className={`px-3 py-1.5 text-sm font-medium rounded-full transition-colors ${
                                filters.status === 'dismissed'
                                    ? 'bg-zinc-500 text-white'
                                    : 'bg-zinc-100 text-zinc-700 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700'
                            }`}
                        >
                            Dismissed
                        </button>
                    </div>
                </div>
            </div>

            {/* Reports Table */}
            <div className="glass-card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-zinc-200 dark:divide-zinc-700">
                        <thead className="bg-zinc-50 dark:bg-zinc-800">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    User ID
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Message
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Status
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Reported At
                                </th>
                                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-zinc-900 divide-y divide-zinc-200 dark:divide-zinc-700">
                            {filteredReports.length === 0 ? (
                                <tr>
                                    <td colSpan="5" className="px-6 py-4 text-center text-zinc-500 dark:text-zinc-400">
                                        No reported messages found.
                                    </td>
                                </tr>
                            ) : (
                                filteredReports.map(report => (
                                    <tr key={report.id} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/50">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-zinc-900 dark:text-white">
                                                {report.reporter_name}
                                            </div>
                                            <div className="text-xs text-zinc-500 dark:text-zinc-400">
                                                {report.reporter_email}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="text-sm text-zinc-500 dark:text-zinc-400">
                                                {truncateText(report.message_content)}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                                {
                                                    'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
                                                    'reviewed': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
                                                    'dismissed': 'bg-zinc-100 text-zinc-800 dark:bg-zinc-700 dark:text-zinc-300'
                                                }[report.status]
                                            }`}>
                                                {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-500 dark:text-zinc-400">
                                            {new Date(report.reported_at).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <div className="flex justify-end space-x-2">
                                                <button
                                                    onClick={() => {
                                                        setSelectedReport(report);
                                                        setShowModal(true);
                                                    }}
                                                    className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300"
                                                    title="View Details"
                                                >
                                                    <EyeIcon className="h-5 w-5" />
                                                </button>
                                                {report.status === 'pending' && (
                                                    <>
                                                        <button
                                                            onClick={() => handleResolve(report.id, 'reviewed')}
                                                            className="text-green-600 dark:text-green-400 hover:text-green-900 dark:hover:text-green-300"
                                                            title="Resolve"
                                                        >
                                                            <CheckCircleIcon className="h-5 w-5" />
                                                        </button>
                                                        <button
                                                            onClick={() => handleResolve(report.id, 'dismissed')}
                                                            className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300"
                                                            title="Dismiss"
                                                        >
                                                            <XCircleIcon className="h-5 w-5" />
                                                        </button>
                                                    </>
                                                )}
                                        </div>
                                    </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
            {showModal && selectedReport && (
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center" onClick={() => setShowModal(false)}>
                <div className="bg-white dark:bg-zinc-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                    <div className="p-6">
                        <div className="flex justify-between items-start mb-4">
                            <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">
                                Reported Message Details
                            </h2>
                            <button
                                onClick={() => setShowModal(false)}
                                className="text-zinc-400 hover:text-zinc-500 dark:hover:text-zinc-300"
                            >
                                <XCircleIcon className="h-6 w-6" />
                            </button>
                        </div>
                        
                        <div className="space-y-4">
                            <div>
                                <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">
                                    Reported By
                                </h3>
                                <p className="text-zinc-900 dark:text-white">
                                    {selectedReport.reporter_name}
                                </p>
                                <p className="text-sm text-zinc-500 dark:text-zinc-400">
                                    {selectedReport.reporter_email}
                                </p>
                            </div>

                            <div>
                                <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">
                                    Message Content
                                </h3>
                                <div className="bg-zinc-50 dark:bg-zinc-900 rounded-lg p-4">
                                    <p className="text-zinc-900 dark:text-white whitespace-pre-wrap">
                                        {selectedReport.message_content}
                                    </p>
                                </div>
                            </div>

                            <div className="flex justify-between items-center">
                                <div>
                                    <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">
                                        Status
                                    </h3>
                                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                        {
                                            'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
                                            'resolved': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
                                            'dismissed': 'bg-zinc-100 text-zinc-800 dark:bg-zinc-700 dark:text-zinc-300'
                                        }[selectedReport.status]
                                    }`}>
                                        {selectedReport.status.charAt(0).toUpperCase() + selectedReport.status.slice(1)}
                                    </span>
                                </div>
                                <div className="text-sm text-zinc-500 dark:text-zinc-400">
                                    Reported on {new Date(selectedReport.reported_at).toLocaleString()}
                                </div>
                            </div>

                            {selectedReport.status === 'pending' && (
                                <div className="flex justify-end space-x-2 mt-6 pt-4 border-t border-zinc-200 dark:border-zinc-700">
                                    <button
                                        onClick={() => {
                                            handleResolve(selectedReport.id, 'reviewed');
                                            setShowModal(false);
                                        }}
                                        className="btn-success"
                                    >
                                        Resolve Report
                                    </button>
                                    <button
                                        onClick={() => {
                                            handleResolve(selectedReport.id, 'dismissed');
                                            setShowModal(false);
                                        }}
                                        className="btn-danger"
                                    >
                                        Dismiss Report
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        )}
        </div>
    );
};

export default ReportedMessagesList;