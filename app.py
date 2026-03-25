from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc
from datetime import datetime, timezone, timedelta
import math
try:
    from zoneinfo import ZoneInfo
    try:
        LIMA = ZoneInfo('America/Lima')
    except Exception:
        # tzdata not available in environment; fall back to fixed offset -05:00
        LIMA = timezone(timedelta(hours=-5))
except Exception:
    # older Python or zoneinfo unavailable; use fixed offset -05:00
    from datetime import timezone as _tz
    LIMA = _tz(timedelta(hours=-5))
import os

app = Flask(__name__, static_folder='backend/static', static_url_path='/static', template_folder='backend/templates')
# 1. Definimos la ruta base del proyecto de forma absoluta
basedir = os.path.abspath(os.path.dirname(__file__))

# 2. Definimos la ruta de la carpeta 'instance' y nos aseguramos de que exista
instance_path = os.path.join(basedir, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# 3. Definimos la ruta final del archivo de la base de datos
default_db_path = os.path.join(instance_path, 'laptops.db')

# 4. Configuramos la URI (el replace es por si vienes de Windows, en PythonAnywhere no estorba)
default_db_uri = f"sqlite:///{default_db_path.replace('\\', '/')}"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_db_uri)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')

db = SQLAlchemy(app)

# Peru / Lima timezone (LIMA is defined above)


class Laptop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    is_borrowed = db.Column(db.Boolean, default=False, nullable=False)
    borrower = db.Column(db.String(100), nullable=True)
    borrowed_at = db.Column(db.DateTime, nullable=True)
    borrower_email = db.Column(db.String(200), nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Laptop {self.name}>'


class BorrowHistory(db.Model):
    __tablename__ = 'borrow_history'
    id = db.Column(db.Integer, primary_key=True)
    laptop_id = db.Column(db.Integer, db.ForeignKey('laptop.id'), nullable=False)
    laptop = db.relationship('Laptop')
    borrower = db.Column(db.String(100), nullable=False)
    borrower_email = db.Column(db.String(200), nullable=True)
    borrowed_at = db.Column(db.DateTime, nullable=False)
    returned_at = db.Column(db.DateTime, nullable=True)
    observation = db.Column(db.Text, nullable=True)
    requested_days = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<BorrowHistory {self.laptop.name} by {self.borrower}>'


class OtherDevice(db.Model):
    __tablename__ = 'other_device'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    is_borrowed = db.Column(db.Boolean, default=False, nullable=False)
    borrower = db.Column(db.String(100), nullable=True)
    borrower_email = db.Column(db.String(200), nullable=True)
    borrowed_at = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<OtherDevice {self.name}>'


class OtherDeviceHistory(db.Model):
    __tablename__ = 'other_device_history'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('other_device.id'), nullable=False)
    device = db.relationship('OtherDevice')
    borrower = db.Column(db.String(100), nullable=False)
    borrower_email = db.Column(db.String(200), nullable=True)
    borrowed_at = db.Column(db.DateTime, nullable=False)
    returned_at = db.Column(db.DateTime, nullable=True)
    observation = db.Column(db.Text, nullable=True)
    requested_days = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<OtherDeviceHistory {self.device.name} by {self.borrower}>'

@app.template_filter('datetimeformat')
def datetimeformat(value):
    if not value:
        return '-'
    # If a datetime/date object is passed, format to YYYY-MM-DD
    try:
        from datetime import date
        if isinstance(value, (date,)):
            return value.isoformat()
    except Exception:
        pass
    # Fallback: handle ISO-like strings
    try:
        return value.split('T')[0]
    except Exception:
        return str(value)

@app.route('/')
def index():
    laptops = Laptop.query.order_by(Laptop.id).all()
    now = datetime.now(LIMA).replace(tzinfo=None)
    items = []
    for l in laptops:
        due = getattr(l, 'due_date', None)
        due_str = due.strftime('%Y-%m-%d') if due else None
        is_overdue = bool(l.is_borrowed and due and due < now)
        days_remaining = None
        days_text = None
        days_badge = None
        if l.is_borrowed and due:
            secs = (due - now).total_seconds()
            if secs > 0:
                days_remaining = math.ceil(secs / 86400)
            else:
                days_remaining = -math.ceil(abs(secs) / 86400)
            if days_remaining > 1:
                days_text = f"{days_remaining} days left"
                days_badge = 'orange'
            elif days_remaining == 1:
                days_text = '1 day left'
                days_badge = 'orange'
            elif days_remaining == 0:
                days_text = 'Due today'
                days_badge = 'orange'
            else:
                od = abs(days_remaining)
                days_text = 'Overdue by 1 day' if od == 1 else f'Overdue by {od} days'
                days_badge = 'red'
        items.append({
            'id': l.id,
            'name': l.name,
            'is_borrowed': l.is_borrowed,
            'borrower': l.borrower,
            'borrower_email': getattr(l, 'borrower_email', None),
            'due_date': due_str,
            'is_overdue': is_overdue,
            'days_remaining': days_remaining,
            'days_text': days_text,
            'days_badge': days_badge,
        })
    return render_template('index.html', items=items)


# history route removed to revert to pre-history-button state


@app.route('/borrow/<int:laptop_id>', methods=['GET', 'POST'])
def borrow(laptop_id):
    laptop = db.session.get(Laptop, laptop_id)
    if laptop is None:
        abort(404)
    if laptop.is_borrowed:
        flash('This laptop is already borrowed.', 'warning')
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        days = request.form.get('days', '').strip()
        if not name:
            flash('Please provide your name to borrow a laptop.', 'danger')
            return redirect(request.url)
        
        # Check if this borrower already has an active borrowed laptop
        existing_borrow = Laptop.query.filter_by(is_borrowed=True).filter(
            Laptop.borrower.ilike(f'%{name}%')
        ).first()
        if existing_borrow:
            flash(f'You already have {existing_borrow.name} borrowed. Please return it before borrowing another laptop.', 'warning')
            return redirect(request.url)
        
        laptop.is_borrowed = True
        laptop.borrower = name
        laptop.borrower_email = email or None
        # store naive local (Lima) time in DB for compatibility
        laptop.borrowed_at = datetime.now(LIMA).replace(tzinfo=None)
        try:
            requested_days = int(days) if days else 7
        except ValueError:
            flash('Invalid number of days; using default 7.', 'warning')
            requested_days = 7
        if requested_days < 0 or requested_days > 365:
            flash('Requested days must be between 0 and 365.', 'danger')
            return redirect(request.url)
        laptop.due_date = laptop.borrowed_at + timedelta(days=requested_days)
        db.session.commit()
        
        # Also create a BorrowHistory record for analytics
        history = BorrowHistory(
            laptop_id=laptop.id,
            borrower=name,
            borrower_email=email or None,
            borrowed_at=laptop.borrowed_at,
            returned_at=None,
            requested_days=requested_days
        )
        db.session.add(history)
        db.session.commit()
        
        flash(f'{laptop.name} borrowed by {name}.', 'success')
        return redirect(url_for('index'))
    return render_template('borrow.html', laptop=laptop)


@app.route('/return/<int:laptop_id>', methods=['POST'])
def return_laptop(laptop_id):
    laptop = db.session.get(Laptop, laptop_id)
    if laptop is None:
        abort(404)
    if not laptop.is_borrowed:
        flash('Laptop is not currently borrowed.', 'warning')
        return redirect(url_for('index'))
    
    # Update BorrowHistory to mark as returned
    active_history = BorrowHistory.query.filter_by(laptop_id=laptop.id).filter(
        BorrowHistory.returned_at.is_(None)
    ).order_by(BorrowHistory.id.desc()).first()
    
    if active_history:
        active_history.returned_at = datetime.now(LIMA).replace(tzinfo=None)
        db.session.add(active_history)
    
    laptop.is_borrowed = False
    laptop.borrower = None
    laptop.borrowed_at = None
    laptop.borrower_email = None
    laptop.due_date = None
    db.session.commit()
    flash(f'{laptop.name} has been returned.', 'success')
    return redirect(url_for('index'))


@app.route('/active-loans')
def active_loans():
    laptops = Laptop.query.filter_by(is_borrowed=True).order_by(Laptop.id).all()
    now = datetime.now(LIMA).replace(tzinfo=None)
    enriched = []
    for l in laptops:
        due = getattr(l, 'due_date', None)
        days_remaining = None
        days_text = None
        days_badge = None
        if due:
            secs = (due - now).total_seconds()
            if secs > 0:
                days_remaining = math.ceil(secs / 86400)
            else:
                days_remaining = -math.ceil(abs(secs) / 86400)
            if days_remaining > 1:
                days_text = f"{days_remaining} days left"
                days_badge = 'orange'
            elif days_remaining == 1:
                days_text = '1 day left'
                days_badge = 'orange'
            elif days_remaining == 0:
                days_text = 'Due today'
                days_badge = 'orange'
            else:
                od = abs(days_remaining)
                days_text = 'Overdue by 1 day' if od == 1 else f'Overdue by {od} days'
                days_badge = 'red'
        enriched.append({
            'id': l.id,
            'name': l.name,
            'borrower': l.borrower,
            'borrower_email': getattr(l, 'borrower_email', None),
            'borrowed_at': l.borrowed_at,
            'due_date': l.due_date.isoformat() if getattr(l, 'due_date', None) else None,
            'days_remaining': days_remaining,
            'days_text': days_text,
            'days_badge': days_badge,
        })
    return render_template('active_loans.html', laptops=enriched)


@app.route('/analytics')
def analytics():
    # Summary metrics
    total_borrows = BorrowHistory.query.count()

    # Top borrowers (name, count)
    top_borrowers_q = db.session.query(
        BorrowHistory.borrower,
        func.count(BorrowHistory.id).label('count')
    ).group_by(BorrowHistory.borrower).order_by(desc('count')).limit(10).all()

    top_borrowers = [{'borrower': r[0], 'count': r[1]} for r in top_borrowers_q]

    # Borrows per device
    per_device_q = db.session.query(
        BorrowHistory.laptop_id,
        func.count(BorrowHistory.id).label('count')
    ).group_by(BorrowHistory.laptop_id).order_by(desc('count')).all()

    # Map laptop ids to names
    device_ids = [r[0] for r in per_device_q]
    devices = {d.id: d.name for d in Laptop.query.filter(Laptop.id.in_(device_ids)).all()} if device_ids else {}
    per_device = [{'laptop_id': r[0], 'name': devices.get(r[0], f'#{r[0]}'), 'count': r[1]} for r in per_device_q]

    # Average borrow duration (only for returned items)
    returned = BorrowHistory.query.filter(BorrowHistory.returned_at.isnot(None)).all()
    total_days = 0
    count_returned = 0
    for r in returned:
        if r.returned_at and r.borrowed_at:
            diff = r.returned_at - r.borrowed_at
            total_days += diff.total_seconds() / 86400.0
            count_returned += 1
    avg_duration_days = round(total_days / count_returned, 2) if count_returned else None

    # Recent borrows
    recent = BorrowHistory.query.order_by(BorrowHistory.id.desc()).limit(10).all()

    return render_template('analytics.html',
                           total_borrows=total_borrows,
                           top_borrowers=top_borrowers,
                           per_device=per_device,
                           avg_duration_days=avg_duration_days,
                           recent=recent)


# --- Other devices routes (borrow/return/manage other equipment) ---
@app.route('/other-devices')
def other_devices_menu():
    # show available devices for borrowing by default
    devices = OtherDevice.query.filter_by(is_borrowed=False).order_by(OtherDevice.id).all()
    return render_template('other_list.html', devices=devices)


@app.route('/other-devices/add', methods=['GET', 'POST'])
def other_add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip() or None
        if not name:
            flash('Please provide a device name.', 'danger')
            return redirect(request.url)
        existing = OtherDevice.query.filter_by(name=name).first()
        if existing:
            flash('A device with that name already exists.', 'warning')
            return redirect(request.url)
        d = OtherDevice(name=name, category=category)
        db.session.add(d)
        db.session.commit()
        flash(f'{name} added.', 'success')
        return redirect(url_for('other_devices_menu'))
    return render_template('other_add.html')


@app.route('/other-devices/available')
def other_available():
    # show only available devices for borrowing
    devices = OtherDevice.query.filter_by(is_borrowed=False).order_by(OtherDevice.id).all()
    return render_template('other_list.html', devices=devices)


@app.route('/other-devices/borrowed')
def other_borrowed():
    # show only borrowed devices for return
    devices = OtherDevice.query.filter_by(is_borrowed=True).order_by(OtherDevice.id).all()
    return render_template('other_list.html', devices=devices)


@app.route('/other-devices/manage/<int:device_id>', methods=['GET', 'POST'])
def other_manage(device_id):
    device = db.session.get(OtherDevice, device_id)
    if device is None:
        abort(404)
    if request.method == 'POST':
        if device.is_borrowed:
            # Return flow
            observation = request.form.get('observation', '').strip() or None
            history = OtherDeviceHistory.query.filter_by(device_id=device.id, returned_at=None).order_by(OtherDeviceHistory.id.desc()).first()
            if history:
                history.returned_at = datetime.now(LIMA).replace(tzinfo=None)
                history.observation = observation
            device.is_borrowed = False
            device.borrower = None
            device.borrower_email = None
            device.borrowed_at = None
            device.due_date = None
            db.session.commit()
            flash(f"{device.name} has been returned.", 'success')
        else:
            # Borrow flow
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            days = request.form.get('days', '').strip()
            if not name:
                flash('Please provide your name to borrow a device.', 'danger')
                return redirect(request.url)
            existing = None
            if email:
                existing = OtherDevice.query.filter(OtherDevice.is_borrowed == True).filter(OtherDevice.borrower_email.ilike(email)).first()
            if not existing:
                existing = OtherDevice.query.filter(OtherDevice.is_borrowed == True).filter(OtherDevice.borrower.ilike(name)).first()
            if existing:
                flash('You already have a borrowed device (return it before borrowing another).', 'warning')
                return redirect(request.url)
            device.is_borrowed = True
            device.borrower = name
            device.borrower_email = email or None
            device.borrowed_at = datetime.now(LIMA).replace(tzinfo=None)
            try:
                requested_days = int(days) if days else 7
            except ValueError:
                flash('Invalid number of days; using default 7.', 'warning')
                requested_days = 7
            if requested_days < 0 or requested_days > 365:
                flash('Requested days must be between 0 and 365.', 'danger')
                return redirect(request.url)
            device.due_date = device.borrowed_at + timedelta(days=requested_days)
            history = OtherDeviceHistory(
                device_id=device.id,
                borrower=name,
                borrower_email=email or None,
                borrowed_at=device.borrowed_at,
                requested_days=requested_days
            )
            db.session.add(history)
            db.session.commit()
            flash(f"{device.name} borrowed by {name}.", 'success')
        return redirect(url_for('other_devices_menu'))
    return render_template('other_manage.html', device=device)


@app.route('/other-devices/delete/<int:device_id>', methods=['POST'])
def other_delete(device_id):
    device = db.session.get(OtherDevice, device_id)
    if device is None:
        abort(404)
    if device.is_borrowed:
        flash('Cannot delete a device that is currently borrowed.', 'warning')
        return redirect(url_for('other_available'))
    name = device.name
    db.session.delete(device)
    db.session.commit()
    flash(f'{name} deleted.', 'success')
    return redirect(url_for('other_available'))


@app.route('/other-devices/status')
def other_status():
    rows = OtherDeviceHistory.query.order_by(OtherDeviceHistory.id.desc()).limit(200).all()
    return render_template('other_status.html', rows=rows)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
