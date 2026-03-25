import sys
import os
from pathlib import Path

# Add the current directory to the path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Load environment variables from .env file if it exists
from dotenv import load_dotenv
env_path = os.path.join(project_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Ensure instance directory exists
instance_dir = os.path.join(project_dir, 'instance')
os.makedirs(instance_dir, exist_ok=True)

# Import the Flask app
from backend import app as application

# Ensure database is initialized on first run
if not os.path.exists(os.path.join(instance_dir, 'laptops.db')):
    try:
        from backend.init_db import init_db
        with application.app_context():
            init_db()
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")