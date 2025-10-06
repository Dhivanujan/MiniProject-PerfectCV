# PerfectCV React Frontend

This is the React frontend for the PerfectCV application, converted from Flask templates.

## Setup Instructions

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm start
```

The application will run on `http://localhost:3000`

### 3. Build for Production
```bash
npm run build
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   └── Navbar.js
│   ├── context/
│   │   └── AuthContext.js
│   ├── pages/
│   │   ├── Home.js
│   │   ├── Login.js
│   │   ├── Register.js
│   │   ├── Dashboard.js
│   │   ├── ForgotPassword.js
│   │   └── ResetPassword.js
│   ├── App.js
│   ├── index.js
│   └── index.css
└── package.json
```

## Features Converted

1. ✅ Home page with navigation
2. ✅ Login/Register forms
3. ✅ Authentication context
4. ✅ Protected routes
5. ✅ Dashboard layout
6. ✅ Password reset functionality
7. ✅ Responsive design with Tailwind CSS

## Backend Integration

The frontend is configured to connect to a Flask backend at `http://localhost:5000`. Make sure your Flask app has the following API endpoints:

- `POST /api/auth/login`
- `POST /api/auth/register`
- `POST /api/auth/logout`
- `GET /api/auth/check`
- `POST /api/auth/forgot-password`
- `POST /api/auth/reset-password`

## Static Files

Copy your static files (images) to the `public/static/` directory:
- `public/static/Hero.png`
- `public/static/CV.png`
- `public/static/Logo.png`

## Environment Variables

Create a `.env` file in the frontend directory if you need to configure different API endpoints:

```
REACT_APP_API_URL=http://localhost:5000
```