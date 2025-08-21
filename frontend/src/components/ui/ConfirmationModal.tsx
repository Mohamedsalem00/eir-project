'use client'

import React from 'react'

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  children: React.ReactNode;
  t: (key: string) => string;
  variant?: 'danger' | 'primary'; // New prop for color scheme
  actionTextKey?: string; // New prop for the confirmation button text key
}

export function ConfirmationModal({ 
  t, 
  isOpen, 
  onClose, 
  onConfirm, 
  title, 
  children,
  variant = 'danger', // Default to 'danger' for destructive actions
  actionTextKey = 'confirm' // Default translation key for the action button
}: ConfirmationModalProps) {
  if (!isOpen) return null;

  // Function to determine button color based on the variant
  const getVariantClasses = () => {
    switch (variant) {
      case 'primary':
        return 'bg-blue-600 hover:bg-blue-700';
      case 'danger':
      default:
        return 'bg-red-600 hover:bg-red-700';
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" aria-modal="true" role="dialog">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-8 max-w-sm w-full text-center m-4">
        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">{title}</h2>
        <p className="text-gray-600 dark:text-gray-300 mb-8">{children}</p>
        <div className="flex gap-4 justify-center">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-100 text-gray-800 rounded-lg font-medium hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            {t('annuler')}
          </button>
          <button
            onClick={onConfirm}
            className={`px-6 py-2 text-white rounded-lg font-medium transition-colors ${getVariantClasses()}`}
          >
            {t(actionTextKey)}
          </button>
        </div>
      </div>
    </div>
  );
}
