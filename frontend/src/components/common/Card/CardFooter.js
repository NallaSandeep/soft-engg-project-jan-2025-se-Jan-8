import React from 'react';
import PropTypes from 'prop-types';

const CardFooter = ({ children, className = '', ...props }) => (
  <div 
    className={`p-4 border-t border-light-accent dark:border-dark-accent ${className}`}
    {...props}
  >
    {children}
  </div>
);

CardFooter.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string
};

export default CardFooter; 