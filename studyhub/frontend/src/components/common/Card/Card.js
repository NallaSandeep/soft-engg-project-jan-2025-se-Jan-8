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
  const baseStyles = 'rounded-lg transition-all duration-300';
  
  const variants = {
    default: 'bg-white shadow-sm',
    elevated: 'bg-white shadow-md',
    flat: 'bg-gray-50'
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