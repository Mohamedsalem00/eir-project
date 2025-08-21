import React from 'react'

interface FooterProps {
  title: string
  copyright: string
  builtWith: string
}

export const Footer: React.FC<FooterProps> = ({ title, copyright, builtWith }) => (
  <footer className="bg-white/80 dark:bg-gray-900/80 backdrop-blur border-t border-gray-200/50 dark:border-gray-800/50 mt-20">
    <div className="container mx-auto px-6 py-12 text-center">
      <div className="mb-6">
        <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-3xl flex items-center justify-center mx-auto mb-4 shadow-lg">
          <span className="text-white font-bold text-xl">EIR</span>
        </div>
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">{title}</h3>
      </div>
      <div className="text-sm text-gray-500 dark:text-gray-400 space-y-2">
        <p>{copyright}</p>
        <p>{builtWith}</p>
      </div>
    </div>
  </footer>
)
