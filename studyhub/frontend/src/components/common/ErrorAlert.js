import React from 'react';

const ErrorAlert = ({ message }) => {
    return (
        <div className="rounded-md bg-red-50 p-4">
            <div className="flex">
                <div className="flex-shrink-0">
                    <span className="text-red-400">⚠</span>
                </div>
                <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Error</h3>
                    <div className="mt-2 text-sm text-red-700">
                        <p>{message}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ErrorAlert; 