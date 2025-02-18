import React, { forwardRef } from 'react';
import PropTypes from 'prop-types';

const TextArea = forwardRef(({
  className = '',
  error = false,
  label,
  helperText,
  fullWidth = false,
  disabled = false,
  required = false,
  rows = 4,
  ...props
}, ref) => {
  const baseStyles = 'rounded-lg border bg-light-primary dark:bg-dark-primary transition-colors duration-200';
  const errorStyles = error ? 'border-brand-error text-brand-error' : 'border-light-accent dark:border-dark-accent';
  const disabledStyles = disabled ? 'opacity-50 cursor-not-allowed' : '';
  const widthStyles = fullWidth ? 'w-full' : '';

  return (
    <div className={`${widthStyles}`}>
      {label && (
        <label className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-1">
          {label}
          {required && <span className="text-brand-error ml-1">*</span>}
        </label>
      )}
      <textarea
        ref={ref}
        rows={rows}
        disabled={disabled}
        required={required}
        className={`
          ${baseStyles}
          ${errorStyles}
          ${disabledStyles}
          ${className}
          w-full px-4 py-2 text-light-text-primary dark:text-dark-text-primary
          placeholder:text-light-text-secondary dark:placeholder:text-dark-text-secondary
          focus:outline-none focus:ring-2 focus:ring-brand-primary/50
          resize-vertical
        `}
        {...props}
      />
      {helperText && (
        <p className={`mt-1 text-sm ${error ? 'text-brand-error' : 'text-light-text-secondary dark:text-dark-text-secondary'}`}>
          {helperText}
        </p>
      )}
    </div>
  );
});

TextArea.displayName = 'TextArea';

TextArea.propTypes = {
  className: PropTypes.string,
  error: PropTypes.bool,
  label: PropTypes.string,
  helperText: PropTypes.string,
  fullWidth: PropTypes.bool,
  disabled: PropTypes.bool,
  required: PropTypes.bool,
  rows: PropTypes.number
};

export default TextArea; 