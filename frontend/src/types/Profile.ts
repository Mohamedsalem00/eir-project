export interface ProfileData {
  id: string
  nom: string
  email: string
  type_utilisateur: string
  date_creation?: string
  derniere_connexion?: string
  statut_compte: string
  permissions: string[]
  statistiques: {
    nombre_connexions: number
    activites_7_derniers_jours: number
    compte_cree_depuis_jours: number
    derniere_activite?: string
  }
}