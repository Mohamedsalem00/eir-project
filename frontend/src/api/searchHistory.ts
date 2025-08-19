// api/SearchHistoryService.ts

import { apiClient } from '../lib/api-client'
import { handleApiError } from '../lib/api-error'
import { ApiResponse, SearchHistoryItem } from '../types/api'

interface SearchHistoryResponse {
  searches: SearchHistoryItem[];
  // Assuming the backend might provide total count for pagination
  total_count?: number; 
}

// Interface for filtering options
interface GetHistoryOptions {
  language?: 'fr' | 'en' | 'ar';
  skip?: number;
  limit?: number;
  searchTerm?: string;
}

export class SearchHistoryService {
  /**
   * Fetches search history with optional filtering, pagination, and search term.
   * @param authToken - The user's authentication token.
   * @param options - An object containing language, skip, limit, and searchTerm.
   */
  static async getSearchHistory(
    authToken: string, 
    options: GetHistoryOptions = {}
  ): Promise<ApiResponse<SearchHistoryResponse> & { status?: number }> {
    // Set default values for options
    const { language = 'fr', skip = 0, limit = 10, searchTerm = '' } = options;

    try {
      if (!authToken) {
        return { success: false, error: 'Authentication token is required.', status: 401 };
      }

      // Dynamically build query parameters
      const params = new URLSearchParams();
      params.append('skip', String(skip));
      params.append('limit', String(limit));
      if (searchTerm) {
        params.append('q', searchTerm); // Assuming backend uses 'q' for search
      }

      const config = {
        headers: {
          'Accept-Language': language,
          'Authorization': `Bearer ${authToken}`,
        },
        params, // Axios will append these to the URL
      };

      const response = await apiClient.get<SearchHistoryResponse>('/recherches', config);

      return { success: true, data: response.data, status: response.status };
    } catch (error: any) {
      console.error('❌ Error fetching search history:', error);
      const apiError = handleApiError(error);
      return { success: false, error: apiError.message, status: apiError.status };
    }
  }
}

export default SearchHistoryService;