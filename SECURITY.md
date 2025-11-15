# PerfectCV - Security Update

## ⚠️ Important: Environment Variables

The `.env` file has been removed from version control to protect sensitive credentials.

### Setup Instructions:

1. **Copy the example file:**
   ```bash
   cd perfectcv-backend
   cp .env.example .env
   ```

2. **Update `.env` with your actual credentials:**
   - `GOOGLE_API_KEY`: Get from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - `MONGO_URI`: Your MongoDB connection string
   - `MAIL_USERNAME` & `MAIL_PASSWORD`: Gmail SMTP credentials (use [App Password](https://support.google.com/accounts/answer/185833))
   - `SECRET_KEY`: Generate a random secret key

3. **Never commit `.env` file to Git**

### Important Note:
If you previously committed API keys, they are now exposed in Git history. You should:
1. **Revoke and regenerate all API keys** (Google API, MongoDB passwords, etc.)
2. Consider using `git filter-branch` or `BFG Repo-Cleaner` to remove sensitive data from history
3. Update all services with new credentials

### Current Protection:
- ✅ `.env` added to `.gitignore`
- ✅ `.env.example` template created
- ✅ Enhanced `.gitignore` for Python/Node projects
