import React from 'react';
import PropTypes from 'prop-types';

const CardHeader = ({ children, className = '', ...props }) => (
  <div 
    className={`p-4 border-b border-light-accent dark:border-dark-accent ${className}`}
    {...props}
  >
    {children}
  </div>
);

CardHeader.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string
};

export default CardHeader; 