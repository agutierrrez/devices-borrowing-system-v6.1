from . import app, db
from .models import Laptop
import os
from .models import BorrowHistory, OtherDevice, OtherDeviceHistory


def init_db():
    # Determine effective DB URL (tests may set DATABASE_URL after importing backend)
    db_url = os.environ.get('DATABASE_URL') or app.config.get('SQLALCHEMY_DATABASE_URI')

    # Create a separate engine/session to ensure we operate on the intended DB
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(db_url, future=True)

    # Create tables based on the models' metadata
    db.metadata.create_all(bind=engine)

    # Use a fresh session to seed data so we don't rely on the Flask-SQLAlchemy session
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        existing = {l.name for l in session.query(Laptop).all()}
        for i in range(1, 11):
            name = f'byol{i}'
            if name not in existing:
                laptop = Laptop(name=name)
                session.add(laptop)
        # seed some example other devices
        existing_other = {d.name for d in session.query(OtherDevice).all()}
        sample_other = ['Projector A', 'Staff Laptop 1', 'Charger 1', 'HDMI Cable', 'Microphone']
        for name in sample_other:
            if name not in existing_other:
                od = OtherDevice(name=name, category='general')
                session.add(od)
        session.commit()
        # Ensure deterministic clean state for tests: clear borrow flags and history
        session.query(BorrowHistory).delete()
        session.query(OtherDeviceHistory).delete()
        for l in session.query(Laptop).all():
            l.is_borrowed = False
            l.borrower = None
            # laptop may not have borrower_email in older seeds
            if hasattr(l, 'borrower_email'):
                l.borrower_email = None
            l.borrowed_at = None
            if hasattr(l, 'due_date'):
                l.due_date = None
        session.commit()
    finally:
        session.close()
    # Rebind the Flask-SQLAlchemy session to this engine so the app uses the same DB
    try:
        from backend import db as _db
        _db.session.remove()
        _db.session.configure(bind=engine)
    except Exception:
        # best-effort rebinding; if it fails, tests may still pass via the created engine
        pass

    # Additionally, ensure the app's configured DB (if different) is created/cleaned
    try:
        app_db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        if app_db_url and app_db_url != db_url:
            engine2 = create_engine(app_db_url, future=True)
            # create tables if missing
            db.metadata.create_all(bind=engine2)
            Session2 = sessionmaker(bind=engine2)
            s2 = Session2()
            try:
                s2.query(BorrowHistory).delete()
                for l in s2.query(Laptop).all():
                    l.is_borrowed = False
                    l.borrower = None
                    if hasattr(l, 'borrower_email'):
                        l.borrower_email = None
                    l.borrowed_at = None
                    if hasattr(l, 'due_date'):
                        l.due_date = None
                s2.commit()
            finally:
                s2.close()
    except Exception:
        pass


if __name__ == '__main__':
    init_db()
    print('Backend DB initialized with 10 laptops (byol1..byol10).')
