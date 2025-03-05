import React, { forwardRef } from 'react';
import PropTypes from 'prop-types';

const Input = forwardRef(({
  className = '',
  type = 'text',
  error = false,
  label,
  helperText,
  startIcon,
  endIcon,
  fullWidth = false,
  disabled = false,
  required = false,
  ...props
}, ref) => {
  const baseStyles = 'rounded-lg border bg-light-primary dark:bg-dark-primary transition-colors duration-200';
  const errorStyles = error ? 'border-brand-error text-brand-error' : 'border-light-accent dark:border-dark-accent';
  const disabledStyles = disabled ? 'opacity-50 cursor-not-allowed' : '';
  const widthStyles = fullWidth ? 'w-full' : '';
  const iconStyles = (startIcon || endIcon) ? 'pl-10' : '';

  return (
    <div className={`${widthStyles}`}>
      {label && (
        <label className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-1">
          {label}
          {required && <span className="text-brand-error ml-1">*</span>}
        </label>
      )}
      <div className="relative">
        {startIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-light-text-secondary dark:text-dark-text-secondary">
            {startIcon}
          </div>
        )}
        <input
          ref={ref}
          type={type}
          disabled={disabled}
          required={required}
          className={`
            ${baseStyles}
            ${errorStyles}
            ${disabledStyles}
            ${iconStyles}
            ${className}
            w-full px-4 py-2 text-light-text-primary dark:text-dark-text-primary
            placeholder:text-light-text-secondary dark:placeholder:text-dark-text-secondary
            focus:outline-none focus:ring-2 focus:ring-brand-primary/50
          `}
          {...props}
        />
        {endIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-light-text-secondary dark:text-dark-text-secondary">
            {endIcon}
          </div>
        )}
      </div>
      {helperText && (
        <p className={`mt-1 text-sm ${error ? 'text-brand-error' : 'text-light-text-secondary dark:text-dark-text-secondary'}`}>
          {helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

Input.propTypes = {
  className: PropTypes.string,
  type: PropTypes.string,
  error: PropTypes.bool,
  label: PropTypes.string,
  helperText: PropTypes.string,
  startIcon: PropTypes.node,
  endIcon: PropTypes.node,
  fullWidth: PropTypes.bool,
  disabled: PropTypes.bool,
  required: PropTypes.bool
};

export default Input; 