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
                        className="w-full pl-10 pr-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-600 focus:outline-none focus:border-blue-500 bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                    />
                    <FaSearch className="absolute left-3 top-3 text-zinc-400 dark:text-zinc-500" />
                </div>

                <div className="flex items-center ml-4">
                    <button
                        onClick={() => onFilterChange({ favorite: !filters.favorite })}
                        className={`p-2 rounded-lg mr-2 ${
                            filters.favorite ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400' : 'bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-400'
                        }`}
                    >
                        <FaStar />
                    </button>

                    <Menu as="div" className="relative">
                        <Menu.Button
                            className={`p-2 rounded-lg ${
                                showFilters ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' : 'bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-400'
                            }`}
                        >
                            <FaFilter />
                        </Menu.Button>

                        <Menu.Items className="absolute right-0 mt-2 w-64 bg-white dark:bg-zinc-800 rounded-lg shadow-lg z-10 p-4 border border-zinc-200 dark:border-zinc-700">
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                                    Importance
                                </label>
                                <div className="flex space-x-2">
                                    {[1, 2, 3, 4, 5].map((level) => (
                                        <button
                                            key={level}
                                            onClick={() => handleImportanceChange(level)}
                                            className={`w-8 h-8 rounded-full flex items-center justify-center ${
                                                filters.importance === level
                                                    ? 'bg-blue-600 dark:bg-blue-700 text-white'
                                                    : 'bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-400'
                                            }`}
                                        >
                                            {level}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                                    Tags
                                </label>
                                <input
                                    type="text"
                                    value={filters.tags.join(', ')}
                                    onChange={handleTagsChange}
                                    placeholder="Enter tags, separated by commas"
                                    className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg focus:outline-none focus:border-blue-500 bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
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
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300">
                            <FaStar className="mr-1" /> Favorites
                            <button
                                onClick={() => onFilterChange({ favorite: false })}
                                className="ml-2 text-yellow-600 dark:text-yellow-400 hover:text-yellow-800 dark:hover:text-yellow-300"
                            >
                                ×
                            </button>
                        </span>
                    )}

                    {filters.importance && (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300">
                            Importance: {filters.importance}
                            <button
                                onClick={() => onFilterChange({ importance: null })}
                                className="ml-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                            >
                                ×
                            </button>
                        </span>
                    )}

                    {filters.tags.map((tag) => (
                        <span
                            key={tag}
                            className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-zinc-100 dark:bg-zinc-700 text-zinc-800 dark:text-zinc-300"
                        >
                            #{tag}
                            <button
                                onClick={() =>
                                    onFilterChange({
                                        tags: filters.tags.filter((t) => t !== tag)
                                    })
                                }
                                className="ml-2 text-zinc-600 dark:text-zinc-400 hover:text-zinc-800 dark:hover:text-zinc-300"
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
                        className="text-sm text-zinc-600 dark:text-zinc-400 hover:text-zinc-800 dark:hover:text-zinc-300"
                    >
                        Clear all filters
                    </button>
                </div>
            )}
        </div>
    );
};

export default SearchBar; 