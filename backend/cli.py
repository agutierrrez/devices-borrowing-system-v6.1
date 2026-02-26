"""Small CLI helpers: seed-db and backup-db."""
import os
import shutil
from backend.init_db import init_db
from backend import app


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


if __name__ == '__main__':
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    if cmd == 'seed-db':
        seed_db()
    elif cmd == 'backup-db':
        out = backup_db()
        if out:
            print('Backup created at', out)
    else:
        print('Usage: python -m backend.cli seed-db|backup-db')
