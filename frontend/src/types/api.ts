// API Response Types
export interface IMEIResponse {
  id?: string
  imei: string
  trouve: boolean
  statut?: string
  numero_slot?: number
  message: string
  recherche_enregistree: boolean
  id_recherche: string
  contexte_acces: {
    niveau_acces: string
    motif_acces: string
    portee_donnees?: string
  }
  appareil?: {
    id?: string
    marque: string
    modele: string
    emmc?: string
    numero_serie?: string
    utilisateur_id?: string
    created_date?: string
    last_updated?: string
  }
}

// Type pour la nouvelle endpoint /imei/{imei}/details
export interface IMEIDetailsResponse {
  imei: string
  recherche_locale: {
    id?: string
    imei: string
    trouve: boolean
    statut?: string
    numero_slot?: number
    message: string
    recherche_enregistree: boolean
    id_recherche: string
    contexte_acces?: {
      niveau_acces: string
      motif_acces: string
      portee_donnees?: string
    }
    appareil?: {
      id?: string
      marque: string
      modele: string
      emmc?: string
      utilisateur_id?: string
      created_date?: string
      last_updated?: string
    }
  }
  validation_tac: {
    tac: string
    marque?: string
    modele?: string
    source: string
    statut?: string
    valide: boolean
    luhn_valide: boolean
    recherche_enregistree: boolean
    id_recherche: string
    timestamp: string
    user_level: string
  }
  details_tac: {
    tac: string
    trouve: boolean
    message?: string
    marque?: string
    modele?: string
    type_appareil?: string
    statut?: string
    annee_sortie?: string
    date_creation?: string
    date_modification?: string
  }
  resume: {
    trouve_localement: boolean
    tac_valide: boolean
    luhn_valide: boolean
    statut_global: string
  }
  timestamp: string
}

export interface PublicStatsResponse {
  total_appareils: number
  total_recherches: number
  recherches_30_jours: number
  total_tacs_disponibles: number
  repartition_statuts: Record<string, number>
  derniere_mise_a_jour: string
  periode_stats?: string
  type_donnees?: string
  message?: string
}

export interface TACResponse {
  tac: string
  trouve: boolean
  message?: string
  marque?: string
  modele?: string
  type_appareil?: string
  categorie?: string
  fabricant?: string
  statut?: string
  [key: string]: any
}

export interface ErrorResponse {
  detail: string
  status_code: number
  retry_after?: string
  limit?: string
}

export interface RateLimitInfo {
  message: string
  retryAfter: string
  limit: string
}

export interface HealthResponse {
  statut: string
  horodatage: string
  service: string
  version: string
  duree_fonctionnement: string
  status: string
  timestamp: string
  base_donnees: {
    statut: string
    message: string
    latence: string
  }
  infos_systeme: {
    duree_fonctionnement: string
    plateforme: string
    version_python: string
    heure_serveur: string
  }
}

// histoty rescherche 
// history recherche SearchHistoryItem
export interface SearchHistoryItem {
  id: string;
  date_recherche: string; // This is a date string, e.g., "2025-08-15 12:40:24"
  imei_recherche: string;
  utilisateur_id: string;
}

// API Request Types
export interface SearchIMEIRequest {
  imei: string
  authToken?: string
}

export interface SearchTACRequest {
  tac: string
}

// Generic API Response
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  rateLimitInfo?: RateLimitInfo
}
