// Types pour les clés de traduction
export type TranslationKey = 
  | 'verification_imei'
  | 'invite_imei'
  | 'libelle_imei'
  | 'format_imei'
  | 'longueur_imei'
  | 'verifier_imei'
  | 'nouvelle_recherche'
  | 'titre_resultats'
  | 'details_imei'
  | 'analyse_complete'
  | 'invalide_luhn'
  | 'resume'
  | 'base_locale'
  | 'trouve'
  | 'tac_valide'
  | 'luhn_valide'
  | 'recherche_locale'
  | 'statut'
  | 'etat'
  | 'marque'
  | 'modele'
  | 'validation_tac'
  | 'tac'
  | 'libelle_tac_valide'
  | 'libelle_luhn_valide'
  | 'source'
  | 'details_tac'
  | 'tac_non_trouve'
  | 'analyse_complete_effectuee'
  | 'description_analyse_complete'
  | 'horodatage'

export type TranslationParams = Record<string, string | number>

// Type pour la fonction de traduction
export type TranslateFunction = (key: TranslationKey, params?: TranslationParams) => string
