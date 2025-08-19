import { UserProfile } from '@/api/auth'

// Permission utility functions
export const PermissionService = {
  canViewDashboard(user?: UserProfile): boolean {
    if (!user) return false
    return user.type_utilisateur === 'administrateur' || user.type_utilisateur === 'operateur'
  },

  canViewAdminPanel(user?: UserProfile): boolean {
    if (!user) return false
    return user.type_utilisateur === 'administrateur'
  },

  canViewOrganisation(user?: UserProfile): boolean {
    if (!user) return false
    return user.type_utilisateur === 'operateur' && !!user.organisation
  },

  canViewMyDevices(user?: UserProfile): boolean {
    if (!user) return false
    return user.type_utilisateur === 'utilisateur_authentifie' && user.niveau_acces === 'standard'
  },

  canViewSearchHistory(user?: UserProfile): boolean {
    if (!user) return false
    return user.type_utilisateur === 'utilisateur_authentifie' && user.niveau_acces === 'standard'
  },

  canEditDevice(user?: UserProfile): boolean {
    if (!user) return false
    // Example: Only admin and operator can edit devices
    return user.type_utilisateur === 'administrateur' || user.type_utilisateur === 'operateur'
  },

  // Add more permission checks as needed
}
