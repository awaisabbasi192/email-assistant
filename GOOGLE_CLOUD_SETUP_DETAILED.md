# 🔐 Google Cloud Setup - EXACT Steps (Copy-Paste Ready)

**Follow EXACTLY as written. Takes 10-15 minutes.**

---

## 📋 **Complete Checklist**

- [ ] Step 1: Create Project
- [ ] Step 2: Enable Gmail API
- [ ] Step 3: Configure Consent Screen
- [ ] Step 4: Create OAuth Credentials
- [ ] Step 5: Download JSON
- [ ] Step 6: Copy to Project Folder
- [ ] Done! ✅

---

## 🚀 **START HERE**

### **Step 1: Open Google Cloud Console**

**COPY & PASTE this URL in browser:**
```
https://console.cloud.google.com/
```

**Login with your Gmail account**

---

### **Step 2: Create New Project**

**Look for** → **Project Dropdown** (top left, next to "Google Cloud logo")

**Click it** → You'll see a popup

**In popup, click** → **"NEW PROJECT"** (top right of popup)

**Fill form:**
- **Project name:** `EmailAssistant`
- **Organization:** Leave empty (or your workspace)

**Click:** **"CREATE"**

**Wait 1-2 minutes** ⏳ (page will refresh automatically)

---

### **Step 3: Enable Gmail API**

**After project is created:**

**Top search bar** → Type: `gmail api`

**Click:** First result **"Gmail API"**

**Big button** → **"ENABLE"** (blue button in middle of page)

**Wait 30 seconds** (it will say "API enabled" at top)

---

### **Step 4: Configure Consent Screen**

**Left sidebar** → **APIs & Services** → **OAuth consent screen**

**Choose:** **"External"** (left option)

**Click:** **"CREATE"**

**Now fill the form:**

#### **App Information**
- **App name:** `EmailAssistant`
- **User support email:** Your Gmail address
- **Developer contact:** Your Gmail address

**Scroll down** → **"SAVE AND CONTINUE"**

---

#### **Scopes**

**"ADD OR REMOVE SCOPES"** button

**Search box** → Type: `gmail`

**Check these boxes:**
- ✅ `.../auth/gmail.modify`
- ✅ `.../auth/gmail.send`
- ✅ `.../auth/gmail.readonly`

**"UPDATE"** → **"SAVE AND CONTINUE"**

---

#### **Test Users**

**"ADD USERS"** button

**Enter:** Your Gmail address (john@gmail.com)

**"ADD"** button

**"SAVE AND CONTINUE"**

---

### **Step 5: Create OAuth Credentials**

**Left sidebar** → **APIs & Services** → **Credentials**

**Big button** → **"+ CREATE CREDENTIALS"** (top)

**Choose:** **"OAuth client ID"**

**Application type:** Click dropdown → **"Web application"**

**Name:** `EmailAssistant Web`

---

#### **Authorized JavaScript Origins**

**"ADD URI"** button → Enter:
```
http://localhost:5000
```

**"ADD URI"** button again → Enter:
```
https://email-assistant-xxx.onrender.com
```

(Replace `xxx` with your Render service name - you'll know it after deployment)

---

#### **Authorized Redirect URIs**

**"ADD URI"** button → Enter:
```
http://localhost:5000/auth/callback
```

**"ADD URI"** button again → Enter:
```
https://email-assistant-xxx.onrender.com/auth/callback
```

---

**"CREATE"** button (blue)

**Popup appears** with your credentials. **DON'T CLOSE IT YET!**

---

### **Step 6: Download & Copy Credentials**

**In the popup:**

**Right side** → **Download button** (⬇ icon)

**Click it** → `client_secret_xxx.json` downloads

**Rename file to:** `google_credentials.json`

---

## 📂 **Step 7: Add to Your Project**

**File Explorer:**

1. Open: `C:\Users\awais\OneDrive\Desktop\email assistant`

2. Paste `google_credentials.json` here (same folder as `app.py`)

---

## 📝 **Step 8: Create .env File**

**In same folder**, create file: `.env`

**Content (copy exactly):**
```
GOOGLE_CLIENT_ID=PASTE_YOUR_CLIENT_ID_HERE
GOOGLE_CLIENT_SECRET=PASTE_YOUR_CLIENT_SECRET_HERE
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

**To get Client ID & Secret:**

1. Go back to Google Cloud
2. **Credentials** page
3. Find your OAuth credential (listed as "EmailAssistant Web")
4. Click it
5. Copy:
   - **Client ID**
   - **Client Secret**
6. Paste in `.env` file

---

## ✅ **Verification Checklist**

Check you have:

- [ ] `google_credentials.json` in project folder
- [ ] `.env` file with:
  - `GOOGLE_CLIENT_ID` = filled
  - `GOOGLE_CLIENT_SECRET` = filled
  - `ANTHROPIC_API_KEY` = filled
- [ ] Google Cloud shows:
  - ✅ Gmail API enabled
  - ✅ OAuth consent screen configured
  - ✅ OAuth credentials created
  - ✅ Your Gmail in test users

---

## 🧪 **Quick Test (Local)**

```powershell
cd "C:\Users\awais\OneDrive\Desktop\email assistant"
cd web_ui
python app.py
```

1. Go: `http://localhost:5000`
2. Sign up / Login
3. Click **"Gmail Setup"**
4. Click **"🔐 Connect Gmail Account"**
5. **Browser opens Google login**
6. **Sign in** with your Gmail
7. **Click "Allow"**
8. **Should redirect back to dashboard**

✅ If this works, you're GOOD!

---

## 🚀 **Then Deploy to Render**

Once local test works:

1. `git pull origin main`
2. `git add .`
3. `git commit -m "Add Google credentials"`
4. `git push origin main`
5. Render auto-deploys
6. Add env vars in Render dashboard:
   ```
   GOOGLE_CLIENT_ID = xxx
   GOOGLE_CLIENT_SECRET = xxx
   ANTHROPIC_API_KEY = sk-ant-xxx
   GOOGLE_REDIRECT_URI = https://email-assistant-xxx.onrender.com/auth/callback
   ```
7. Done! ✅

---

## 📝 **Copy-Paste Checklist**

**Google Cloud URLs:**
- Console: https://console.cloud.google.com/
- Gmail API: https://console.cloud.google.com/apis/library/gmail.googleapis.com

**Exact Values to Enter:**

App Name:
```
EmailAssistant
```

Localhost URIs:
```
http://localhost:5000
http://localhost:5000/auth/callback
```

Render URIs (LATER):
```
https://email-assistant-xxx.onrender.com
https://email-assistant-xxx.onrender.com/auth/callback
```

---

## 🎯 **If You Get Stuck**

Most common issues:

**"Redirect URI mismatch"**
- Make sure you added BOTH:
  - `http://localhost:5000/auth/callback` (local)
  - `https://...onrender.com/auth/callback` (production)

**"Gmail API not found"**
- Search bar at top → `gmail api` → click first result

**"OAuth not enabled"**
- Left sidebar → APIs & Services → check Gmail API is enabled

**"Can't find credentials"**
- Go to Credentials page → find "EmailAssistant Web" OAuth credential → click it

---

## ⏱️ **Total Time: 15 minutes**

- Google Cloud setup: 10 min
- Download: 1 min
- Add to project: 2 min
- Test: 2 min

**Then deploy = 5 more minutes on Render!**

---

**Follow EXACTLY and you'll be done!** 🚀

Got stuck? Tell me exactly which step and I'll help!

---

**Ready? Start from Step 1!** ✅
