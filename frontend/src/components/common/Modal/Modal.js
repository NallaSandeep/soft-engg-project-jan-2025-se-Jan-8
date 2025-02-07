import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { createPortal } from 'react-dom';
import { useModal } from './ModalContext';
import { Button } from '../Button';

const Modal = ({
  id,
  title,
  children,
  onClose,
  size = 'md',
  hideCloseButton = false,
  closeOnClickOutside = true,
  closeOnEsc = true,
  showFooter = true,
  footerContent,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  loading = false,
  className = '',
  ...props
}) => {
  const modalRef = useRef(null);
  const { closeModal } = useModal();

  useEffect(() => {
    const handleEsc = (event) => {
      if (closeOnEsc && event.key === 'Escape') {
        onClose?.();
        closeModal(id);
      }
    };

    document.addEventListener('keydown', handleEsc);
    return () => {
      document.removeEventListener('keydown', handleEsc);
    };
  }, [closeOnEsc, onClose, closeModal, id]);

  const handleBackdropClick = (event) => {
    if (closeOnClickOutside && event.target === event.currentTarget) {
      onClose?.();
      closeModal(id);
    }
  };

  const handleConfirm = async () => {
    if (onConfirm) {
      await onConfirm();
    }
    closeModal(id);
  };

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4'
  };

  const modalContent = (
    <div
      className="fixed inset-0 z-50 overflow-y-auto"
      aria-labelledby={`modal-${id}`}
      role="dialog"
      aria-modal="true"
      onClick={handleBackdropClick}
    >
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div className="fixed inset-0 bg-black/50 transition-opacity" />

        {/* Modal Panel */}
        <div
          ref={modalRef}
          className={`
            relative transform overflow-hidden rounded-lg bg-light-primary dark:bg-dark-primary shadow-xl 
            transition-all w-full ${sizes[size]} ${className}
          `}
          {...props}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-light-accent dark:border-dark-accent">
            <h3
              className="text-lg font-semibold text-light-text-primary dark:text-dark-text-primary"
              id={`modal-${id}`}
            >
              {title}
            </h3>
            {!hideCloseButton && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  onClose?.();
                  closeModal(id);
                }}
                aria-label="Close modal"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </Button>
            )}
          </div>

          {/* Body */}
          <div className="p-4">{children}</div>

          {/* Footer */}
          {showFooter && (
            <div className="flex justify-end gap-2 p-4 border-t border-light-accent dark:border-dark-accent">
              {footerContent || (
                <>
                  <Button
                    variant="secondary"
                    onClick={() => {
                      onClose?.();
                      closeModal(id);
                    }}
                  >
                    {cancelText}
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleConfirm}
                    loading={loading}
                  >
                    {confirmText}
                  </Button>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};

Modal.propTypes = {
  id: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  onClose: PropTypes.func,
  size: PropTypes.oneOf(['sm', 'md', 'lg', 'xl', 'full']),
  hideCloseButton: PropTypes.bool,
  closeOnClickOutside: PropTypes.bool,
  closeOnEsc: PropTypes.bool,
  showFooter: PropTypes.bool,
  footerContent: PropTypes.node,
  confirmText: PropTypes.string,
  cancelText: PropTypes.string,
  onConfirm: PropTypes.func,
  loading: PropTypes.bool,
  className: PropTypes.string
};

export default Modal; 