from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import timezone, timedelta

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configure database - support both relative (dev) and absolute (production) paths
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    # Use absolute path to avoid issues with different working directories
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_path = os.path.join(instance_path, 'laptops.db')
    db_url = f'sqlite:///{db_path.replace(chr(92), "/")}'  # Handle Windows paths

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
# When True, borrowers must provide an email to borrow; default True
app.config['REQUIRE_BORROWER_EMAIL'] = os.environ.get('REQUIRE_BORROWER_EMAIL', '1') == '1'
# Production configuration
app.config['ENV'] = os.environ.get('FLASK_ENV', 'development')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', '0') == '1'

# Peru / Lima timezone helper used across the package
try:
	from zoneinfo import ZoneInfo
	try:
		LIMA = ZoneInfo('America/Lima')
	except Exception:
		LIMA = timezone(timedelta(hours=-5))
except Exception:
	# Fall back to fixed offset if zoneinfo not available
	LIMA = timezone(timedelta(hours=-5))

db = SQLAlchemy(app)

from . import routes, models
