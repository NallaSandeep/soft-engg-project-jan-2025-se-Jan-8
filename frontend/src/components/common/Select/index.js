import React, { forwardRef } from 'react';
import PropTypes from 'prop-types';

const Select = forwardRef(({
  className = '',
  options = [],
  error,
  label,
  helperText,
  fullWidth = false,
  disabled = false,
  required = false,
  placeholder = 'Select an option',
  value,
  onChange,
  ...props
}, ref) => {
  const baseStyles = 'rounded-lg border transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const getSelectStyles = () => {
    const styles = [
      baseStyles,
      'bg-light-primary dark:bg-dark-primary',
      'text-light-text-primary dark:text-dark-text-primary',
      'border-light-accent dark:border-dark-accent',
      'focus:border-brand-primary dark:focus:border-brand-primary',
      'focus:ring-brand-primary/50',
      'appearance-none'
    ];

    if (error) {
      styles.push('border-brand-error focus:border-brand-error focus:ring-brand-error/50');
    }

    if (disabled) {
      styles.push('opacity-50 cursor-not-allowed bg-light-accent dark:bg-dark-accent');
    }

    if (fullWidth) {
      styles.push('w-full');
    }

    return styles.join(' ');
  };

  const renderLabel = () => {
    if (!label) return null;
    return (
      <label 
        className={`block mb-2 text-sm font-medium ${
          error 
            ? 'text-brand-error' 
            : 'text-light-text-primary dark:text-dark-text-primary'
        }`}
      >
        {label}
        {required && <span className="text-brand-error ml-1">*</span>}
      </label>
    );
  };

  const renderHelperText = () => {
    if (!helperText && !error) return null;
    return (
      <p 
        className={`mt-1 text-sm ${
          error 
            ? 'text-brand-error' 
            : 'text-light-text-secondary dark:text-dark-text-secondary'
        }`}
      >
        {error || helperText}
      </p>
    );
  };

  return (
    <div className={`relative ${fullWidth ? 'w-full' : ''}`}>
      {renderLabel()}
      <div className="relative">
        <select
          ref={ref}
          value={value}
          onChange={onChange}
          className={`${getSelectStyles()} pr-10 ${className}`}
          disabled={disabled}
          required={required}
          aria-invalid={error ? 'true' : 'false'}
          {...props}
        >
          <option value="" disabled>
            {placeholder}
          </option>
          {options.map((option) => (
            <option 
              key={option.value} 
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>
        <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
          <svg
            className="w-5 h-5 text-light-text-secondary dark:text-dark-text-secondary"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </div>
      </div>
      {renderHelperText()}
    </div>
  );
});

Select.displayName = 'Select';

Select.propTypes = {
  className: PropTypes.string,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      label: PropTypes.string.isRequired,
      disabled: PropTypes.bool
    })
  ).isRequired,
  error: PropTypes.string,
  label: PropTypes.string,
  helperText: PropTypes.string,
  fullWidth: PropTypes.bool,
  disabled: PropTypes.bool,
  required: PropTypes.bool,
  placeholder: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func
};

export default Select;

// MultiSelect variant
export const MultiSelect = forwardRef(({
  value = [],
  onChange,
  ...props
}, ref) => {
  const handleChange = (e) => {
    const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
    onChange?.(selectedOptions);
  };

  return (
    <Select
      ref={ref}
      multiple
      value={value}
      onChange={handleChange}
      className="min-h-[100px]"
      {...props}
    />
  );
});

MultiSelect.displayName = 'MultiSelect';

MultiSelect.propTypes = {
  value: PropTypes.arrayOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number])),
  onChange: PropTypes.func,
  ...Select.propTypes
}; 