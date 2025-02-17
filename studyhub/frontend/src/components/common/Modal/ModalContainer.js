import React from 'react';
import { useModal } from './ModalContext';
import Modal from './Modal';

const ModalContainer = () => {
  const { modals } = useModal();

  return (
    <>
      {modals.map((modalProps) => (
        <Modal key={modalProps.id} {...modalProps} />
      ))}
    </>
  );
};

export default ModalContainer; 