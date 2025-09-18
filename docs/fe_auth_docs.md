# Authentication API - Frontend Integration Guide

## Overview
Our authentication system now provides **immediate logout** - when a user logs out, all API endpoints become inaccessible instantly (no waiting for token expiry).

## Token Lifetimes
- **Access Token**: 15 minutes
- **Refresh Token**: 60 minutes
- **Auto-rotation**: Enabled (new refresh token on each refresh)

## Endpoints

### Login
```http
POST /auth/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Logout
```http
POST /auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "message": "Logout successful - all tokens invalidated"
}
```

### Refresh Token
```http
POST /auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Implementation Examples

### React/JavaScript
```javascript
class AuthService {
  async login(username, password) {
    const response = await fetch('/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    if (response.ok) {
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
    }
    return data;
  }

  async logout() {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    // Call logout endpoint with both tokens
    await fetch('/auth/logout/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    
    // Clear storage immediately
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    const response = await fetch('/auth/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      return data;
    } else {
      // Refresh failed - redirect to login
      this.logout();
      throw new Error('Session expired');
    }
  }

  // Auto-retry with refresh on 401
  async apiCall(url, options = {}) {
    const accessToken = localStorage.getItem('access_token');
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    if (response.status === 401) {
      // Try refreshing token
      try {
        await this.refreshToken();
        // Retry original request
        const newToken = localStorage.getItem('access_token');
        return fetch(url, {
          ...options,
          headers: {
            'Authorization': `Bearer ${newToken}`,
            'Content-Type': 'application/json',
            ...options.headers
          }
        });
      } catch {
        // Refresh failed - logout
        window.location.href = '/login';
      }
    }
    
    return response;
  }
}
```

### Axios Interceptor Example
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api'
});

// Request interceptor to add auth header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await fetch('/auth/refresh/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh: refreshToken })
        });
        
        if (response.ok) {
          const data = await response.json();
          localStorage.setItem('access_token', data.access);
          localStorage.setItem('refresh_token', data.refresh);
          
          // Retry original request
          error.config.headers.Authorization = `Bearer ${data.access}`;
          return api.request(error.config);
        }
      } catch (refreshError) {
        // Refresh failed - logout
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);
```

## Important Notes

### ⚠️ Critical Requirements
1. **Always send refresh token in logout** - This ensures immediate invalidation
2. **Include Authorization header in logout** - Current access token is also blacklisted
3. **Clear storage immediately** after logout call

### 🔄 Token Rotation
- Each refresh call returns a NEW refresh token
- Always update storage with both new tokens
- Old tokens become invalid immediately

### 🚫 Instant Logout Effect
- After logout, ALL API calls with old tokens fail immediately
- No grace period - protection is instant
- Users cannot access protected resources even if tokens haven't expired

### 📱 Multiple Device Support
- Logout only affects the current session
- Other devices remain logged in with their own token pairs
- Each login creates independent token pairs

## Error Responses

| Status | Error | Action |
|--------|-------|---------|
| 401 | Token expired/invalid | Refresh token or redirect to login |
| 400 | Invalid refresh token | Clear storage, redirect to login |
| 400 | Missing refresh token in logout | Include refresh_token in request body |

## Testing & Development

### Token Invalidation for Testing
To test the logout functionality properly, you may need to invalidate existing tokens:

```bash
# Invalidate all existing tokens (for testing)
python manage.py invalidate_all_tokens --confirm
```

### Admin Dashboard Integration (Optional)
The token invalidation can be integrated into your admin dashboard as an emergency logout-all-users feature:

```javascript
// Admin dashboard button
const invalidateAllTokens = async () => {
  const confirmed = confirm(
    'This will log out ALL users immediately. Continue?'
  );
  
  if (confirmed) {
    try {
      await fetch('/admin/invalidate-all-tokens/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        }
      });
      alert('All user sessions invalidated');
    } catch (error) {
      alert('Failed to invalidate tokens');
    }
  }
};
```

**Backend endpoint for admin:**
```python
# In your admin views
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def invalidate_all_tokens_view(request):
    """Admin endpoint to invalidate all user tokens"""
    from django.core.management import call_command
    
    try:
        call_command('invalidate_all_tokens', confirm=True)
        return Response({
            'message': 'All user sessions invalidated successfully'
        })
    except Exception as e:
        return Response({
            'error': 'Failed to invalidate tokens'
        }, status=500)
```

### Use Cases for Token Invalidation
- **Security Breach**: Force logout all users immediately
- **System Maintenance**: Clear sessions before major updates
- **Testing**: Clean slate for authentication testing
- **User Management**: Admin override for problematic accounts

## Testing Checklist
- [ ] Login stores both tokens
- [ ] Logout sends both tokens and clears storage
- [ ] API calls include Authorization header
- [ ] 401 responses trigger token refresh
- [ ] Failed refresh redirects to login
- [ ] After logout, API calls fail immediately
- [ ] Token invalidation command works for testing
- [ ] Admin token invalidation (if implemented) works correctly
