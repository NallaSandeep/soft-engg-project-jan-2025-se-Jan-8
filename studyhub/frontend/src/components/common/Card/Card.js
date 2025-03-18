import React from 'react';
import PropTypes from 'prop-types';

const Card = ({
  children,
  className = '',
  variant = 'default',
  hover = false,
  onClick,
  ...props
}) => {
  const baseStyles = 'rounded-lg';
  
  const variants = {
    default: 'bg-zinc-100 dark:bg-zinc-800 shadow-sm dark:shadow-zinc-900/50',
    elevated: 'bg-zinc-100 dark:bg-zinc-800 shadow-md dark:shadow-zinc-900/50',
    flat: 'bg-gray-50 dark:bg-zinc-800/50'
  };

  const hoverStyles = hover ? 'hover:shadow-md hover:scale-[1.01]' : '';
  
  return (
    <div
      className={`${baseStyles} ${variants[variant]} ${hoverStyles} ${className}`}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  );
};

Card.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
  variant: PropTypes.oneOf(['default', 'elevated', 'flat']),
  hover: PropTypes.bool,
  onClick: PropTypes.func
};

export default Card; 