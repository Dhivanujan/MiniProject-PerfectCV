# Git Commit Instructions

After setting up the React frontend, follow these git commits:

## Commit 1: Initial React Setup and Project Structure
```bash
git add frontend/package.json frontend/public/ frontend/src/index.js frontend/src/index.css
git commit -m "feat: Initial React project setup with basic structure"
```

## Commit 2: Main App Component and Routing Setup
```bash
git add frontend/src/App.js frontend/src/context/AuthContext.js
git commit -m "feat: Add React Router and Authentication context setup"
```

## Commit 3: Navigation Component and Home Page
```bash
git add frontend/src/components/Navbar.js frontend/src/pages/Home.js
git commit -m "feat: Convert home page and navigation to React components"
```

## Commit 4: Login and Register Components
```bash
git add frontend/src/pages/Login.js frontend/src/pages/Register.js
git commit -m "feat: Convert login and register forms to React components"
```

## Commit 5: Dashboard and Password Reset Components
```bash
git add frontend/src/pages/Dashboard.js frontend/src/pages/ForgotPassword.js frontend/src/pages/ResetPassword.js frontend/README.md
git commit -m "feat: Complete React conversion with dashboard and password reset components"
```

## Setup Instructions

1. Copy static files to frontend/public/static/:
   - Copy static/Hero.png to frontend/public/static/Hero.png
   - Copy static/CV.png to frontend/public/static/CV.png
   - Copy static/Logo.png to frontend/public/static/Logo.png

2. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Start development server:
   ```bash
   npm start
   ```

## Backend Modifications Needed

You'll need to create API endpoints in your Flask app to support the React frontend:

```python
# Add these routes to your Flask app
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    # Handle login logic
    pass

@app.route('/api/auth/register', methods=['POST'])  
def api_register():
    # Handle registration logic
    pass

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    # Handle logout logic
    pass

@app.route('/api/auth/check', methods=['GET'])
def api_check_auth():
    # Check if user is authenticated
    pass

@app.route('/api/auth/forgot-password', methods=['POST'])
def api_forgot_password():
    # Handle forgot password logic
    pass

@app.route('/api/auth/reset-password', methods=['POST'])
def api_reset_password():
    # Handle password reset logic
    pass
```