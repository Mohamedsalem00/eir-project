# Navigation System Documentation

## Overview
The navigation system has been reorganized into a modular component-based architecture that provides different experiences for visitors and authenticated users.

## Components

### 1. Navigation Component (`src/components/Navigation.tsx`)
- **Responsive Design**: Mobile-first approach with hamburger menu
- **Conditional Rendering**: Shows different navigation items based on user authentication status
- **Language Support**: Integrated language switcher for French, English, and Arabic
- **User Menu**: Dropdown menu for authenticated users with profile and logout options

### 2. Authentication Context (`src/contexts/AuthContext.tsx`)
- **User State Management**: Manages user authentication state across the application
- **Login/Register Functions**: Handles user authentication and registration
- **Token Storage**: Manages JWT tokens in localStorage
- **Profile Management**: Fetches and manages user profile data

### 3. Login Form (`src/components/LoginForm.tsx`)
- **Form Validation**: Client-side validation for email and password
- **Error Handling**: Displays authentication errors and validation messages
- **Responsive Design**: Mobile-friendly form layout
- **Internationalization**: Supports multiple languages

### 4. Register Form (`src/components/RegisterForm.tsx`)
- **User Registration**: Complete registration form with validation
- **Password Confirmation**: Ensures password confirmation matches
- **User Type Selection**: Allows selection between regular user and administrator
- **Form Validation**: Comprehensive client-side validation

## Pages

### 1. Home Page (`app/page.tsx`)
- **Updated Navigation**: Now uses the Navigation component
- **User Context**: Integrates with authentication system
- **Conditional Content**: Can show different content based on user status

### 2. Login Page (`app/login/page.tsx`)
- **Authentication Form**: Renders the LoginForm component
- **Clean Layout**: Minimal, focused design for better UX

### 3. Register Page (`app/register/page.tsx`)
- **Registration Form**: Renders the RegisterForm component
- **User Onboarding**: Complete user registration flow

### 4. Dashboard Page (`app/dashboard/page.tsx`)
- **Protected Route**: Only accessible to authenticated users
- **User Overview**: Displays user information and quick actions
- **Navigation Integration**: Uses Navigation component with user context

### 5. Profile Page (`app/profile/page.tsx`)
- **User Profile**: Detailed user information and statistics
- **Account Management**: Actions for profile modification and password changes
- **Protected Access**: Requires authentication

## Features

### For Visitors (Unauthenticated Users)
- **Public Navigation**: Access to home, IMEI information, and API testing
- **Authentication Options**: Login and register buttons prominently displayed
- **Language Support**: Full internationalization support

### For Authenticated Users
- **Enhanced Navigation**: Additional menu items for dashboard and profile
- **User Menu**: Dropdown with user name, profile access, and logout
- **Protected Routes**: Access to dashboard and profile pages
- **Personalized Experience**: User-specific content and features

## Technical Implementation

### State Management
- **React Context**: Uses Context API for global state management
- **Local Storage**: JWT tokens stored securely in browser storage
- **User Persistence**: User state maintained across page refreshes

### Routing
- **Next.js App Router**: Modern file-based routing system
- **Protected Routes**: Automatic redirection for unauthenticated users
- **Dynamic Navigation**: Navigation adapts based on current route and user status

### Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Responsive Design**: Mobile-first approach with breakpoint-based layouts
- **Consistent UI**: Unified design language across all components

## Usage Examples

### Adding New Navigation Items
```tsx
// In Navigation.tsx, add new items to the nav array
<nav className="flex items-center space-x-6 text-sm">
  <Link href="/" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">
    {t('accueil')}
  </Link>
  {/* Add new navigation items here */}
  <Link href="/new-page" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">
    {t('new_page')}
  </Link>
</nav>
```

### Creating Protected Pages
```tsx
// In any new protected page
'use client'

import { useAuth } from '../../src/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function ProtectedPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login')
    }
  }, [user, isLoading, router])

  if (!user) return null

  return (
    <div>
      {/* Protected content here */}
    </div>
  )
}
```

## Future Enhancements

1. **Role-Based Access Control**: Implement different navigation based on user roles
2. **Notification System**: Add notification indicators in navigation
3. **Search Integration**: Global search functionality in navigation
4. **Theme Switching**: Dark/light mode toggle
5. **Advanced User Menu**: Enhanced dropdown with additional options

## Maintenance

- **Translation Keys**: Add new keys to all language files (fr.json, en.json, ar.json)
- **Component Updates**: Modify Navigation.tsx for structural changes
- **Route Protection**: Use useAuth hook for any new protected pages
- **Testing**: Ensure navigation works correctly on all device sizes and languages
