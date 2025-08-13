'use client'

import { useState, useEffect } from 'react'
import { IMEIService } from '../api/imei'

export function SearchLimitDebug() {
  const [debugInfo, setDebugInfo] = useState({
    count: 0,
    limit: 0,
    remaining: 0,
    timeRemaining: '',
    isLimitReached: false
  })

  const updateDebugInfo = () => {
    setDebugInfo({
      count: IMEIService.getSearchCount(),
      limit: IMEIService.getSearchLimit(),
      remaining: IMEIService.getRemainingSearches(),
      timeRemaining: IMEIService.getSessionTimeRemaining(),
      isLimitReached: IMEIService.isSearchLimitReached()
    })
  }

  useEffect(() => {
    updateDebugInfo()
    
    // Update every 30 seconds
    const interval = setInterval(updateDebugInfo, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const clearSession = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('eir_search_count')
      localStorage.removeItem('eir_search_date')
      updateDebugInfo()
    }
  }

  const simulateSearch = () => {
    // Simulate a search by incrementing the counter manually
    if (typeof window !== 'undefined') {
      const current = IMEIService.getSearchCount()
      localStorage.setItem('eir_search_count', (current + 1).toString())
      updateDebugInfo()
    }
  }

  return (
    <div className="fixed bottom-4 right-4 bg-white border rounded-lg shadow-lg p-4 text-xs max-w-sm">
      <h4 className="font-semibold text-gray-700 mb-2">🔍 Search Limit Debug</h4>
      <div className="space-y-1 text-gray-600">
        <div>Count: {debugInfo.count}/{debugInfo.limit}</div>
        <div>Remaining: {debugInfo.remaining}</div>
        <div>Reset in: {debugInfo.timeRemaining}</div>
        <div className={`font-medium ${debugInfo.isLimitReached ? 'text-red-600' : 'text-green-600'}`}>
          Status: {debugInfo.isLimitReached ? 'LIMIT REACHED' : 'ACTIVE'}
        </div>
      </div>
      <div className="flex gap-2 mt-3">
        <button 
          onClick={simulateSearch}
          className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs hover:bg-blue-200"
          disabled={debugInfo.isLimitReached}
        >
          +1 Search
        </button>
        <button 
          onClick={clearSession}
          className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs hover:bg-red-200"
        >
          Clear Session
        </button>
        <button 
          onClick={updateDebugInfo}
          className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs hover:bg-gray-200"
        >
          Refresh
        </button>
      </div>
    </div>
  )
}
