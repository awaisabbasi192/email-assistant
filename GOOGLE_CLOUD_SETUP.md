# 🔐 Google Cloud OAuth Setup Guide

This guide will help you set up Google Cloud project so users can securely connect their Gmail accounts.

---

## 📋 **Complete Step-by-Step Setup**

### **Step 1: Create Google Cloud Project**

1. Go: **https://console.cloud.google.com/**
2. Click **Project Dropdown** (top left, near "Google Cloud")
3. Click **"NEW PROJECT"**
4. **Project Name**: `Email Assistant`
5. Click **"CREATE"**
6. Wait 1-2 minutes for project to be created

---

### **Step 2: Enable Gmail API**

1. Top search bar, type: `Gmail API`
2. Click **"Gmail API"** from results
3. Click **"ENABLE"** button
4. Wait for it to enable (shows "API enabled")

---

### **Step 3: Create OAuth Consent Screen**

1. Left sidebar → **APIs & Services** → **OAuth consent screen**
2. **User Type**: Select **"External"**
3. Click **"CREATE"**

**Fill Form:**
- **App name**: `Email Assistant`
- **User support email**: Your Gmail address
- **Developer contact information**: Your Gmail address
- Click **"SAVE AND CONTINUE"**

**Scopes Page:**
- Click **"ADD OR REMOVE SCOPES"**
- Search: `gmail`
- Select:
  - `https://www.googleapis.com/auth/gmail.modify` (Read/Modify)
  - `https://www.googleapis.com/auth/gmail.readonly` (Read only)
- Click **"UPDATE"**
- Click **"SAVE AND CONTINUE"**

**Test Users Page:**
- Click **"ADD USERS"**
- Add your Gmail address
- Click **"ADD"** → **"SAVE AND CONTINUE"**

---

### **Step 4: Create OAuth 2.0 Credentials**

1. Left sidebar → **APIs & Services** → **Credentials**
2. Click **"+ CREATE CREDENTIALS"** (top)
3. Select **"OAuth client ID"**

**Configure:**
- **Application type**: **"Web application"**
- **Name**: `Email Assistant Web`

**Authorized JavaScript origins:**
- Add: `http://localhost:5000`
- Add: `https://email-assistant-xxx.onrender.com` (replace xxx with your Render service name)

**Authorized redirect URIs:**
- Add: `http://localhost:5000/auth/callback`
- Add: `https://email-assistant-xxx.onrender.com/auth/callback`

4. Click **"CREATE"**
5. **Download JSON** (click download button)
6. Save as **`google_credentials.json`** in your project folder

---

### **Step 5: Get Your Client ID & Secret**

In the JSON file you downloaded, you'll see:
```json
{
  "client_id": "xxxx-xxxx.apps.googleusercontent.com",
  "client_secret": "GOCSP...",
  ...
}
```

**Save these values!** You'll need them.

---

## 🚀 **Step 6: Add to Your Project**

1. Place `google_credentials.json` in project root:
   ```
   C:\Users\awais\OneDrive\Desktop\email assistant\google_credentials.json
   ```

2. Add to `.gitignore` (so it doesn't push to GitHub)

3. Set environment variables:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

---

## 🌐 **Step 7: On Render - Add Secrets**

1. Go: **Render Dashboard**
2. Click **`email-assistant`** service
3. Go to **"Environment"**
4. Add variables:
   - `GOOGLE_CLIENT_ID`: Your client ID
   - `GOOGLE_CLIENT_SECRET`: Your client secret
   - `GOOGLE_REDIRECT_URI`: `https://email-assistant-xxx.onrender.com/auth/callback`

---

## ✅ **Verification**

Once done, your app will:
1. Show "Connect Gmail" button
2. When user clicks it → redirects to Google login
3. User authorizes
4. Gets OAuth token
5. Can read/write emails!

---

## 🔒 **Security Notes**

✅ Credentials stored securely in Render secrets
✅ OAuth tokens encrypted in database
✅ User controls what app can access
✅ Can be revoked anytime

---

## 🆘 **Troubleshooting**

### **"Redirect URI mismatch"**
- Make sure redirect URI exactly matches in Google Cloud
- Include `http://` or `https://`

### **"Invalid client"**
- Check CLIENT_ID and CLIENT_SECRET are correct
- No extra spaces

### **"Gmail API not enabled"**
- Go back to Step 2, ensure API is enabled

---

**Setup complete! App will now handle full OAuth flow!** ✅
