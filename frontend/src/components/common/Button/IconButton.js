import React from 'react';
import PropTypes from 'prop-types';
import Button from './Button';

const IconButton = ({ 
  icon, 
  className = '', 
  size = 'md',
  ...props 
}) => {
  const sizes = {
    sm: 'p-1.5',
    md: 'p-2',
    lg: 'p-3'
  };

  return (
    <Button
      className={`!p-0 ${sizes[size]} ${className}`}
      {...props}
    >
      {icon}
    </Button>
  );
};

IconButton.propTypes = {
  icon: PropTypes.node.isRequired,
  className: PropTypes.string,
  size: PropTypes.oneOf(['sm', 'md', 'lg'])
};

export default IconButton; 