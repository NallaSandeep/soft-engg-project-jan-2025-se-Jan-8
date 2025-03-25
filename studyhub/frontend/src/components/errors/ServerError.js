import React from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../common/Card';

export default function ServerError() {
    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900">
            <div className="max-w-5xl mx-auto p-4 lg:px-8">
                <Card className="text-center p-8">
                    <div className="space-y-6">
                        <h1 className="text-6xl font-bold text-zinc-900 dark:text-white">500</h1>
                        <h2 className="text-2xl font-semibold text-zinc-800 dark:text-zinc-200">
                            Server Error
                        </h2>
                        <p className="text-zinc-600 dark:text-zinc-400 max-w-md mx-auto">
                            Something went wrong on our end. Please try again later or contact support if the problem persists.
                        </p>
                        <div className="pt-4 space-x-4">
                            <button
                                onClick={() => window.location.reload()}
                                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                                Try Again
                            </button>
                            <Link
                                to="/student/dashboard"
                                className="inline-flex items-center px-4 py-2 border border-zinc-300 dark:border-zinc-600 text-sm font-medium rounded-md text-zinc-700 dark:text-zinc-300 bg-white dark:bg-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                                Return to Dashboard
                            </Link>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
} 