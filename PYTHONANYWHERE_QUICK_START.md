# PythonAnywhere Deployment - Quick Checklist

## Phase 1: Local Preparation (DO THIS FIRST)
- [ ] Copy `.env.example` to `.env`
- [ ] Update `.env` with your settings:
  - [ ] Generate a strong `SECRET_KEY` (e.g., `python -c "import secrets; print(secrets.token_hex(32))"`)
  - [ ] Update database path if needed
  - [ ] Configure email settings (optional)
- [ ] Test locally:
  ```bash
  .venv-1\Scripts\Activate.ps1
  pip install -r requirements.txt
  python init_db.py
  python backend/run.py
  ```
- [ ] Verify all routes work
- [ ] Test static files are served
- [ ] **DO NOT COMMIT .env FILE** - it's in `.gitignore`

## Phase 2: Upload to PythonAnywhere
- [ ] Option A (Recommended): Push to GitHub, then `git clone` on PythonAnywhere
  - [ ] `git init` locally
  - [ ] Create GitHub repository
  - [ ] `git add .` and `git commit -m "Initial commit"`
  - [ ] `git push` to GitHub
  - [ ] In PythonAnywhere Bash: `git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git`

- [ ] Option B: Manual upload via PythonAnywhere web interface

## Phase 3: PythonAnywhere Configuration

### Virtual Environment
```bash
cd /home/yourusername/devices_borrowing_system
mkvirtualenv --python=/usr/bin/python3.10 venv
workon venv
pip install -r requirements.txt
```

### Web App Setup (Web tab)
- [ ] Add new web app
- [ ] Manual configuration, Python 3.10
- [ ] **Virtualenv path:** `/home/yourusername/.virtualenvs/venv`
- [ ] **Source code:** `/home/yourusername/devices_borrowing_system`

### WSGI Configuration (Web tab)
- [ ] Edit WSGI configuration file
- [ ] Copy the recommended WSGI template from `DEPLOYMENT_PYTHONANYWHERE.md`
- [ ] Replace `yourusername` with your actual username
- [ ] Save

### Static Files (Web tab)
- [ ] Add static mapping:
  - URL: `/static/`
  - Directory: `/home/yourusername/devices_borrowing_system/backend/static`

### Environment Variables
Choose ONE method:

**Method 1: .env File (Recommended)**
```bash
cd /home/yourusername/devices_borrowing_system
nano .env
# Paste your environment variables
# Save: Ctrl+X, Y, Enter
```

**Method 2: Web Interface**
- [ ] Account → Web app settings
- [ ] Environment variables section
- [ ] Add each variable manually

## Phase 4: Test Deployment
- [ ] Click **Reload** button in Web tab
- [ ] Visit `https://yourusername.pythonanywhere.com`
- [ ] Test main page loads
- [ ] Test borrow/return functionality
- [ ] Check logs for errors:
  - Web tab → Log files section → error.log

## Phase 5: Troubleshooting (If Issues)

### 404 or Page Not Found
```bash
# SSH into PythonAnywhere and check:
ls -la /home/yourusername/devices_borrowing_system/
ls -la /home/yourusername/devices_borrowing_system/backend/templates/
```

### Module Import Errors
- [ ] Verify virtual environment is selected in Web tab
- [ ] Check WSGI file has correct path
- [ ] Reload web app

### Static Files Not Loading
- [ ] Verify path is absolute: `/home/.../backend/static`
- [ ] Check files actually exist in that directory
- [ ] Reload web app

### Database Errors
```bash
cd /home/yourusername/devices_borrowing_system
mkdir -p instance
python -c "from backend.init_db import init_db; from backend import app; \
  app.app_context().push(); init_db(); print('Database initialized')"
```

### Still Have Issues?
1. Check `error.log` in Web tab → Log files
2. Check server/error console output
3. Verify all paths use absolute paths, not relative
4. See full guide: `DEPLOYMENT_PYTHONANYWHERE.md`

## Phase 6: Ongoing Maintenance

### Update Code
```bash
cd /home/yourusername/devices_borrowing_system
git pull origin main
# Then Reload in Web tab
```

### Update Dependencies
```bash
workon venv
pip install --upgrade -r requirements.txt
# Then Reload in Web tab
```

### Monitor Errors
- [ ] Check error.log regularly
- [ ] Subscribe to error emails in Account settings

### Backup Database
```bash
cd /home/yourusername/devices_borrowing_system/instance
cp laptops.db laptops_backup_$(date +%Y%m%d).db
```

---

## Useful Commands

### Check Python Version
```bash
python --version
```

### Check Installed Packages
```bash
workon venv
pip list
```

### Run Database Initialization
```bash
cd /home/yourusername/devices_borrowing_system
python init_db.py
```

### View Application Logs
```bash
tail -f /home/yourusername/devices_borrowing_system/logs/app.log
```

### Restart Web App
```
Go to Web tab → Click "Reload" button
```

---

**✅ Your app is deployed!** Start with Phase 1 local prep, then follow Phase 2-4.
