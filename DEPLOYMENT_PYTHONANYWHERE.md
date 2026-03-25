# Devices Borrowing System - PythonAnywhere Deployment Guide

## Prerequisites
- A PythonAnywhere account (free or paid tier)
- Your Flask application code
- All files in the project directory

## Step 1: Prepare Your Local Project

### 1.1 Update Environment Configuration
Create a `.env` file in the project root:

```bash
# .env file (DO NOT commit this to git)
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-secure-secret-key-here
DATABASE_URL=sqlite:////home/yourusername/devices_borrowing_system/instance/laptops.db
REQUIRE_BORROWER_EMAIL=1

# Email Configuration (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
```

### 1.2 Verify requirements.txt
Ensure all dependencies are listed with pinned versions:
```bash
pip list  # Check what packages you have installed
pip freeze > requirements.txt  # Generate exact versions
```

### 1.3 Test Locally
```bash
# Activate your virtual environment
.venv-1\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run the app
python backend/run.py
```

---

## Step 2: Upload Code to PythonAnywhere

### Option A: Using Git (Recommended)

1. **Create a GitHub repository** (if not already done)
   ```bash
   git init
   git add .
   git commit -m "Initial commit for PythonAnywhere deployment"
   git remote add origin https://github.com/yourusername/devices-borrowing.git
   git push -u origin main
   ```

2. **In PythonAnywhere Console:**
   ```bash
   cd /home/yourusername
   git clone https://github.com/yourusername/devices-borrowing.git
   cd devices-borrowing
   ```

### Option B: Manual Upload

1. Go to [PythonAnywhere Files Tab](https://www.pythonanywhere.com/user/username/files/home/)
2. Create folder: `/home/yourusername/devices_borrowing_system`
3. Upload all your project files using the web interface
4. Keep the `.env` file locally and configure it on PythonAnywhere (see Step 3)

---

## Step 3: Set Up Virtual Environment on PythonAnywhere

1. **Open PythonAnywhere Bash Console:**
   ```bash
   cd /home/yourusername/devices_borrowing_system
   
   # Create virtual environment (use Python 3.10 or higher)
   mkvirtualenv --python=/usr/bin/python3.10 venv
   
   # Activate and install requirements
   workon venv
   pip install -r requirements.txt
   ```

2. **Verify installation:**
   ```bash
   python -c "import flask; print(flask.__version__)"
   ```

---

## Step 4: Configure Web App in PythonAnywhere

### 4.1 Create a New Web App
1. Go to **Web** tab → **Add a new web app**
2. Choose **Manual configuration**
3. Select **Python 3.10** (or your preferred version)

### 4.2 Configure WSGI File
1. Navigate to **Web** tab → Look for "WSGI configuration file"
2. Edit the WSGI file (usually `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
3. Replace its content with:

```python
import sys
import os
from pathlib import Path

# Add the project directory to the path
project_home = '/home/yourusername/devices_borrowing_system'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Set environment variables at the application level
os.chdir(project_home)

# Ensure instance directory exists
instance_dir = os.path.join(project_home, 'instance')
os.makedirs(instance_dir, exist_ok=True)

# Import and run the Flask app
from backend import app as application

# Initialize database if it doesn't exist
if not os.path.exists(os.path.join(instance_dir, 'laptops.db')):
    try:
        from backend.init_db import init_db
        with application.app_context():
            init_db()
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
```

**Replace `yourusername` with your actual PythonAnywhere username.**

### 4.3 Configure Virtual Environment
In the **Web** tab:
- Set "Virtualenv": `/home/yourusername/.virtualenvs/venv`
- Or click the link and select the virtual environment you created

### 4.4 Configure Source Code
In the **Web** tab:
- Set "Source code": `/home/yourusername/devices_borrowing_system`

---

## Step 5: Set Environment Variables

### Option A: Using .env File (Recommended for development)
1. In **Bash Console**, navigate to your project:
   ```bash
   cd /home/yourusername/devices_borrowing_system
   nano .env
   ```

2. Add your environment variables:
   ```
   FLASK_ENV=production
   FLASK_DEBUG=0
   SECRET_KEY=your-very-secure-random-string
   REQUIRE_BORROWER_EMAIL=1
   ```

3. Save and exit (Ctrl+X, then Y, then Enter)

### Option B: Using PythonAnywhere Web Interface (Alternative)
1. Go to **Account** → **Web app** → Click your app
2. Scroll to **Environment variables**
3. Add each variable as a separate entry

### Option C: Hardcode in WSGI (Last Resort)
Add to your WSGI file before importing the app:
```python
os.environ['SECRET_KEY'] = 'your-secret-key'
os.environ['FLASK_ENV'] = 'production'
# etc.
```

---

## Step 6: Configure Static Files

In the **Web** tab, add static file mappings:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/devices_borrowing_system/backend/static` |

Example entries:
- URL: `/static/`
- Directory: `/home/yourusername/devices_borrowing_system/backend/static`

---

## Step 7: Configure Logging (Optional but Recommended)

1. Create a logs directory:
   ```bash
   mkdir -p /home/yourusername/devices_borrowing_system/logs
   ```

2. Update your WSGI file to log errors:
   ```python
   import logging
   
   logging.basicConfig(
       filename='/home/yourusername/devices_borrowing_system/logs/app.log',
       level=logging.ERROR,
       format='%(asctime)s %(levelname)s: %(message)s'
   )
   ```

---

## Step 8: Reload and Test

1. In **Web** tab, click **Reload** (green button at the top)
2. Visit your web app URL: `https://yourusername.pythonanywhere.com`
3. Check the error logs if issues arise:
   - **Web** tab → **Log files** area
   - View "error.log" or "server.log"

---

## Troubleshooting

### Database Connection Error
**Error:** `unable to open database file`

**Solution:**
```bash
# Check database path is absolute
echo $DATABASE_URL

# Create instance directory manually
mkdir -p /home/yourusername/devices_borrowing_system/instance

# Reinitialize database
cd /home/yourusername/devices_borrowing_system
python -c "from backend.init_db import init_db; from backend import app; app.app_context().push(); init_db()"
```

### Module Not Found
**Error:** `ModuleNotFoundError: No module named 'backend'`

**Solution:**
- Check WSGI file has correct `sys.path.insert(0, project_home)`
- Verify virtual environment is activated in WSGI configuration
- Reload web app

### Static Files Not Loading
**Error:** CSS/images not displaying

**Solution:**
- Verify static file mapping in **Web** tab
- Check path is absolute: `/home/yourusername/devices_borrowing_system/backend/static`
- Reload web app

### Import Errors
**Error:** `ImportError: cannot import name 'app' from 'backend'`

**Solution:**
- Ensure `backend/__init__.py` exports `app`
- Check project directory structure matches local
- Reload web app

### 404 on Routes
**Error:** Routes return 404

**Solution:**
- Verify templates are in `/home/yourusername/devices_borrowing_system/backend/templates/`
- Check WSGI file sets correct working directory: `os.chdir(project_home)`
- Reload web app

---

## Daily Operations

### Updating Code
After git push to your repository:
```bash
cd /home/yourusername/devices_borrowing_system
git pull origin main
```

Then reload in PythonAnywhere **Web** tab.

### Updating Dependencies
```bash
workon venv
pip install -r requirements.txt
```

Then reload web app.

### View Logs
- **Web** tab → **Log files** section
- Check `error.log` for Python errors
- Check `server.log` for HTTP requests

---

## Security Checklist

- [ ] Change `SECRET_KEY` to a random, secure string
- [ ] Set `FLASK_DEBUG=0` in production
- [ ] Use environment variables for all secrets (no hardcoding)
- [ ] Ensure `.env` file is NOT in git repository
- [ ] Add `.env` to `.gitignore`:
  ```
  .env
  instance/laptops.db
  __pycache__/
  .venv*/
  ```
- [ ] Use HTTPS (PythonAnywhere provides this by default)
- [ ] Regularly update Flask and dependencies

---

## Database Backup

### Manual Backup (Bash Console)
```bash
cp /home/yourusername/devices_borrowing_system/instance/laptops.db \
   /home/yourusername/devices_borrowing_system/backups/laptops_$(date +%Y%m%d_%H%M%S).db
```

### Automated Daily Backup (Optional)
Add a task in **Tasks** tab to run:
```bash
/home/yourusername/.virtualenvs/venv/bin/python -c \
  "import shutil; from datetime import datetime; \
  shutil.copy('/home/yourusername/devices_borrowing_system/instance/laptops.db', \
  f'/home/yourusername/devices_borrowing_system/backups/laptops_{datetime.now():%Y%m%d_%H%M%S}.db')"
```

---

## Support & Resources

- [PythonAnywhere Official Help](https://www.pythonanywhere.com/help/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

## Checklist for Deployment

- [ ] Create `.env` file with all required variables
- [ ] Test app locally
- [ ] Upload code to PythonAnywhere (git clone or manual)
- [ ] Create virtual environment
- [ ] Install dependencies from `requirements.txt`
- [ ] Configure WSGI file
- [ ] Set virtual environment path in Web tab
- [ ] Set source code path in Web tab
- [ ] Configure static files mapping
- [ ] Set environment variables
- [ ] Reload web app
- [ ] Test by visiting your URL
- [ ] Check logs for errors
- [ ] Verify database is created
- [ ] Verify static files load
- [ ] Update DNS/domain if needed

---

**You're all set! 🚀 Your Devices Borrowing System is now live on PythonAnywhere!**
