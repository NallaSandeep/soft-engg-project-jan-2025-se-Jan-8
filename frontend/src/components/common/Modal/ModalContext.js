import React, { createContext, useContext, useReducer, useCallback } from 'react';
import PropTypes from 'prop-types';

const ModalContext = createContext(null);

// Modal actions
const OPEN_MODAL = 'OPEN_MODAL';
const CLOSE_MODAL = 'CLOSE_MODAL';
const CLOSE_ALL_MODALS = 'CLOSE_ALL_MODALS';

// Modal reducer
const modalReducer = (state, action) => {
  switch (action.type) {
    case OPEN_MODAL:
      return {
        ...state,
        modals: [...state.modals, action.payload]
      };
    case CLOSE_MODAL:
      return {
        ...state,
        modals: state.modals.filter(modal => modal.id !== action.payload)
      };
    case CLOSE_ALL_MODALS:
      return {
        ...state,
        modals: []
      };
    default:
      return state;
  }
};

export const ModalProvider = ({ children }) => {
  const [state, dispatch] = useReducer(modalReducer, { modals: [] });

  const openModal = useCallback((modalProps) => {
    const id = Math.random().toString(36).substr(2, 9);
    dispatch({
      type: OPEN_MODAL,
      payload: { id, ...modalProps }
    });
    return id;
  }, []);

  const closeModal = useCallback((modalId) => {
    dispatch({
      type: CLOSE_MODAL,
      payload: modalId
    });
  }, []);

  const closeAllModals = useCallback(() => {
    dispatch({ type: CLOSE_ALL_MODALS });
  }, []);

  return (
    <ModalContext.Provider
      value={{
        modals: state.modals,
        openModal,
        closeModal,
        closeAllModals
      }}
    >
      {children}
    </ModalContext.Provider>
  );
};

ModalProvider.propTypes = {
  children: PropTypes.node.isRequired
};

export const useModal = () => {
  const context = useContext(ModalContext);
  if (!context) {
    throw new Error('useModal must be used within a ModalProvider');
  }
  return context;
};

// Hook for creating modal instances
export const useCreateModal = (defaultProps = {}) => {
  const { openModal, closeModal } = useModal();

  const open = useCallback((props = {}) => {
    return openModal({ ...defaultProps, ...props });
  }, [defaultProps, openModal]);

  return [open, closeModal];
}; 