const renderQuestion = (question, index) => {
    return (
        <div key={question.id} className="p-6 border-b border-gray-200 last:border-b-0">
            <div className="flex justify-between items-start">
                <div>
                    <h3 className="font-medium text-gray-900">
                        Question {index + 1}: {question.title}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                        {question.type} • {question.points} points
                    </p>
                </div>
                <button
                    onClick={() => handleRemoveQuestion(question.id)}
                    className="text-red-600 hover:text-red-800"
                    title="Remove Question"
                >
                    <FaTrash />
                </button>
            </div>
            <div className="mt-4">
                <p className="text-gray-700">{question.content}</p>
                {question.type === 'MCQ' && Array.isArray(question.options) && (
                    <div className="mt-4 space-y-2">
                        {question.options.map((option, optionIndex) => (
                            <div key={optionIndex} className="flex items-center gap-2">
                                <input
                                    type="radio"
                                    disabled
                                    className="text-blue-600"
                                />
                                <span>{option}</span>
                            </div>
                        ))}
                    </div>
                )}
                {question.type === 'MSQ' && Array.isArray(question.options) && (
                    <div className="mt-4 space-y-2">
                        {question.options.map((option, optionIndex) => (
                            <div key={optionIndex} className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    disabled
                                    className="text-blue-600"
                                />
                                <span>{option}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}; 