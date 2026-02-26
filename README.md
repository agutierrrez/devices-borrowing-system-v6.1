# Devices Borrowing System (Flask + SQLite)


Minimal web app to borrow/return laptops. Initializes with 10 laptops named `byol1`..`byol10`.

Project layout

- `backend/` — Flask application package (`backend/run.py`, `backend/__init__.py`, `backend/models.py`, `backend/routes.py`, `backend/init_db.py`).
- `tests/` — pytest test suite (`tests/test_app.py`).
- `.github/workflows/ci.yml` — GitHub Actions workflow to run tests on push/PR.

Setup (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
python -m backend.run
```

Run tests locally:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
```

CI

The repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` that installs dependencies and runs `pytest` on push and pull requests.

Notes
- The app uses SQLite by default (`laptops.db`) and a simple `Laptop` model in `backend/models.py`.
- To change DB path, set `DATABASE_URL` environment variable.

Overdue report (mock email or real SMTP)

You can generate an overdue report which prints overdue items and writes a report file. By default the script prints the intended email content; enable SMTP to send real emails.

```powershell
# generate report without sending emails
python -m backend.overdue_report

# enable sending emails (configure SMTP environment variables first)
$env:OVERDUE_SEND_EMAILS = '1'
$env:SMTP_HOST = 'smtp.example.com'
$env:SMTP_PORT = '587'
$env:SMTP_USER = 'user@example.com'
$env:SMTP_PASS = 'smtppassword'
$env:SMTP_FROM = 'noreply@example.com'
python -m backend.overdue_report
```

Environment variables used for SMTP (optional):

- `SMTP_HOST` — SMTP server host (required to actually send)
- `SMTP_PORT` — SMTP server port (default 587)
- `SMTP_USER` — SMTP username
- `SMTP_PASS` — SMTP password
- `SMTP_FROM` — From address (defaults to `SMTP_USER`)
- `OVERDUE_SEND_EMAILS` — set to `1`/`true` to enable email sends

If SMTP vars are not configured, the script will print the message that would have been sent (mock send).

