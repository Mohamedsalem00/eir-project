// src/api/SearchService.ts

export class SearchService {
  private static readonly SESSION_KEY = 'eir_search_count'
  private static readonly SESSION_DATE_KEY = 'eir_search_date'
  private static readonly SESSION_RESET_HOURS = 24
  public static readonly maxSearches = parseInt(process.env.NEXT_PUBLIC_VISITOR_SEARCH_LIMIT || '10')

  private static initializeSearchCount(): number {
    if (typeof window === 'undefined') return 0
    try {
      const storedDate = localStorage.getItem(this.SESSION_DATE_KEY)
      const storedCount = localStorage.getItem(this.SESSION_KEY)
      if (!storedDate || !storedCount) {
        this.resetSearchSession()
        return 0
      }
      const sessionDate = new Date(parseInt(storedDate))
      const now = new Date()
      const hoursDiff = (now.getTime() - sessionDate.getTime()) / (1000 * 60 * 60)
      if (hoursDiff >= this.SESSION_RESET_HOURS) {
        this.resetSearchSession()
        return 0
      }
      return parseInt(storedCount) || 0
    } catch (error) {
      this.resetSearchSession()
      return 0
    }
  }

  private static resetSearchSession(): void {
    if (typeof window === 'undefined') return
    try {
      const now = new Date().getTime().toString()
      localStorage.setItem(this.SESSION_DATE_KEY, now)
      localStorage.setItem(this.SESSION_KEY, '0')
    } catch {}
  }

  static updateSearchCount(count: number): void {
    if (typeof window === 'undefined') return
    try {
      localStorage.setItem(this.SESSION_KEY, count.toString())
    } catch {}
  }

  static getSearchCount(): number {
    return this.initializeSearchCount()
  }

  static getSearchLimit(): number {
    return SearchService.maxSearches
  }

  static resetSearchCount(): void {
    this.resetSearchSession()
  }

  static isSearchLimitReached(): boolean {
    return SearchService.getSearchCount() >= SearchService.maxSearches
  }

  static getRemainingSearches(): number {
    return Math.max(0, SearchService.maxSearches - SearchService.getSearchCount())
  }

  static getSessionTimeRemaining(): string {
    if (typeof window === 'undefined') return '24h'
    try {
      const storedDate = localStorage.getItem(this.SESSION_DATE_KEY)
      if (!storedDate) return '24h'
      const sessionDate = new Date(parseInt(storedDate))
      const now = new Date()
      const hoursRemaining = this.SESSION_RESET_HOURS - ((now.getTime() - sessionDate.getTime()) / (1000 * 60 * 60))
      if (hoursRemaining <= 0) return '0h'
      if (hoursRemaining < 1) {
        const minutesRemaining = Math.ceil(hoursRemaining * 60)
        return `${minutesRemaining}min`
      }
      return `${Math.ceil(hoursRemaining)}h`
    } catch {
      return '24h'
    }
  }
}

export default SearchService
