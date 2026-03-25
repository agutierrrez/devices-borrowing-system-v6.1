# PythonAnywhere Deployment Documentation

This folder contains comprehensive guides for deploying your Devices Borrowing System to PythonAnywhere. Use the documents below based on your needs.

## 📚 Documentation Files

### 🚀 **START HERE: `PYTHONANYWHERE_QUICK_START.md`**
**Use this for a fast, checklist-based deployment path**
- ⏱️ Estimated time: 30-45 minutes
- ✅ Step-by-step checklist format
- 📋 Follow Phase 1 → Phase 2 → Phase 3 → etc.
- 🆘 Includes quick troubleshooting commands
- **Best for:** Getting your app live quickly

### 📖 **`DEPLOYMENT_PYTHONANYWHERE.md`**
**Complete reference guide with detailed explanations**
- 📚 Comprehensive step-by-step instructions
- 🔍 Detailed explanations for each step
- 🆘 Extensive troubleshooting section
- 🔒 Security best practices
- 📊 Configuration examples
- **Best for:** Understanding every aspect of deployment

### ⚙️ **`PRODUCTION_CONFIG.md`**
**Configuration and secrets management guide**
- 🔑 How to generate a secure SECRET_KEY
- 🔒 Environment variables setup (3 methods)
- 📧 Email configuration (Gmail, Office 365, SendGrid)
- 🗄️ Database configuration (SQLite, MySQL)
- 🆘 Verification and troubleshooting
- **Best for:** Understanding and configuring your settings

### 📋 **`DEPLOYMENT_SUMMARY.md`**
**Overview and quick reference**
- ✅ What was configured for you
- 🚀 Quick start (5 steps)
- 📋 Comprehensive checklist
- 🔒 Security reminders
- 📁 File modifications summary
- **Best for:** Quick overview and navigation

### ℹ️ **`README_DEPLOYMENT.md`** (this file)
**Navigation guide for all deployment documentation**

---

## 🎯 Quick Navigation by Goal

### "I want to deploy ASAP!"
1. Read: `PYTHONANYWHERE_QUICK_START.md` (Phase 1)
2. Follow the checklist through all phases
3. If you hit an error, check that document's troubleshooting section

### "I want to understand everything first"
1. Read: `DEPLOYMENT_SUMMARY.md` (overview)
2. Then: `DEPLOYMENT_PYTHONANYWHERE.md` (detailed)
3. Then: `PRODUCTION_CONFIG.md` (for config questions)

### "I need help with configuration"
👉 **`PRODUCTION_CONFIG.md`**
- Generating SECRET_KEY
- Setting environment variables
- Configuring email
- Configuring database

### "I need help with a specific error"
👉 **`DEPLOYMENT_PYTHONANYWHERE.md` → Troubleshooting section**
- Database Connection Error
- Module Not Found
- Static Files Not Loading
- Import Errors
- 404 on Routes

### "I want to understand what was changed"
👉 **`DEPLOYMENT_SUMMARY.md` → "What Has Been Configured" section**
- Shows all files modified
- Shows all files created
- Explains what each change does

---

## ✨ What Was Done For You

### Code Updated
- ✅ `requirements.txt` - Pinned versions for all dependencies
- ✅ `wsgi.py` - Enhanced for PythonAnywhere compatibility
- ✅ `backend/__init__.py` - Production configuration
- ✅ `.gitignore` - Added `.env` file (prevent secret leaks)

### New Files Created
- ✅ `.env.example` - Template for configuration
- ✅ `PYTHONANYWHERE_QUICK_START.md` - Quick deployment checklist
- ✅ `DEPLOYMENT_PYTHONANYWHERE.md` - Detailed deployment guide
- ✅ `PRODUCTION_CONFIG.md` - Configuration guide
- ✅ `DEPLOYMENT_SUMMARY.md` - Overview and summary
- ✅ `README_DEPLOYMENT.md` - This file

---

## 🔄 Deployment Workflow

```
1. Local Preparation
   ↓
2. Create .env file
   ↓
3. Test locally
   ↓
4. Upload to GitHub
   ↓
5. Clone on PythonAnywhere
   ↓
6. Create virtual environment
   ↓
7. Install dependencies
   ↓
8. Configure WSGI
   ↓
9. Set environment variables
   ↓
10. Reload app
    ↓
11. Test on live URL
    ↓
12. Monitor logs
```

👉 **See `PYTHONANYWHERE_QUICK_START.md` for the actual steps**

---

## 📋 Key Concepts

### Environment Variables (`.env`)
Configuration values like `SECRET_KEY`, database path, email settings, etc.
- **Why?** Secrets stay out of code and git
- **Where?** In `.env` file (not committed to git)
- **How?** Copy `.env.example` → `.env` → Fill in values
- **Read more:** `PRODUCTION_CONFIG.md` → Section 3

### WSGI File
The web server gateway interface - tells PythonAnywhere how to run your Flask app
- **Why?** PythonAnywhere needs this to start your app
- **Where?** Configured in PythonAnywhere Web tab
- **How?** Copy template from `DEPLOYMENT_PYTHONANYWHERE.md` → Step 4
- **Read more:** `DEPLOYMENT_PYTHONANYWHERE.md` → Step 4.2

### Virtual Environment
Isolated Python installation just for your app
- **Why?** Prevents dependency conflicts
- **Where?** `/home/yourusername/.virtualenvs/venv`
- **How?** `mkvirtualenv --python=/usr/bin/python3.10 venv`
- **Read more:** `PYTHONANYWHERE_QUICK_START.md` → Phase 3

### Static Files
CSS, images, JavaScript - served directly by web server
- **Why?** Faster delivery, not processed by Flask
- **Where?** `backend/static/` in your project
- **How?** Configure in Web tab → Static files section
- **Read more:** `DEPLOYMENT_PYTHONANYWHERE.md` → Step 6

---

## 🆘 I Have An Error!

### Step 1: Find Your Error
- Check PythonAnywhere **Web tab** → **Log files** → **error.log**
- Copy the error message

### Step 2: Look It Up
- Search in `DEPLOYMENT_PYTHONANYWHERE.md` → **Troubleshooting section**
- Common errors listed with solutions

### Step 3: If Not Found
- Check `PRODUCTION_CONFIG.md` → **Section 8: Troubleshooting**
- Check error message matches your situation
- Follow suggested fix
- Reload web app

### Step 4: Still Stuck?
- Verify WSGI configuration matches the template
- Verify paths are correct and absolute
- Check `.env` file is in the right location
- Make sure virtual environment is selected

---

## ✅ Pre-Deployment Checklist

### Must Do
- [ ] Create `.env` file from `.env.example`
- [ ] Generate a secure `SECRET_KEY`
- [ ] Test the app locally
- [ ] Push code to GitHub (or prepare manual upload)

### Should Do
- [ ] Read at least `PYTHONANYWHERE_QUICK_START.md`
- [ ] Understand environment variables
- [ ] Have your PythonAnywhere account ready

### Nice to Have
- [ ] Read full `DEPLOYMENT_PYTHONANYWHERE.md`
- [ ] Set up email configuration
- [ ] Plan backup strategy for database

---

## 🚀 Let's Go!

**Ready to deploy?**

1. **Fast path:** Start with `PYTHONANYWHERE_QUICK_START.md`
2. **Detailed path:** Start with `DEPLOYMENT_SUMMARY.md`, then `DEPLOYMENT_PYTHONANYWHERE.md`
3. **Config help needed:** Jump to `PRODUCTION_CONFIG.md`

---

## 📝 Document Summary Table

| Document | Length | Audience | Use When |
|----------|--------|----------|----------|
| `PYTHONANYWHERE_QUICK_START.md` | Medium | Everyone | Ready to deploy quickly |
| `DEPLOYMENT_PYTHONANYWHERE.md` | Long | Detailed learners | Want full understanding |
| `PRODUCTION_CONFIG.md` | Medium | Config questions | Need to understand secrets |
| `DEPLOYMENT_SUMMARY.md` | Short | Quick reference | Need overview |
| `README_DEPLOYMENT.md` | Medium | Navigation | This file |

---

## 🔗 External Resources

- [PythonAnywhere Help](https://www.pythonanywhere.com/help/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python-dotenv Docs](https://python-dotenv.readthedocs.io/)

---

## 💬 Questions?

**Common questions answered in:**
- "How do I set up environment variables?" → `PRODUCTION_CONFIG.md` Section 3
- "What's the WSGI file?" → `DEPLOYMENT_PYTHONANYWHERE.md` Step 4
- "How do I generate a SECRET_KEY?" → `PRODUCTION_CONFIG.md` Section 1
- "What's that error message?" → `DEPLOYMENT_PYTHONANYWHERE.md` Troubleshooting
- "What was changed in my code?" → `DEPLOYMENT_SUMMARY.md` Section 2

---

**Good luck with your deployment! 🎉**

Feel free to reference these documents at any time during or after deployment.
