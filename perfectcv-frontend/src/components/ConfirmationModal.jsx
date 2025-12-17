import React, { useEffect } from 'react';
import { FaExclamationCircle, FaTimes } from 'react-icons/fa';

const ConfirmationModal = ({ isOpen, onClose, onConfirm, title, message, confirmText = "Continue", cancelText = "Cancel" }) => {
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fadeIn"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full animate-slideUp">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-sage-100 dark:bg-sage-900/30 rounded-lg">
              <FaExclamationCircle className="text-sage-600 dark:text-sage-400 text-xl" />
            </div>
            <h3 id="modal-title" className="text-xl font-bold text-gray-900 dark:text-gray-100">
              {title}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            aria-label="Close modal"
          >
            <FaTimes className="text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6">
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
            {message}
          </p>
        </div>

        {/* Footer */}
        <div className="flex justify-center p-6 pt-0">
          <button
            onClick={onConfirm}
            className="w-full px-6 py-3 bg-gradient-to-r from-sage-600 to-sage-800 dark:from-sage-700 dark:to-sage-900 
              hover:from-sage-700 hover:to-sage-900 dark:hover:from-sage-800 dark:hover:to-slate-700 
              text-white rounded-lg font-bold transition-all shadow-sm hover:shadow-md text-base"
            autoFocus
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
