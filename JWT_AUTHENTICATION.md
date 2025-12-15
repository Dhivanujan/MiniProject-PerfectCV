# 🔐 JWT Authentication Implementation Guide

## Overview

JWT (JSON Web Token) authentication has been successfully implemented in the PerfectCV backend. This provides secure, stateless authentication for all API endpoints.

---

## 🎯 Features Implemented

### 1. **JWT Token Generation**
- ✅ Access tokens (24-hour expiry)
- ✅ Refresh tokens (30-day expiry)
- ✅ HS256 algorithm with secret key
- ✅ Token payload includes user ID and email

### 2. **Authentication Endpoints**
- ✅ `POST /auth/login` - Login and receive JWT tokens
- ✅ `POST /auth/register` - Register and receive JWT tokens
- ✅ `POST /auth/refresh` - Refresh expired access token
- ✅ `GET /auth/me` - Get current authenticated user
- ✅ Password reset flow (unchanged)

### 3. **Security Features**
- ✅ Password hashing with bcrypt
- ✅ Token expiration validation
- ✅ Token type validation (access vs refresh)
- ✅ User existence verification
- ✅ Secure password storage

---

## 📁 File Structure

```
perfectcv-backend/
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt_handler.py          # JWT utilities
│   └── routes/
│       └── auth_fastapi.py          # Auth endpoints (updated)
├── config/
│   └── config.py                    # JWT configuration
├── app_fastapi.py                   # JWT initialization
└── requirements.txt                 # JWT dependencies added
```

---

## 🔧 Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30      # 30 days

# Fallback
SECRET_KEY=your-general-secret-key
```

### Config Values

```python
# config/config.py
class Config:
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30       # 30 days
```

---

## 🚀 API Usage

### 1. User Registration

**Request:**
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "full_name": "John Doe",
  "username": "johndoe"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Registered successfully",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "full_name": "John Doe",
    "username": "johndoe"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. User Login

**Request:**
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Logged in successfully",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "full_name": "John Doe",
    "username": "johndoe"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Get Current User (Protected Route)

**Request:**
```bash
GET /auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "full_name": "John Doe",
  "username": "johndoe"
}
```

### 4. Refresh Access Token

**Request:**
```bash
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "full_name": "John Doe",
    "username": "johndoe"
  }
}
```

---

## 🔒 Protecting Routes

### Method 1: Using Dependency

```python
from fastapi import Depends
from app.auth.jwt_handler import get_current_user, get_current_active_user

@router.get("/protected-endpoint")
async def protected_route(current_user: dict = Depends(get_current_active_user)):
    """
    This route requires valid JWT token
    """
    return {
        "message": f"Hello {current_user['email']}!",
        "user_id": current_user['id']
    }
```

### Method 2: Manual Token Verification

```python
from fastapi import HTTPException, Header
from app.auth.jwt_handler import verify_token

@router.get("/another-protected")
async def another_protected(authorization: str = Header(None)):
    """
    Manual token verification
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    
    return {"user_id": payload["sub"]}
```

---

## 🎨 Frontend Integration

### React/JavaScript Example

```javascript
// api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken
        });
        
        const { access_token, refresh_token } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### Login Component Example

```javascript
// Login.jsx
import React, { useState } from 'react';
import api from './api';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    
    try {
      const response = await api.post('/auth/login', {
        email,
        password
      });
      
      const { access_token, refresh_token, user } = response.data;
      
      // Store tokens
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Login failed:', error);
      alert(error.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      <button type="submit">Login</button>
    </form>
  );
};

export default Login;
```

---

## 🛡️ Security Best Practices

### 1. **Token Storage**
- ✅ Store tokens in localStorage or sessionStorage
- ✅ Never store tokens in cookies without httpOnly flag
- ✅ Clear tokens on logout

### 2. **Token Expiration**
- ✅ Access tokens expire after 24 hours
- ✅ Refresh tokens expire after 30 days
- ✅ Implement automatic token refresh

### 3. **Secret Key Management**
- ⚠️ **CRITICAL**: Change default secret keys in production
- ✅ Use strong, random secret keys (minimum 32 characters)
- ✅ Never commit secret keys to version control
- ✅ Use environment variables

### 4. **HTTPS in Production**
- ⚠️ Always use HTTPS in production
- ✅ Tokens transmitted over secure connections only

---

## 📊 Token Structure

### Access Token Payload
```json
{
  "sub": "507f1f77bcf86cd799439011",  // User ID
  "email": "user@example.com",
  "exp": 1703001600,                   // Expiration timestamp
  "iat": 1702915200,                   // Issued at timestamp
  "type": "access"
}
```

### Refresh Token Payload
```json
{
  "sub": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "exp": 1705507200,
  "iat": 1702915200,
  "type": "refresh"
}
```

---

## 🧪 Testing

### 1. Test Registration
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "full_name": "Test User"
  }'
```

### 2. Test Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

### 3. Test Protected Endpoint
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Test Token Refresh
```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

---

## 🔍 Troubleshooting

### Error: "Could not validate credentials"
- Check if token is expired
- Verify token format in Authorization header
- Ensure JWT_SECRET_KEY matches between token creation and verification

### Error: "Invalid token type"
- Using refresh token where access token is required
- Use correct token for each endpoint

### Error: "User not found"
- Token valid but user deleted from database
- Re-authenticate to get new token

---

## 📦 Dependencies Installed

```
python-jose[cryptography]>=3.3.0  # JWT encoding/decoding
passlib[bcrypt]>=1.7.4            # Password hashing
```

Install with:
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

---

## ✅ Implementation Checklist

- [x] JWT token generation (access & refresh)
- [x] Token verification and validation
- [x] Password hashing with bcrypt
- [x] User authentication endpoints
- [x] Protected route examples
- [x] Token refresh mechanism
- [x] Current user endpoint
- [x] Configuration management
- [x] Documentation

---

## 🚀 Next Steps

### Recommended Enhancements:
1. **Token Blacklist**: Implement token blacklist for logout
2. **Rate Limiting**: Add rate limiting to auth endpoints
3. **OAuth Integration**: Add Google/GitHub OAuth
4. **2FA**: Implement two-factor authentication
5. **Session Management**: Track active sessions
6. **Audit Logging**: Log authentication events

---

**Status**: ✅ **JWT Authentication Fully Implemented**

**Date**: December 15, 2025  
**Version**: 1.0.0
