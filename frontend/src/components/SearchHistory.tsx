// components/SearchHistory.tsx

'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useTranslation } from '@/hooks/useTranslation'
import { SearchHistoryService } from '@/api'
import { SearchHistoryItem } from '@/types/api'
import { authService } from '@/api/auth'
import Unauthorized401 from '../../src/components/Unauthorized401'

// --- Helper Components (unchanged) ---
const SearchIcon = () => ( <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>);
const EmptyState = ({ message }: { message: string }) => ( <div className="text-center py-16 px-6"><div className="mx-auto w-16 h-16 text-gray-400"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 10.5h.01" /></svg></div><h3 className="mt-2 text-lg font-medium text-gray-900">No Results Found</h3><p className="mt-1 text-sm text-gray-500">{message}</p></div>);
const SkeletonLoader = () => ( <div className="space-y-2 animate-pulse">{[...Array(5)].map((_, i) => (<div key={i} className="flex items-center justify-between p-4"><div className="h-4 bg-gray-200 rounded w-2/5"></div><div className="h-4 bg-gray-200 rounded w-1/3"></div></div>))}</div>);


export function SearchHistory() {
  const { user } = useAuth();
  const authToken = user ? authService.getAuthToken() : undefined;
  const { t, currentLang } = useTranslation();

  const [history, setHistory] = useState<SearchHistoryItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUnauthorized, setIsUnauthorized] = useState(false);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // 1. Debounce the search term (unchanged)
  useEffect(() => {
    const timerId = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
      setCurrentPage(1); // Reset to first page on new search
    }, 500);
    return () => clearTimeout(timerId);
  }, [searchTerm]);

  // 2. Refactored data fetching into a single, direct useEffect hook
  useEffect(() => {
    // Don't fetch if there's no auth token
    if (!authToken) {
        setIsLoading(false);
        return;
    }

    const fetchHistory = async () => {
      setIsLoading(true);
      setError(null);

      const skip = (currentPage - 1) * itemsPerPage;
      const response = await SearchHistoryService.getSearchHistory(authToken, {
        language: currentLang,
        skip,
        limit: itemsPerPage,
        searchTerm: debouncedSearchTerm,
      });

      if (response.success && response.data) {
        setHistory(response.data.searches);
        setTotalCount(response.data.total_count || 0); // Use total_count from backend
      } else {
        if (response.status === 401) {
          setIsUnauthorized(true);
        } else {
          setError(response.error || t('erreur_inconnue'));
        }
      }
      setIsLoading(false);
    };

    fetchHistory();
    // This effect runs ONLY when the final search term, page number, or auth token changes.
  }, [debouncedSearchTerm, currentPage, authToken, currentLang, t]);

  const lastPage = Math.ceil(totalCount / itemsPerPage);
  const isLastPage = currentPage >= lastPage;

  if (isUnauthorized) {
    return <Unauthorized401 supportEmail="support@eir.com" />;
  }

  return (
    <div className="mt-12 bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Header with Search Bar (unchanged) */}
      <div className="flex flex-col md:flex-row items-center justify-between p-6 border-b border-gray-200 gap-4">
        <h2 className="text-xl font-bold text-gray-900">{t('historique_recherches')}</h2>
        <div className="relative w-full md:w-72">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"><SearchIcon /></div>
          <input type="text" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder={t('rechercher_par_imei')} className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"/>
        </div>
      </div>

      {/* Content Area (unchanged) */}
      <div className="overflow-x-auto">
        {isLoading ? <SkeletonLoader /> : error ? (<div className="text-center py-16 text-red-600"><p>{error}</p></div>) : history.length === 0 ? (<EmptyState message={t('aucune_recherche_historique')} />) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('imei_recherche')}</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t('date')}</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {history.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-800">{item.imei_recherche}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(item.date_recherche).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Footer with Pagination (now uses total_count) */}
      {totalCount > 0 && !isLoading && (
        <div className="p-4 border-t border-gray-200 flex items-center justify-between">
            <span className="text-sm text-gray-600">
                {t('page')} <span className="font-semibold">{currentPage}</span> of <span className="font-semibold">{lastPage}</span>
            </span>
          <div className="flex gap-2">
            <button onClick={() => setCurrentPage((p) => p - 1)} disabled={currentPage === 1} className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">{t('precedent')}</button>
            <button onClick={() => setCurrentPage((p) => p + 1)} disabled={isLastPage} className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">{t('suivant')}</button>
          </div>
        </div>
      )}
    </div>
  );
}