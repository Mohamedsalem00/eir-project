'use client'
import { SearchHistory } from '../../src/components/SearchHistory'
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import AccessDenied from '@/components/AccessDenied'



export default function SearchHistoryPage() {
  const { user } = useAuth()
  const router = useRouter()
  const allowedTypes = [process.env.NEXT_PUBLIC_REGULAR_USER_TYPE && 'utilisateur_authentifie']
  const userType = user?.type_utilisateur

  useEffect(() => {
    if (!user) {
      router.push('/login')
    }
  }, [user, router])

  if (!user) {
    return null
  }

  if (!allowedTypes.includes(userType)) {
    return <AccessDenied />
  }

  return <SearchHistory />
}