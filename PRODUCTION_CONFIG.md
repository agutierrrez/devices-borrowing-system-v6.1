# Production Configuration Guide for PythonAnywhere

## 1. Generate a Secure SECRET_KEY

You need a strong, random `SECRET_KEY` for production. Generate one using Python:

### Method 1: Quick Python Command
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Output example:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### Method 2: Using secrets module (more secure)
```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(secret_key)
```

### Method 3: Using os.urandom
```python
import os
import binascii
secret_key = binascii.hexlify(os.urandom(32)).decode()
print(secret_key)
```

**Copy the generated key and save it to your `.env` file as `SECRET_KEY`**

---

## 2. Environment Variables Setup

### Required Variables
```env
# Production environment flag
FLASK_ENV=production
FLASK_DEBUG=0

# Security - MUST CHANGE THIS!
SECRET_KEY=your-generated-secure-key-from-above

# Email requirement for borrowers
REQUIRE_BORROWER_EMAIL=1
```

### Optional Variables
```env
# Database path (leave empty to use default SQLite)
# DATABASE_URL=sqlite:////home/yourusername/devices_borrowing_system/instance/laptops.db

# Email configuration (only if sending emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
```

---

## 3. Setting Environment Variables on PythonAnywhere

### Option A: Using .env File (Recommended)

1. **Create .env file in your project root:**
   ```bash
   cd /home/yourusername/devices_borrowing_system
   nano .env
   ```

2. **Paste your environment variables:**
   ```
   FLASK_ENV=production
   FLASK_DEBUG=0
   SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
   REQUIRE_BORROWER_EMAIL=1
   ```

3. **Save the file:**
   - Press `Ctrl+X`
   - Press `Y` (yes)
   - Press `Enter`

4. **Verify it was created:**
   ```bash
   cat .env
   ```

**✅ DO NOT commit this file to git! It's in `.gitignore`**

### Option B: Using PythonAnywhere Web Interface

1. Go to **Account** → **Web app** (or **Web**)
2. Click on your app name
3. Scroll to **Environment variables**
4. Click **Add a new variable**
5. Enter each variable:
   - **Variable:** `FLASK_ENV`
   - **Value:** `production`
   - Click **Add**
6. Repeat for each variable

### Option C: Hardcoding (Last Resort, Not Recommended)

If neither option above works, add to your WSGI file after the `sys.path` setup:

```python
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'
os.environ['SECRET_KEY'] = 'your-secret-key'
os.environ['REQUIRE_BORROWER_EMAIL'] = '1'
```

---

## 4. Database Configuration

### Default SQLite Setup (Simplest)
If you don't set `DATABASE_URL`, the app will use:
```
/home/yourusername/devices_borrowing_system/instance/laptops.db
```

The app automatically creates the `instance` directory if it doesn't exist.

### Custom SQLite Path
To use a different database path:
```env
DATABASE_URL=sqlite:////home/yourusername/custom_path/laptops.db
```

**Important:** The path must be absolute (start with `/`) and use forward slashes, even on Windows.

### MySQL Database (Advanced)
If you want to use MySQL instead:
1. First, set up a database on PythonAnywhere
2. Install MySQL driver:
   ```bash
   workon venv
   pip install pymysql
   ```
3. Set DATABASE_URL:
   ```env
   DATABASE_URL=mysql+pymysql://username:password@yourserver.pythonanywhere-services.com/databasename
   ```

---

## 5. Email Configuration (Optional)

### Using Gmail
1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Go to **App passwords**
   - Select **Mail** and **Windows Computer**
   - Google will generate a 16-character password

3. **Add to .env:**
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
   SMTP_FROM=your-email@gmail.com
   ```

### Using Other Email Providers
Update the SMTP settings accordingly:

**Office 365 / Outlook:**
```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
```

**SendGrid:**
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.your-sendgrid-api-key
```

---

## 6. Verify Configuration

### Check Environment Variables are Loaded

Add this to your app temporarily (in `backend/__init__.py` or WSGI file):

```python
import os
print("FLASK_ENV:", os.environ.get('FLASK_ENV'))
print("SECRET_KEY set:", bool(os.environ.get('SECRET_KEY')))
print("DATABASE_URL:", os.environ.get('DATABASE_URL', 'using default'))
```

Then check the error.log after reloading the web app.

### Verify Database Path

```bash
cd /home/yourusername/devices_borrowing_system
python -c "from backend import app; print('Database URI:', app.config['SQLALCHEMY_DATABASE_URI'])"
```

---

## 7. Security Best Practices

- ✅ **Always use a strong, random SECRET_KEY** in production
- ✅ **Never commit .env to git** (use .env.example instead)
- ✅ **Never hardcode secrets** in Python files
- ✅ **Use environment variables** for all sensitive configuration
- ✅ **Set FLASK_DEBUG=0** in production
- ✅ **Set FLASK_ENV=production** in production
- ✅ **Use HTTPS** (PythonAnywhere provides this automatically)
- ✅ **Regularly update** Flask and dependencies
- ✅ **Monitor error logs** for security issues

---

## 8. Troubleshooting

### SECRET_KEY Warning
**If you see:** `Application failed to start: KeyError: SECRET_KEY`

**Fix:**
- Set `SECRET_KEY` in `.env` or environment variables
- Reload web app

### DATABASE_URL Error
**If you see:** `unable to open database file`

**Fix:**
```bash
# Verify .env is loading
cat /home/yourusername/devices_borrowing_system/.env

# Check path is absolute
python -c "import os; print(os.path.exists('/home/yourusername/devices_borrowing_system/instance'))"

# Create instance directory
mkdir -p /home/yourusername/devices_borrowing_system/instance

# Reload web app
```

### Environment Variables Not Loading
**If environment variables aren't being read:**

1. Verify `.env` file is in the correct directory (project root)
2. Check WSGI file has `load_dotenv()` call
3. Try using PythonAnywhere web interface to set variables instead
4. Reload web app

---

## 9. Updating Configuration

### After Changing .env
```bash
# No need to reload manually - changes take effect on next request
# But if it doesn't work, explicitly reload:
# Go to Web tab → Click "Reload"
```

### After Changing Environment Variables (Web Interface)
- Changes take effect immediately
- If not, reload the web app

### After Changing Settings
Always **Reload** the web app from the **Web** tab!

---

## 10. Reference

See also:
- Main deployment guide: `DEPLOYMENT_PYTHONANYWHERE.md`
- Quick start checklist: `PYTHONANYWHERE_QUICK_START.md`
- Flask Configuration: https://flask.palletsprojects.com/config/
- Python-dotenv: https://python-dotenv.readthedocs.io/

---

**Your application is now configured for production! 🚀**
