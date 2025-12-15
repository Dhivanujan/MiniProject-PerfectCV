# 🚀 JWT Authentication - Quick Start Guide

## ✅ Installation Complete

JWT authentication has been successfully implemented in your PerfectCV project!

---

## 📋 What Was Implemented

### 1. **Backend Components**
- ✅ `app/auth/jwt_handler.py` - JWT utilities (token generation, verification)
- ✅ `app/auth/__init__.py` - Auth module exports
- ✅ Updated `app/routes/auth_fastapi.py` - JWT-enabled auth endpoints
- ✅ Updated `config/config.py` - JWT configuration
- ✅ Updated `app_fastapi.py` - JWT initialization on startup
- ✅ Updated `requirements.txt` - Added JWT dependencies

### 2. **Dependencies Installed**
```bash
✅ python-jose[cryptography]==3.5.0
✅ passlib[bcrypt]==1.7.4
```

---

## 🔧 Setup Steps

### 1. Configure Environment Variables

Create or update your `.env` file:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# MongoDB
MONGO_URI=mongodb://localhost:27017/perfectcv

# Other keys (if needed)
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
```

**⚠️ IMPORTANT:** Generate a strong secret key:
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or OpenSSL
openssl rand -hex 32
```

---

## 🚀 Start the Server

```bash
cd perfectcv-backend
python run.py
```

Or:
```bash
uvicorn app_fastapi:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

---

## 🧪 Test Authentication

### 1. Test Registration (Get Tokens)

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Registered successfully",
  "user": {...},
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 2. Test Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

### 3. Test Protected Endpoint

```bash
# Replace YOUR_TOKEN with the access_token from login
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📚 API Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/auth/register` | POST | No | Register new user, get tokens |
| `/auth/login` | POST | No | Login, get tokens |
| `/auth/refresh` | POST | No | Refresh access token |
| `/auth/me` | GET | **Yes** | Get current user info |
| `/auth/forgot-password` | POST | No | Request password reset |
| `/auth/verify-code` | POST | No | Verify reset code |
| `/auth/reset-password` | POST | No | Reset password |
| `/auth/logout` | POST | No | Logout (client discards tokens) |

---

## 🎨 Frontend Integration

### Update your `api.js`:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Add token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      const refresh = localStorage.getItem('refresh_token');
      
      try {
        const { data } = await axios.post(
          'http://localhost:8000/auth/refresh',
          { refresh_token: refresh }
        );
        
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        
        error.config.headers.Authorization = `Bearer ${data.access_token}`;
        return api(error.config);
      } catch (e) {
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Update Login Component:

```javascript
// Login.jsx - Update handleLogin function
const handleLogin = async (e) => {
  e.preventDefault();
  
  try {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, refresh_token, user } = response.data;
    
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    localStorage.setItem('user', JSON.stringify(user));
    
    navigate('/dashboard');
  } catch (error) {
    setError(error.response?.data?.detail || 'Login failed');
  }
};
```

### Update Register Component:

```javascript
// Register.jsx - Update handleRegister function
const handleRegister = async (e) => {
  e.preventDefault();
  
  try {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
      username
    });
    
    const { access_token, refresh_token, user } = response.data;
    
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    localStorage.setItem('user', JSON.stringify(user));
    
    navigate('/dashboard');
  } catch (error) {
    setError(error.response?.data?.detail || 'Registration failed');
  }
};
```

---

## 🔒 Protecting Backend Routes

### Example: Protect CV Routes

```python
# app/routes/cv.py
from fastapi import Depends
from app.auth.jwt_handler import get_current_active_user

@router.post("/generate-cv")
async def generate_cv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_user)  # Add this
):
    """
    Protected route - requires JWT token
    """
    user_id = current_user['id']
    user_email = current_user['email']
    
    # Your existing code...
    return {"message": "CV generated for " + user_email}
```

---

## 📝 Token Flow

1. **User registers/logs in** → Receives access_token & refresh_token
2. **Client stores tokens** → localStorage or sessionStorage
3. **Client makes requests** → Sends `Authorization: Bearer <access_token>`
4. **Access token expires** → Client uses refresh_token to get new tokens
5. **Refresh token expires** → User must log in again

---

## 🛡️ Security Checklist

- [ ] Change `JWT_SECRET_KEY` to a strong random value (32+ characters)
- [ ] Never commit `.env` file to version control
- [ ] Use HTTPS in production
- [ ] Set appropriate token expiration times
- [ ] Clear tokens on logout
- [ ] Implement rate limiting for auth endpoints (optional)
- [ ] Add CORS configuration for your frontend domain

---

## 🔍 Testing with Swagger UI

1. Start the server
2. Open: `http://localhost:8000/docs`
3. Test `/auth/login` or `/auth/register`
4. Copy the `access_token` from response
5. Click "Authorize" button (top right)
6. Enter: `Bearer YOUR_ACCESS_TOKEN`
7. Now you can test protected endpoints!

---

## 📖 Documentation

Full documentation available in:
- `JWT_AUTHENTICATION.md` - Comprehensive guide
- `http://localhost:8000/docs` - Interactive API docs
- `http://localhost:8000/` - API overview

---

## ✨ Key Features

✅ Secure JWT-based authentication  
✅ Access & refresh token system  
✅ Automatic token refresh on frontend  
✅ Password hashing with bcrypt  
✅ Protected route dependencies  
✅ Token expiration validation  
✅ User session management  

---

## 🎉 You're All Set!

JWT authentication is now fully integrated into your PerfectCV project. Start the server and test the endpoints!

**Need Help?**
- Check `JWT_AUTHENTICATION.md` for detailed examples
- Visit `/docs` for interactive API testing
- Review error messages in terminal logs

---

**Status**: ✅ **Ready to Use**  
**Date**: December 15, 2025
