import React from 'react';
import PropTypes from 'prop-types';

const Button = ({
  children,
  className = '',
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  icon,
  onClick,
  type = 'button',
  fullWidth = false,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variants = {
    primary: `
      bg-blue-600 dark:bg-blue-700
      hover:bg-blue-700 dark:hover:bg-blue-600
      text-white
      focus:ring-4 focus:ring-blue-500/30
      active:bg-blue-800 dark:active:bg-blue-500
    `,
    secondary: `
      bg-gray-200 dark:bg-gray-700
      hover:bg-gray-300 dark:hover:bg-gray-600
      text-gray-800 dark:text-gray-100
      focus:ring-4 focus:ring-gray-500/20
      active:bg-gray-400 dark:active:bg-gray-500
    `,
    success: `
      bg-green-600 dark:bg-green-700
      hover:bg-green-700 dark:hover:bg-green-600
      text-white
      focus:ring-4 focus:ring-green-500/30
      active:bg-green-800 dark:active:bg-green-500
    `,
    danger: `
      bg-red-600 dark:bg-red-700
      hover:bg-red-700 dark:hover:bg-red-600
      text-white
      focus:ring-4 focus:ring-red-500/30
      active:bg-red-800 dark:active:bg-red-500
    `,
    warning: `
      bg-yellow-500 dark:bg-yellow-600
      hover:bg-yellow-600 dark:hover:bg-yellow-500
      text-white
      focus:ring-4 focus:ring-yellow-500/30
      active:bg-yellow-700 dark:active:bg-yellow-400
    `,
    ghost: `
      bg-transparent
      hover:bg-gray-100 dark:hover:bg-gray-800
      text-gray-800 dark:text-gray-200
      focus:ring-4 focus:ring-gray-500/10
      active:bg-gray-200 dark:active:bg-gray-700
    `,
    link: `
      bg-transparent
      hover:underline
      text-blue-600 dark:text-blue-400
      focus:ring-2 focus:ring-blue-500/20
      active:text-blue-800 dark:active:text-blue-200
    `
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  const disabledStyles = disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer';
  const widthStyles = fullWidth ? 'w-full' : '';
  const loadingStyles = loading ? 'relative !text-transparent' : '';

  return (
    <button
      type={type}
      className={`
        ${baseStyles}
        ${variants[variant]}
        ${sizes[size]}
        ${disabledStyles}
        ${widthStyles}
        ${loadingStyles}
        ${className}
      `}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <svg 
            className="animate-spin h-5 w-5 text-current" 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24"
          >
            <circle 
              className="opacity-25" 
              cx="12" 
              cy="12" 
              r="10" 
              stroke="currentColor" 
              strokeWidth="4"
            />
            <path 
              className="opacity-75" 
              fill="currentColor" 
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        </div>
      )}
      {icon && <span className={`mr-2 ${loading ? 'invisible' : ''}`}>{icon}</span>}
      {children}
    </button>
  );
};

Button.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
  variant: PropTypes.oneOf(['primary', 'secondary', 'success', 'danger', 'warning', 'ghost']),
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
  disabled: PropTypes.bool,
  loading: PropTypes.bool,
  icon: PropTypes.node,
  onClick: PropTypes.func,
  type: PropTypes.oneOf(['button', 'submit', 'reset']),
  fullWidth: PropTypes.bool
};

export default Button; 