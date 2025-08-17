# API Integration Documentation

## Overview
This document describes the complete API integration system for the EIR frontend, including authentication, user management, and all backend communication.

## Architecture

### 1. API Client (`src/lib/api-client.ts`)
- **Base Configuration**: Configurable base URL with environment variables
- **Interceptors**: Automatic token injection and error handling
- **Request/Response Logging**: Development mode logging for debugging
- **Timeout Handling**: 10-second timeout for all requests

### 2. Error Handling (`src/lib/api-error.ts`)
- **Standardized Errors**: Consistent error format across the application
- **HTTP Status Mapping**: Specific error messages for different HTTP status codes
- **Rate Limiting**: Special handling for 429 rate limit responses
- **Network Errors**: Connection and timeout error handling

### 3. Authentication Service (`src/api/auth.ts`)
- **Complete Auth Flow**: Login, register, profile management, and logout
- **Password Reset**: Full password reset flow with email/SMS verification
- **Token Management**: Automatic token storage and retrieval
- **User Persistence**: Local storage management for user sessions

## API Endpoints

### Authentication Endpoints

#### POST `/authentification/connexion`
**Login endpoint**
```typescript
interface LoginRequest {
  email: string
  mot_de_passe: string
}

interface LoginResponse {
  access_token: string
  token_type: string
}
```

#### POST `/authentification/inscription`
**User registration endpoint**
```typescript
interface RegisterRequest {
  nom: string
  email: string
  mot_de_passe: string
  type_utilisateur: string
}

interface RegisterResponse {
  id: string
  nom: string
  email: string
  type_utilisateur: string
}
```

#### GET `/authentification/profile`
**Get detailed user profile (requires authentication)**
```typescript
interface UserProfile {
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
```

#### GET `/authentification/profile/simple`
**Get simple user profile (requires authentication)**
```typescript
interface SimpleProfile {
  id: string
  nom: string
  email: string
  type_utilisateur: string
}
```

#### POST `/authentification/deconnexion`
**User logout (requires authentication)**
```typescript
Response: { message: string }
```

#### POST `/authentification/mot-de-passe-oublie`
**Request password reset**
```typescript
interface PasswordResetRequest {
  email: string
  methode_verification: 'EMAIL' | 'SMS'
  telephone?: string
}

interface PasswordResetResponse {
  success: boolean
  message: string
  token?: string
  methode_verification?: string
  expires_in_minutes?: number
}
```

#### POST `/authentification/verifier-code-reset`
**Verify reset code**
```typescript
interface VerifyCodeRequest {
  token: string
  code_verification: string
}
```

#### POST `/authentification/nouveau-mot-de-passe`
**Set new password**
```typescript
interface NewPasswordRequest {
  token: string
  nouveau_mot_de_passe: string
  confirmer_mot_de_passe: string
}
```

## Usage Examples

### 1. Basic Authentication Flow
```typescript
import { authService } from '../api/auth'

// Login
try {
  const loginResponse = await authService.login({
    email: 'user@example.com',
    mot_de_passe: 'password123'
  })
  
  // Token is automatically stored
  console.log('Login successful:', loginResponse.access_token)
} catch (error) {
  console.error('Login failed:', error.message)
}

// Get user profile
try {
  const profile = await authService.getProfile()
  console.log('User profile:', profile)
} catch (error) {
  console.error('Failed to get profile:', error.message)
}
```

### 2. User Registration
```typescript
import { authService } from '../api/auth'

try {
  const userData = {
    nom: 'John Doe',
    email: 'john@example.com',
    mot_de_passe: 'securepassword123',
    type_utilisateur: 'utilisateur_authentifie'
  }
  
  const response = await authService.register(userData)
  console.log('Registration successful:', response)
  
  // User is automatically logged in after registration
} catch (error) {
  console.error('Registration failed:', error.message)
}
```

### 3. Password Reset Flow
```typescript
import { authService } from '../api/auth'

// Step 1: Request reset
const resetRequest = await authService.requestPasswordReset({
  email: 'user@example.com',
  methode_verification: 'EMAIL'
})

// Step 2: Verify code (user enters code from email)
const verification = await authService.verifyResetCode({
  token: resetRequest.token!,
  code_verification: '123456'
})

// Step 3: Set new password
const passwordChange = await authService.setNewPassword({
  token: resetRequest.token!,
  nouveau_mot_de_passe: 'newpassword123',
  confirmer_mot_de_passe: 'newpassword123'
})
```

### 4. Protected API Calls
```typescript
import { apiClient } from '../lib/api-client'

// The API client automatically includes the auth token
try {
  const response = await apiClient.get('/protected-endpoint')
  console.log('Protected data:', response.data)
} catch (error) {
  if (error.status === 401) {
    // Token expired or invalid, redirect to login
    window.location.href = '/login'
  }
}
```

## Error Handling

### Standard Error Format
```typescript
interface ApiError {
  message: string
  status: number
  rateLimitInfo?: RateLimitInfo
}
```

### Common Error Scenarios
```typescript
import { handleApiError } from '../lib/api-error'

try {
  await apiClient.post('/endpoint', data)
} catch (error: any) {
  const apiError = handleApiError(error)
  
  switch (apiError.status) {
    case 401:
      // Unauthorized - redirect to login
      break
    case 403:
      // Forbidden - insufficient permissions
      break
    case 429:
      // Rate limited - show retry information
      console.log('Retry after:', apiError.rateLimitInfo?.retryAfter)
      break
    case 500:
      // Server error - show generic error message
      break
  }
}
```

## Configuration

### Environment Variables
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
```

### API Client Configuration
```typescript
// src/lib/api-client.ts
const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const timeout = 10000 // 10 seconds
```

## Security Features

### 1. Token Management
- **Automatic Storage**: JWT tokens stored in localStorage
- **Automatic Injection**: Tokens automatically included in all authenticated requests
- **Secure Cleanup**: Tokens removed on logout or expiration

### 2. Request Validation
- **Input Sanitization**: All user inputs validated before API calls
- **Type Safety**: TypeScript interfaces ensure data consistency
- **Error Boundaries**: Graceful error handling for network failures

### 3. Rate Limiting
- **Automatic Detection**: Rate limit responses automatically parsed
- **User Feedback**: Clear messages about rate limits and retry times
- **Graceful Degradation**: Application continues to function with appropriate messaging

## Testing

### Mock API Responses
```typescript
// __mocks__/api/auth.ts
export const authService = {
  login: jest.fn().mockResolvedValue({
    access_token: 'mock-token',
    token_type: 'bearer'
  }),
  getProfile: jest.fn().mockResolvedValue({
    id: 'mock-id',
    nom: 'Mock User',
    email: 'mock@example.com',
    type_utilisateur: 'utilisateur_authentifie'
  })
}
```

### API Error Testing
```typescript
import { handleApiError } from '../lib/api-error'

test('handles 401 unauthorized error', () => {
  const mockError = {
    response: { status: 401, data: { detail: 'Unauthorized' } }
  }
  
  const result = handleApiError(mockError as any)
  expect(result.status).toBe(401)
  expect(result.message).toBe('Authentification requise')
})
```

## Troubleshooting

### Common Issues

#### 1. CORS Errors
- Ensure backend allows requests from frontend domain
- Check that credentials are included in requests
- Verify preflight request handling

#### 2. Token Expiration
- Implement automatic token refresh
- Add interceptor to handle 401 responses
- Redirect to login on authentication failure

#### 3. Network Timeouts
- Increase timeout value for slow connections
- Implement retry logic for failed requests
- Add offline detection and handling

### Debug Mode
```typescript
// Enable detailed logging in development
if (process.env.NODE_ENV === 'development') {
  console.log('🚀 API Request:', config.method?.toUpperCase(), config.url)
  console.log('✅ API Response:', response.status, response.config.url)
}
```

## Best Practices

### 1. Error Handling
- Always wrap API calls in try-catch blocks
- Provide meaningful error messages to users
- Implement fallback behavior for critical failures

### 2. Performance
- Use request caching where appropriate
- Implement request debouncing for search inputs
- Optimize bundle size by lazy loading API modules

### 3. Security
- Never store sensitive data in localStorage
- Implement proper token expiration handling
- Use HTTPS in production environments

### 4. User Experience
- Show loading states during API calls
- Provide clear feedback for all user actions
- Implement optimistic updates where appropriate

## Future Enhancements

1. **Real-time Updates**: WebSocket integration for live data
2. **Offline Support**: Service worker for offline functionality
3. **Advanced Caching**: Redis-like caching layer
4. **API Versioning**: Support for multiple API versions
5. **Request Queuing**: Queue management for rate-limited requests
6. **Analytics Integration**: Track API usage and performance
7. **A/B Testing**: API endpoint testing framework
