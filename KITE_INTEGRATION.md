# Kite Connect Integration Guide

## Overview
This integration enables users to connect their Zerodha Kite accounts to the Agentic Trader platform using OAuth 2.0 flow.

## Architecture

### Backend (FastAPI)
**File**: `app/routes/kite_auth.py`

**Endpoints**:
1. **GET `/api/v1/auth/kite/login`**
   - Redirects user to Kite Connect authorization page
   - URL: `https://kite.zerodha.com/connect/login?api_key={API_KEY}`

2. **GET `/api/v1/auth/kite/callback`**
   - Handles the OAuth callback from Kite
   - Receives `request_token` from Kite
   - Generates access token using API secret
   - Automatically updates `ACCESS_TOKEN` in `app/companies.py`
   - Redirects back to frontend with status

3. **GET `/api/v1/auth/kite/status`**
   - Returns current authentication status
   - Response:
     ```json
     {
       "is_authenticated": true,
       "user_id": "ABC123",
       "expires_at": "2024-01-01T12:00:00"
     }
     ```

4. **POST `/api/v1/auth/kite/logout`**
   - Clears the session
   - Removes authentication

### Frontend (React)
**File**: `frontend/src/pages/KiteLogin.jsx`

**Features**:
- Beautiful gradient UI with Tailwind CSS
- Real-time authentication status display
- Success/error message handling
- Session expiry display
- One-click connect/disconnect buttons

**Route**: `/kite-login`

## Authentication Flow

```
1. User clicks "Connect to Kite" button
   ↓
2. Frontend redirects to: http://localhost:8000/api/v1/auth/kite/login
   ↓
3. Backend redirects to: https://kite.zerodha.com/connect/login?api_key=...
   ↓
4. User authorizes on Kite
   ↓
5. Kite redirects to: http://localhost:8000/api/v1/auth/kite/callback?request_token=...
   ↓
6. Backend:
   - Generates checksum (SHA256 of api_key + request_token + api_secret)
   - Exchanges request_token for access_token
   - Saves access_token in memory
   - Updates ACCESS_TOKEN in companies.py
   ↓
7. Backend redirects to: http://localhost:5173/?kite_auth=success&user_id=...
   ↓
8. Frontend displays success message
```

## Configuration

### Environment Variables (Optional)
You can set these in `.env` file:

```bash
KITE_API_KEY=your_api_key
KITE_API_SECRET=your_api_secret
KITE_REDIRECT_URL=http://localhost:8000/api/v1/auth/kite/callback
FRONTEND_URL=http://localhost:5173
```

### Current Hardcoded Values
- API_KEY: `2j2xf518ahokaidb`
- API_SECRET: `40zqlt7f0ippycpx97w5bxa5ij4b8z44`
- Redirect URL: `http://localhost:8000/api/v1/auth/kite/callback`
- Frontend URL: `http://localhost:5173`

## Usage

### 1. Start Backend
```bash
cd /home/shtlp_0170/Videos/hackthon/Agentic-Trader
python3 -m app.main
```
Backend runs on: http://localhost:8000

### 2. Start Frontend
```bash
cd /home/shtlp_0170/Videos/hackthon/Agentic-Trader/frontend
npm run dev
```
Frontend runs on: http://localhost:5173

### 3. Access Kite Login Page
Navigate to: http://localhost:5173/kite-login

### 4. Connect to Kite
1. Click "Connect to Kite" button
2. Login with your Zerodha credentials
3. Authorize the application
4. You'll be redirected back with success message

## Features

### Session Management
- Access tokens are valid for **24 hours**
- Session stored in-memory (resets on server restart)
- Automatic token update in `companies.py`

### Security
- Uses SHA256 checksum for token verification
- Credentials should be moved to environment variables in production
- HTTPS recommended for production

### Error Handling
- Authorization denied
- Invalid request token
- Session generation failed
- Network errors

## Testing

### Check Authentication Status
```bash
curl http://localhost:8000/api/v1/auth/kite/status
```

### Manual Logout
```bash
curl -X POST http://localhost:8000/api/v1/auth/kite/logout
```

## API Documentation
Visit: http://localhost:8000/docs

## Next Steps

1. **Production Ready**:
   - Move credentials to environment variables
   - Use Redis for session storage
   - Enable HTTPS
   - Add session persistence

2. **Enhanced Features**:
   - Add user profile display
   - Show account balance
   - Display holdings
   - Trading capabilities

3. **Security Improvements**:
   - Add CSRF protection
   - Implement rate limiting
   - Add session timeout warnings
   - Encrypt tokens at rest

## Troubleshooting

### Issue: Redirect URL mismatch
**Solution**: Make sure the redirect URL in your Kite app settings matches:
`http://localhost:8000/api/v1/auth/kite/callback`

### Issue: Access token not updating
**Solution**: Check file permissions on `app/companies.py`

### Issue: CORS errors
**Solution**: CORS is already configured in `application.py` to allow all origins in development

## Files Modified/Created

**Backend**:
- ✅ Created: `app/routes/kite_auth.py`
- ✅ Modified: `app/application.py` (added router)

**Frontend**:
- ✅ Created: `frontend/src/pages/KiteLogin.jsx`
- ✅ Modified: `frontend/src/App.jsx` (added route)
- ✅ Installed: `lucide-react` package

## Support
For issues or questions, refer to:
- Kite Connect Documentation: https://kite.trade/docs/connect/v3/
- Zerodha Support: https://support.zerodha.com/
