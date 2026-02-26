from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import timezone, timedelta

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/laptops.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
# When True, borrowers must provide an email to borrow; default True
app.config['REQUIRE_BORROWER_EMAIL'] = os.environ.get('REQUIRE_BORROWER_EMAIL', '1') == '1'

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

from backend import routes, models
