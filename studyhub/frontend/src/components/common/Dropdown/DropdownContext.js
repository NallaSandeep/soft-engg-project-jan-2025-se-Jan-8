import React, { createContext, useContext, useCallback, useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const DropdownContext = createContext(null);

export const DropdownProvider = ({ children }) => {
  const [openDropdowns, setOpenDropdowns] = useState(new Set());

  const registerDropdown = useCallback((id) => {
    setOpenDropdowns(prev => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
  }, []);

  const unregisterDropdown = useCallback((id) => {
    setOpenDropdowns(prev => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  }, []);

  const isDropdownOpen = useCallback((id) => {
    return openDropdowns.has(id);
  }, [openDropdowns]);

  // Close all dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      const isOutside = !event.target.closest('[data-dropdown]');
      if (isOutside && openDropdowns.size > 0) {
        setOpenDropdowns(new Set());
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [openDropdowns]);

  // Close dropdowns on escape key
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape' && openDropdowns.size > 0) {
        setOpenDropdowns(new Set());
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [openDropdowns]);

  return (
    <DropdownContext.Provider
      value={{
        registerDropdown,
        unregisterDropdown,
        isDropdownOpen
      }}
    >
      {children}
    </DropdownContext.Provider>
  );
};

DropdownProvider.propTypes = {
  children: PropTypes.node.isRequired
};

export const useDropdown = () => {
  const context = useContext(DropdownContext);
  if (!context) {
    throw new Error('useDropdown must be used within a DropdownProvider');
  }
  return context;
};

// Hook for managing dropdown state
export const useDropdownState = (id) => {
  const { registerDropdown, unregisterDropdown, isDropdownOpen } = useDropdown();
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (isOpen) {
      registerDropdown(id);
    } else {
      unregisterDropdown(id);
    }
  }, [id, isOpen, registerDropdown, unregisterDropdown]);

  useEffect(() => {
    // Update local state when global state changes
    setIsOpen(isDropdownOpen(id));
  }, [id, isDropdownOpen]);

  return [isOpen, setIsOpen];
}; 