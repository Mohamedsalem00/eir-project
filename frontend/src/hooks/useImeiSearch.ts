// src/hooks/useImeiSearch.ts
import { useState, useEffect } from 'react';
import { IMEIResponse, IMEIService } from '../api';
import { useLanguage } from '../contexts/LanguageContext';

export function useImeiSearch() {
  const { t, currentLang } = useLanguage();
  const [imei, setImei] = useState('');
  const [result, setResult] = useState<IMEIResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // You can even include search limit state here if it's only used for this search
  const [searchLimitReached, setSearchLimitReached] = useState(false);

  useEffect(() => {
    // Logic to check limit on mount
    setSearchLimitReached(IMEIService.isSearchLimitReached());
  }, []);

  const search = async () => {
    // All the logic from your searchIMEI function goes here...
    const validation = IMEIService.validateIMEI(imei);
    if (!validation.isValid) {
      setError(validation.error || 'Invalid IMEI');
      return;
    }
    
    if (IMEIService.isSearchLimitReached()) {
        setError(t('search_limit_reached'));
        setSearchLimitReached(true);
        return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    const response = await IMEIService.getIMEIDetails(validation.cleanImei!, undefined, currentLang);
    
    if (response.success && response.data) {
      setResult(response.data);
    } else {
      setError(response.error || 'Unknown error');
    }
    
    setIsLoading(false);
    setSearchLimitReached(IMEIService.isSearchLimitReached()); // Update limit status
  };

  const reset = () => {
    setImei('');
    setResult(null);
    setError(null);
    setIsLoading(false);
  };

  return {
    imei,
    setImei,
    result,
    isLoading,
    error,
    searchLimitReached,
    search,
    reset,
  };
}