"""Small CLI helpers: seed-db, backup-db, and admin management."""
import os
import shutil
from backend.init_db import init_db
from backend import app, db
from backend.models import User


def seed_db():
    """Call the existing init_db seeder."""
    init_db()


def backup_db(dest_dir='backups'):
    os.makedirs(dest_dir, exist_ok=True)
    db_url = os.environ.get('DATABASE_URL') or app.config.get('SQLALCHEMY_DATABASE_URI')
    # only support sqlite:///. paths for backup convenience
    if db_url.startswith('sqlite:///'):
        path = db_url.replace('sqlite:///', '')
        if os.path.exists(path):
            dst = os.path.join(dest_dir, os.path.basename(path) + '.bak')
            shutil.copy2(path, dst)
            print('Backed up', path, '->', dst)
            return dst
        else:
            print('DB file not found:', path)
            return None
    else:
        print('Backup only supported for sqlite DBs in this helper')
        return None


def create_admin(username, password):
    """Create a new admin user."""
    with app.app_context():
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f'Admin user "{username}" already exists.')
            return False
        
        user = User(username=username, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f'Admin user "{username}" created successfully.')
        return True


def reset_admin_password(username, password):
    """Reset password for an existing admin user."""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f'Admin user "{username}" not found.')
            return False
        
        if not user.is_admin:
            print(f'User "{username}" is not an admin.')
            return False
        
        user.set_password(password)
        db.session.commit()
        print(f'Password reset successfully for admin user "{username}".')
        return True


if __name__ == '__main__':
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    if cmd == 'seed-db':
        seed_db()
    elif cmd == 'backup-db':
        out = backup_db()
        if out:
            print('Backup created at', out)
    elif cmd == 'create-admin':
        if len(sys.argv) < 4:
            print('Usage: python -m backend.cli create-admin <username> <password>')
        else:
            create_admin(sys.argv[2], sys.argv[3])
    elif cmd == 'reset-admin-password':
        if len(sys.argv) < 4:
            print('Usage: python -m backend.cli reset-admin-password <username> <password>')
        else:
            reset_admin_password(sys.argv[2], sys.argv[3])
    else:
        print('Usage: python -m backend.cli seed-db|backup-db|create-admin|reset-admin-password')
