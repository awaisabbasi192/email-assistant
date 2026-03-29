# Authentication & Email Setup Guide

## Overview

Email Assistant now has a complete **multi-user authentication system** with:
- ✅ User Registration (Sign Up)
- ✅ User Login/Logout
- ✅ Gmail Email Configuration
- ✅ Admin Account (awais/admin)

---

## 🔐 Default Admin Account

**Username:** `awais`
**Password:** `admin`

⚠️ **IMPORTANT:** Change this password immediately after first login!

---

## 📋 User Journey

### Step 1: Sign Up (New Users)
```
Visit: https://your-app.onrender.com/register
- Enter Username (3-50 characters)
- Enter Email (for account recovery)
- Create Password (minimum 6 characters)
- Confirm Password
- Click "Create Account"
```

### Step 2: Login
```
Visit: https://your-app.onrender.com/login
- Enter Username
- Enter Password
- Click "Login"
```

### Step 3: Configure Gmail Email
```
After Login:
1. Go to Settings → Gmail Configuration
2. Enter your Gmail email address (must be @gmail.com)
3. Click "Connect Gmail"
4. The agent will start generating drafts for your emails
```

---

## 🔧 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,           -- Login username
    email TEXT UNIQUE NOT NULL,              -- Account email
    password_hash TEXT NOT NULL,             -- Bcrypt hashed password
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,                    -- Last login time
    is_active BOOLEAN DEFAULT 1,             -- Account status
    gmail_connected BOOLEAN DEFAULT 0,       -- Gmail connected status
    gmail_email TEXT                         -- Gmail email address
)
```

---

## 🚀 Deployment Steps (Render.com)

### 1. Create Admin User (First Time Setup)

Before deploying, run:
```bash
python setup_admin.py
```

This creates the admin user:
- Username: `awais`
- Password: `admin`

### 2. Deploy to Render

See `RENDER_DEPLOYMENT.md` for detailed instructions.

### 3. After Deployment

1. Visit your deployed app URL
2. Click "Sign up here" link on login page
3. Create your account
4. Login with your credentials
5. Go to Settings → Gmail Configuration
6. Enter your Gmail address
7. Start using the assistant!

---

## 👤 User Features

### Authentication
- ✅ Secure password hashing (bcrypt)
- ✅ Session management
- ✅ Login/Logout
- ✅ Account creation
- ✅ Password validation (minimum 6 characters)

### Gmail Configuration
- ✅ Connect Gmail account
- ✅ Update Gmail email
- ✅ Disconnect Gmail
- ✅ Email status display

### Security
- ✅ CSRF protection
- ✅ Rate limiting (5 requests per minute on login)
- ✅ Secure session cookies
- ✅ Password hashing with bcrypt
- ✅ User account activation status

---

## 🔑 Routes

### Authentication Routes
- `GET/POST /login` - Login page and handler
- `GET/POST /register` - Registration page and handler
- `POST /logout` - Logout handler

### Settings Routes
- `GET /gmail-settings` - Gmail configuration page
- `POST /api/gmail-settings` - Update Gmail settings
- `POST /api/gmail-disconnect` - Disconnect Gmail

### Protected Routes (Require Login)
- `/dashboard` - Main dashboard
- `/emails` - Email list
- `/drafts` - Draft management
- `/analytics` - Analytics
- `/settings` - General settings
- All `/api/*` routes

---

## 🐛 Troubleshooting

### "Admin user already exists" message
This is expected. The admin user (awais/admin) has already been created.

### Cannot login
1. Check username and password
2. Ensure account is active
3. Try resetting by running `setup_admin.py` again

### Gmail not connecting
1. Ensure email is a valid @gmail.com address
2. Check database for errors in logs
3. Verify internet connection

### Database issues
If database is corrupted:
```bash
# Delete and reinitialize
rm email_assistant.db
python setup_admin.py
```

---

## 📱 Mobile Access

Works on all devices:
- ✅ Mobile browsers
- ✅ Tablets
- ✅ Desktop browsers
- ✅ Responsive design included

---

## 🔒 Security Best Practices

1. **Change Admin Password** - Do this immediately after first login
2. **Use Strong Passwords** - Minimum 6 characters, consider longer
3. **Secure Transmission** - Always use HTTPS (Render provides this)
4. **Backup Database** - Regularly backup `email_assistant.db`
5. **Monitor Logs** - Check logs for suspicious login attempts

---

## 🛠️ Configuration

Edit `config.json` for:
```json
{
  "web_ui": {
    "session_timeout_minutes": 1440,
    "session_cookie_secure": true,
    "debug": false
  }
}
```

---

## 📞 Support

For issues:
1. Check logs: `email_assistant.log`
2. Review console output
3. Check GitHub issues: https://github.com/awaisabbasi192/email-assistant

---

## 🎉 You're All Set!

Your email assistant is ready to use with:
- ✅ Multi-user support
- ✅ Secure authentication
- ✅ Gmail integration
- ✅ Draft generation
- ✅ Mobile access

Enjoy automated email assistance! 📧
