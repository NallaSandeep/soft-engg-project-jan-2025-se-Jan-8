import React, { useState } from 'react';
import { FaSearch, FaStar, FaFilter } from 'react-icons/fa';
import { Menu } from '@headlessui/react';

const SearchBar = ({ value, onChange, filters, onFilterChange }) => {
    const [showFilters, setShowFilters] = useState(false);

    const handleImportanceChange = (importance) => {
        onFilterChange({ importance: importance === filters.importance ? null : importance });
    };

    const handleTagsChange = (e) => {
        const tags = e.target.value.split(',').map(tag => tag.trim()).filter(Boolean);
        onFilterChange({ tags });
    };

    return (
        <div className="relative">
            <div className="flex items-center mb-4">
                <div className="flex-1 relative">
                    <input
                        type="text"
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                        placeholder="Search documents..."
                        className="w-full pl-10 pr-4 py-2 rounded-lg border focus:outline-none focus:border-blue-500"
                    />
                    <FaSearch className="absolute left-3 top-3 text-gray-400" />
                </div>

                <div className="flex items-center ml-4">
                    <button
                        onClick={() => onFilterChange({ favorite: !filters.favorite })}
                        className={`p-2 rounded-lg mr-2 ${
                            filters.favorite ? 'bg-yellow-100 text-yellow-600' : 'bg-gray-100 text-gray-600'
                        }`}
                    >
                        <FaStar />
                    </button>

                    <Menu as="div" className="relative">
                        <Menu.Button
                            className={`p-2 rounded-lg ${
                                showFilters ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                            }`}
                        >
                            <FaFilter />
                        </Menu.Button>

                        <Menu.Items className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg z-10 p-4">
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Importance
                                </label>
                                <div className="flex space-x-2">
                                    {[1, 2, 3, 4, 5].map((level) => (
                                        <button
                                            key={level}
                                            onClick={() => handleImportanceChange(level)}
                                            className={`w-8 h-8 rounded-full flex items-center justify-center ${
                                                filters.importance === level
                                                    ? 'bg-blue-600 text-white'
                                                    : 'bg-gray-100 text-gray-600'
                                            }`}
                                        >
                                            {level}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Tags
                                </label>
                                <input
                                    type="text"
                                    value={filters.tags.join(', ')}
                                    onChange={handleTagsChange}
                                    placeholder="Enter tags, separated by commas"
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500"
                                />
                            </div>
                        </Menu.Items>
                    </Menu>
                </div>
            </div>

            {/* Active Filters */}
            {(filters.importance || filters.tags.length > 0 || filters.favorite) && (
                <div className="flex flex-wrap gap-2 mb-4">
                    {filters.favorite && (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-yellow-100 text-yellow-800">
                            <FaStar className="mr-1" /> Favorites
                            <button
                                onClick={() => onFilterChange({ favorite: false })}
                                className="ml-2 text-yellow-600 hover:text-yellow-800"
                            >
                                ×
                            </button>
                        </span>
                    )}

                    {filters.importance && (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
                            Importance: {filters.importance}
                            <button
                                onClick={() => onFilterChange({ importance: null })}
                                className="ml-2 text-blue-600 hover:text-blue-800"
                            >
                                ×
                            </button>
                        </span>
                    )}

                    {filters.tags.map((tag) => (
                        <span
                            key={tag}
                            className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-800"
                        >
                            #{tag}
                            <button
                                onClick={() =>
                                    onFilterChange({
                                        tags: filters.tags.filter((t) => t !== tag)
                                    })
                                }
                                className="ml-2 text-gray-600 hover:text-gray-800"
                            >
                                ×
                            </button>
                        </span>
                    ))}

                    <button
                        onClick={() =>
                            onFilterChange({
                                favorite: false,
                                importance: null,
                                tags: []
                            })
                        }
                        className="text-sm text-gray-600 hover:text-gray-800"
                    >
                        Clear all filters
                    </button>
                </div>
            )}
        </div>
    );
};

export default SearchBar; 