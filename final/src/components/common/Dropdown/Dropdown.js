import React, { useRef, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { useDropdownState } from './DropdownContext';

const Dropdown = ({
  id,
  trigger,
  children,
  placement = 'bottom-start',
  offset = 4,
  className = '',
  onOpen,
  onClose,
  ...props
}) => {
  const dropdownRef = useRef(null);
  const triggerRef = useRef(null);
  const [isOpen, setIsOpen] = useDropdownState(id);

  const updatePosition = useCallback(() => {
    if (!isOpen || !dropdownRef.current || !triggerRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const dropdownRect = dropdownRef.current.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;

    let top = 0;
    let left = 0;

    // Calculate position based on placement
    switch (placement) {
      case 'bottom-start':
        top = triggerRect.bottom + offset;
        left = triggerRect.left;
        break;
      case 'bottom-end':
        top = triggerRect.bottom + offset;
        left = triggerRect.right - dropdownRect.width;
        break;
      case 'top-start':
        top = triggerRect.top - dropdownRect.height - offset;
        left = triggerRect.left;
        break;
      case 'top-end':
        top = triggerRect.top - dropdownRect.height - offset;
        left = triggerRect.right - dropdownRect.width;
        break;
      default:
        top = triggerRect.bottom + offset;
        left = triggerRect.left;
    }

    // Adjust for viewport boundaries
    if (top + dropdownRect.height > viewportHeight) {
      top = triggerRect.top - dropdownRect.height - offset;
    }
    if (left + dropdownRect.width > viewportWidth) {
      left = viewportWidth - dropdownRect.width - offset;
    }
    if (top < 0) {
      top = triggerRect.bottom + offset;
    }
    if (left < 0) {
      left = offset;
    }

    dropdownRef.current.style.top = `${top}px`;
    dropdownRef.current.style.left = `${left}px`;
  }, [isOpen, offset, placement]);

  // Update position on scroll or resize
  useEffect(() => {
    if (!isOpen) return;

    const handleUpdate = () => {
      requestAnimationFrame(updatePosition);
    };

    window.addEventListener('scroll', handleUpdate, true);
    window.addEventListener('resize', handleUpdate);

    return () => {
      window.removeEventListener('scroll', handleUpdate, true);
      window.removeEventListener('resize', handleUpdate);
    };
  }, [isOpen, updatePosition]);

  // Update position when content changes
  useEffect(() => {
    if (isOpen) {
      updatePosition();
    }
  }, [isOpen, children, updatePosition]);

  // Handle keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      const focusableElements = dropdownRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      if (!focusableElements?.length) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];
      const activeElement = document.activeElement;

      switch (e.key) {
        case 'Tab':
          if (e.shiftKey && activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          } else if (!e.shiftKey && activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
          break;
        case 'ArrowDown':
          e.preventDefault();
          if (!activeElement || activeElement === lastElement) {
            firstElement.focus();
          } else {
            const currentIndex = Array.from(focusableElements).indexOf(activeElement);
            focusableElements[currentIndex + 1]?.focus();
          }
          break;
        case 'ArrowUp':
          e.preventDefault();
          if (!activeElement || activeElement === firstElement) {
            lastElement.focus();
          } else {
            const currentIndex = Array.from(focusableElements).indexOf(activeElement);
            focusableElements[currentIndex - 1]?.focus();
          }
          break;
        default:
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  const handleToggle = () => {
    const newIsOpen = !isOpen;
    setIsOpen(newIsOpen);
    if (newIsOpen) {
      onOpen?.();
    } else {
      onClose?.();
    }
  };

  return (
    <>
      <div ref={triggerRef} data-dropdown={id}>
        {React.cloneElement(trigger, {
          onClick: handleToggle,
          'aria-expanded': isOpen,
          'aria-haspopup': true
        })}
      </div>
      {isOpen && (
        <div
          ref={dropdownRef}
          className={`
            absolute z-50 min-w-[8rem] py-1 bg-light-primary dark:bg-dark-primary
            rounded-lg shadow-lg border border-light-accent dark:border-dark-accent
            ${className}
          `}
          role="menu"
          aria-orientation="vertical"
          data-dropdown={id}
          {...props}
        >
          {children}
        </div>
      )}
    </>
  );
};

Dropdown.propTypes = {
  id: PropTypes.string.isRequired,
  trigger: PropTypes.element.isRequired,
  children: PropTypes.node.isRequired,
  placement: PropTypes.oneOf(['bottom-start', 'bottom-end', 'top-start', 'top-end']),
  offset: PropTypes.number,
  className: PropTypes.string,
  onOpen: PropTypes.func,
  onClose: PropTypes.func
};

export default Dropdown;

// Dropdown Item component
export const DropdownItem = ({
  children,
  className = '',
  disabled = false,
  onClick,
  ...props
}) => {
  return (
    <button
      className={`
        w-full px-4 py-2 text-left text-sm
        text-light-text-primary dark:text-dark-text-primary
        hover:bg-light-accent dark:hover:bg-dark-accent
        disabled:opacity-50 disabled:cursor-not-allowed
        focus:outline-none focus:bg-light-accent dark:focus:bg-dark-accent
        ${className}
      `}
      role="menuitem"
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
};

DropdownItem.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  onClick: PropTypes.func
}; 