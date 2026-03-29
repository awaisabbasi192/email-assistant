# 🚀 Complete Render Deployment with OAuth Setup

This guide covers everything needed to deploy the Email Assistant with full Gmail OAuth integration.

---

## 📋 **Prerequisites**

Before deploying, complete:
1. Google Cloud OAuth setup (see GOOGLE_CLOUD_SETUP.md)
2. Have your `google_credentials.json` file ready
3. Render account (free)

---

## 🔐 **Step 1: Prepare OAuth Credentials**

### **Get Your Credentials**

From Google Cloud:
```json
{
  "client_id": "xxxx-xxxx.apps.googleusercontent.com",
  "client_secret": "GOCSP...",
  "redirect_uris": [
    "http://localhost:5000/auth/callback",
    "https://email-assistant-xxx.onrender.com/auth/callback"
  ]
}
```

**Save these values!**

---

## 🌐 **Step 2: Deploy to Render**

### **2.1: Go to Render Dashboard**
```
https://dashboard.render.com
```

### **2.2: Click on Your Service**
- Find: `email-assistant`
- Click to open

### **2.3: Manual Deploy**
1. Top right → **"Manual Deploy"**
2. Select **"Deploy latest commit"**
3. Wait 2-3 minutes

---

## 🔑 **Step 3: Add Environment Variables to Render**

After deployment succeeds:

1. **Go to Service** → **email-assistant**
2. **Settings** → **Environment**
3. Add these variables:

```
GOOGLE_CLIENT_ID = xxxx-xxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET = GOCSP...
GOOGLE_REDIRECT_URI = https://email-assistant-xxx.onrender.com/auth/callback
ANTHROPIC_API_KEY = sk-ant-xxxxx
```

4. Click **"Save"**
5. Service will auto-restart with new variables

---

## 📂 **Step 4: Add google_credentials.json to Render**

### **Option A: Via Secrets (Recommended)**

1. Go to Service **Settings**
2. Click **"Add Secret File"** (if available)
3. Name: `google_credentials.json`
4. Content: Paste your full credentials JSON

### **Option B: Via Environment Variable**

If no secret file option:
1. Create single JSON string of credentials
2. Add as env var: `GOOGLE_CREDENTIALS_JSON`
3. Update code to use: `os.getenv('GOOGLE_CREDENTIALS_JSON')`

---

## ✅ **Step 5: Update Google Cloud**

In Google Cloud Console:

1. Go to **OAuth consent screen**
2. **Test users** → Add: `your-email@gmail.com`

---

## 🧪 **Step 6: Test Complete Flow**

### **Test Locally First (Recommended)**

```bash
# Clone fresh
git clone https://github.com/awaisabbasi192/email-assistant.git
cd email-assistant

# Setup venv
python -m venv venv
venv\Scripts\activate  # Windows

# Install deps
pip install -r requirements.txt

# Add credentials
# Place google_credentials.json in project root

# Add .env file
ANTHROPIC_API_KEY=sk-ant-xxxx
GOOGLE_CLIENT_ID=xxxx
GOOGLE_CLIENT_SECRET=xxxx
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback

# Run
cd web_ui
python app.py
```

### **Test Flow**

1. Go: `http://localhost:5000`
2. Sign up (or login as awais/admin)
3. Click **Gmail Setup**
4. Click **"🔐 Connect Gmail Account"**
5. **Browser opens Google login**
6. Sign in with your email
7. Click **"Allow"**
8. **Redirects back to dashboard**
9. Gmail should show as **"Connected"**

---

## 🌍 **Deploy Live**

Once local testing works:

1. **Commit changes**
   ```bash
   git add .
   git commit -m "Add complete OAuth flow for Gmail"
   git push origin main
   ```

2. **Render auto-deploys** (2-3 minutes)

3. **Add environment variables to Render dashboard**

4. **Test on live URL**
   ```
   https://email-assistant-xxx.onrender.com
   ```

---

## 📱 **Share with Users**

Link for users:
```
https://email-assistant-xxx.onrender.com
```

**User flow:**
1. Sign up
2. Click "Gmail Setup"
3. Click "Connect Gmail Account"
4. Authorize with their Google account
5. Agent starts processing their emails!

---

## 🔒 **Security Checklist**

✅ `google_credentials.json` not in GitHub (in .gitignore)
✅ Env variables set only on Render
✅ Tokens encrypted in database
✅ OAuth tokens stored securely
✅ User credentials never exposed

---

## 🆘 **Troubleshooting**

### **"Invalid client" error**
- Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET match exactly
- No extra spaces

### **"Redirect URI mismatch"**
- Ensure GOOGLE_REDIRECT_URI matches exactly in Google Cloud
- Must include `https://` for Render

### **"google_credentials.json not found"**
- Either:
  - Place file in project root, OR
  - Add as Render secret file, OR
  - Use env variable for JSON content

### **OAuth button not showing**
- GOOGLE_CLIENT_ID not set
- Check environment variables on Render dashboard

### **"Access denied" after authorizing**
- User not in Google Cloud test users list
- Add email to test users in Google Cloud OAuth consent screen

---

## 📊 **Monitor on Render**

- **Logs** → Check for OAuth errors
- **Metrics** → Monitor CPU/Memory
- **Environment** → Verify all variables set

---

## 🚀 **Next Steps**

1. ✅ Complete Google Cloud OAuth setup
2. ✅ Deploy to Render
3. ✅ Add environment variables
4. ✅ Test complete flow
5. ✅ Share with users!

---

**Ready to deploy?** Follow steps 1-6 and you're live! 🎉

---

**Created**: March 30, 2026
**Status**: Production Ready ✅
