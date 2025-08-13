// Données de test pour l'interface IMEI
export const TEST_IMEI_DATA = {
  // IMEI valides pour test (exemples)
  valid: [
    '123456789012345',
    '987654321098765',
    '111222333444555',
    '555444333222111'
  ],
  
  // IMEI invalides pour test de validation
  invalid: [
    '12345',           // Trop court
    '1234567890123456', // Trop long
    'abcd1234567890',   // Contient des lettres
    '',                 // Vide
    '123-456-789-012-345' // Avec tirets
  ],
  
  // Messages d'erreur attendus
  errorMessages: {
    tooShort: 'IMEI trop court',
    tooLong: 'IMEI trop long',
    invalidFormat: 'Format IMEI invalide',
    empty: 'Veuillez saisir un numéro IMEI'
  },

  // Exemples de réponses API simulées
  mockResponses: {
    found: {
      id: 'test-id-123',
      imei: '123456789012345',
      trouve: true,
      statut: 'actif',
      numero_slot: 1,
      message: 'IMEI trouvé avec succès',
      recherche_enregistree: true,
      id_recherche: 'search-id-456',
      contexte_acces: {
        niveau_acces: 'visiteur',
        motif_acces: 'Recherche publique',
        portee_donnees: 'Informations de base'
      },
      appareil: {
        id: 'device-id-789',
        marque: 'Samsung',
        modele: 'Galaxy S23',
        emmc: '256GB'
      }
    },
    
    notFound: {
      imei: '987654321098765',
      trouve: false,
      message: 'IMEI non trouvé dans la base de données',
      recherche_enregistree: true,
      id_recherche: 'search-id-789',
      contexte_acces: {
        niveau_acces: 'visiteur',
        motif_acces: 'Recherche publique'
      }
    }
  }
}

// Fonction utilitaire pour formater l'IMEI avec des espaces
export function formatIMEIDisplay(imei: string): string {
  // Format: 123456 789012 345
  const clean = imei.replace(/\D/g, '')
  if (clean.length <= 6) return clean
  if (clean.length <= 12) return `${clean.slice(0, 6)} ${clean.slice(6)}`
  return `${clean.slice(0, 6)} ${clean.slice(6, 12)} ${clean.slice(12)}`
}

// Fonction utilitaire pour générer un IMEI de test aléatoire
export function generateRandomIMEI(): string {
  const digits = '0123456789'
  let imei = ''
  for (let i = 0; i < 15; i++) {
    imei += digits[Math.floor(Math.random() * digits.length)]
  }
  return imei
}

// Validation Luhn simplifiée pour IMEI (pour test)
export function validateLuhnChecksum(imei: string): boolean {
  const digits = imei.replace(/\D/g, '')
  if (digits.length !== 15) return false
  
  let sum = 0
  let isEven = false
  
  // Traiter du dernier chiffre au premier (en excluant le dernier)
  for (let i = digits.length - 2; i >= 0; i--) {
    let digit = parseInt(digits[i])
    
    if (isEven) {
      digit *= 2
      if (digit > 9) {
        digit = digit % 10 + Math.floor(digit / 10)
      }
    }
    
    sum += digit
    isEven = !isEven
  }
  
  const checkDigit = (10 - (sum % 10)) % 10
  return checkDigit === parseInt(digits[digits.length - 1])
}

// Helper pour tester la connectivité API
export async function testApiConnectivity(): Promise<{
  connected: boolean
  latency?: number
  error?: string
}> {
  const startTime = Date.now()
  
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000)
    
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/health`, {
      method: 'GET',
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    const latency = Date.now() - startTime
    
    if (response.ok) {
      return { connected: true, latency }
    } else {
      return { connected: false, error: `HTTP ${response.status}` }
    }
  } catch (error) {
    return { 
      connected: false, 
      error: error instanceof Error ? error.message : 'Erreur inconnue' 
    }
  }
}

export default TEST_IMEI_DATA
