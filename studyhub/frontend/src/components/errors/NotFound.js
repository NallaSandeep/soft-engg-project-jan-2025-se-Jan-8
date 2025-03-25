import React from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../common/Card';

export default function NotFound() {
    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900">
            <div className="max-w-5xl mx-auto p-4 lg:px-8">
                <Card className="text-center p-8">
                    <div className="space-y-6">
                        <h1 className="text-6xl font-bold text-zinc-900 dark:text-white">404</h1>
                        <h2 className="text-2xl font-semibold text-zinc-800 dark:text-zinc-200">
                            Page Not Found
                        </h2>
                        <p className="text-zinc-600 dark:text-zinc-400 max-w-md mx-auto">
                            The page you're looking for doesn't exist or has been moved.
                        </p>
                        <div className="pt-4">
                            <Link
                                to="/student/dashboard"
                                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
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