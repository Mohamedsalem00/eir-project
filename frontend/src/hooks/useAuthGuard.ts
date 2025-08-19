import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { authService } from '../api/auth'

/**
 * useAuthGuard - Protects a page based on allowed user types.
 * @param allowedTypes Array of allowed type_utilisateur values (e.g. ['administrateur', 'operateur'])
 * @param redirectTo Path to redirect unauthorized users (default: '/')
 */
export function useAuthGuard(allowedTypes: string[], redirectTo: string = '/') {
  const router = useRouter()

  useEffect(() => {
    const user = authService.getUserData()
    if (!user || !allowedTypes.includes(user.type_utilisateur)) {
      router.push(redirectTo)
    }
  }, [router, allowedTypes, redirectTo])
}
