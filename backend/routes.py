from flask import render_template, request, redirect, url_for, flash, abort, session
from . import app, db, LIMA
from .models import Laptop, BorrowHistory, OtherDevice, OtherDeviceHistory, User
from datetime import datetime, timedelta
import math
from sqlalchemy import func


@app.route('/')
def index():
    laptops = Laptop.query.order_by(Laptop.id).all()
    # use naive local (Lima) now for comparisons with DB-stored naive local datetimes
    now = datetime.now(LIMA).replace(tzinfo=None)
    items = []
    for l in laptops:
        due = l.due_date
        # DB stores naive local (Lima) datetimes; format and compare directly
        due_str = due.strftime('%Y-%m-%d') if due else None
        is_overdue = bool(l.is_borrowed and due and due < now)
        days_remaining = None
        if l.is_borrowed and due:
            # use ceiling so partial days count as a full day remaining
            secs = (due - now).total_seconds()
            if secs > 0:
                days_remaining = math.ceil(secs / 86400)
            else:
                days_remaining = -math.ceil(abs(secs) / 86400)
        # prepare human-friendly text and badge class
        days_text = None
        days_badge = None
        if l.is_borrowed and due:
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
                overdue_days = abs(days_remaining)
                if overdue_days == 1:
                    days_text = 'Overdue by 1 day'
                else:
                    days_text = f'Overdue by {overdue_days} days'
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
            'comments': l.comments,
        })
    return render_template('index.html', items=items)


@app.route('/active-loans')
def active_loans():
    laptops = Laptop.query.filter_by(is_borrowed=True).order_by(Laptop.id).all()
    # compute days_remaining and human-friendly text for template
    now = datetime.now(LIMA).replace(tzinfo=None)
    enriched = []
    for l in laptops:
        due = l.due_date
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
                overdue_days = abs(days_remaining)
                if overdue_days == 1:
                    days_text = 'Overdue by 1 day'
                else:
                    days_text = f'Overdue by {overdue_days} days'
                days_badge = 'red'
        enriched.append({
            'id': l.id,
            'name': l.name,
            'borrower': l.borrower,
            'borrower_email': getattr(l, 'borrower_email', None),
            'borrowed_at': l.borrowed_at,
            'due_date': l.due_date.isoformat() if l.due_date else None,
            'days_remaining': days_remaining,
            'days_text': days_text,
            'days_badge': days_badge,
            'is_overdue': bool(due and due < now),
        })
    return render_template('active_loans.html', laptops=enriched)


@app.route('/borrow/<int:laptop_id>', methods=['GET', 'POST'])
def borrow(laptop_id):
    laptop = db.session.get(Laptop, laptop_id)
    if laptop is None:
        from flask import abort
        abort(404)
    if laptop.is_borrowed:
        flash('This laptop is already borrowed.', 'warning')
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        days = request.form.get('days', '').strip()
        email = request.form.get('email', '').strip()
        # optional config to require email for borrowing
        if app.config.get('REQUIRE_BORROWER_EMAIL') and not email:
            flash('Please provide an email to borrow a laptop.', 'danger')
            return redirect(request.url)
        if not name:
            flash('Please provide your name to borrow a laptop.', 'danger')
            return redirect(request.url)
        # Prevent a borrower from borrowing another device until they return
        # the one they currently have. Check by name or email (if provided).
        # Perform case-insensitive checks for email and name to avoid dupes
        existing = None
        if email:
            existing = Laptop.query.filter(Laptop.is_borrowed == True).filter(Laptop.borrower_email.ilike(email)).first()
        if not existing:
            existing = Laptop.query.filter(Laptop.is_borrowed == True).filter(Laptop.borrower.ilike(name)).first()
        if existing:
            flash('You already have a borrowed laptop (return it before borrowing another).', 'warning')
            return redirect(url_for('index'))
        laptop.is_borrowed = True
        laptop.borrower = name
        laptop.borrower_email = email or None
        # store naive local (Lima) time in DB
        laptop.borrowed_at = datetime.now(LIMA).replace(tzinfo=None)
        try:
            requested_days = int(days) if days else 7
        except ValueError:
            flash('Invalid number of days; using default 7.', 'warning')
            requested_days = 7
        # enforce sensible range
        if requested_days < 0 or requested_days > 365:
            flash('Requested days must be between 0 and 365.', 'danger')
            return redirect(request.url)
        laptop.due_date = laptop.borrowed_at + timedelta(days=requested_days)
        history = BorrowHistory(
            laptop=laptop,
            borrower=name,
            borrower_email=email or None,
            borrowed_at=laptop.borrowed_at,
            requested_days=requested_days,
        )
        db.session.add(history)
        db.session.commit()
        flash(f"{laptop.name} borrowed by {name}.", 'success')
        return redirect(url_for('index'))
    return render_template('borrow.html', laptop=laptop)


@app.route('/debug/history')
def debug_history():
    # Only expose this in debug mode
    if not app.debug:
        from flask import abort
        abort(404)
    rows = BorrowHistory.query.order_by(BorrowHistory.id.desc()).limit(50).all()
    out = []
    for r in rows:
        out.append({
            'id': r.id,
            'laptop_id': r.laptop_id,
            'laptop_name': r.laptop.name if r.laptop else None,
            'borrower': r.borrower,
            'borrower_email': r.borrower_email,
            'borrowed_at': r.borrowed_at.isoformat() if r.borrowed_at else None,
            'returned_at': r.returned_at.isoformat() if r.returned_at else None,
            'observation': r.observation,
        })
    from flask import jsonify
    return jsonify(out)


@app.route('/return/<int:laptop_id>', methods=['GET', 'POST'])
def return_laptop(laptop_id):
    laptop = db.session.get(Laptop, laptop_id)
    if laptop is None:
        from flask import abort
        abort(404)
    if not laptop.is_borrowed:
        flash('Laptop is not currently borrowed.', 'warning')
        return redirect(url_for('index'))
    if request.method == 'POST':
        observation = request.form.get('observation', '').strip() or None
        history = BorrowHistory.query.filter_by(laptop_id=laptop.id, returned_at=None).order_by(BorrowHistory.id.desc()).first()
        if history:
            # store naive local (Lima) time in DB
            history.returned_at = datetime.now(LIMA).replace(tzinfo=None)
            history.observation = observation
        laptop.is_borrowed = False
        laptop.borrower = None
        laptop.borrower_email = None
        laptop.borrowed_at = None
        laptop.due_date = None
        db.session.commit()
        flash(f"{laptop.name} has been returned.", 'success')
        return redirect(url_for('index'))
    return render_template('return.html', laptop=laptop)


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


@app.route('/other-devices/borrow/<int:device_id>', methods=['GET', 'POST'])
def other_borrow(device_id):
    device = db.session.get(OtherDevice, device_id)
    if device is None:
        from flask import abort
        abort(404)
    if device.is_borrowed:
        flash('This device is already borrowed.', 'warning')
        return redirect(url_for('other_available'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        days = request.form.get('days', '').strip()
        if not name:
            flash('Please provide your name to borrow a device.', 'danger')
            return redirect(request.url)
        # prevent duplicate active borrow by same person
        existing = None
        if email:
            existing = OtherDevice.query.filter(OtherDevice.is_borrowed == True).filter(OtherDevice.borrower_email.ilike(email)).first()
        if not existing:
            existing = OtherDevice.query.filter(OtherDevice.is_borrowed == True).filter(OtherDevice.borrower.ilike(name)).first()
        if existing:
            flash('You already have a borrowed device (return it before borrowing another).', 'warning')
            return redirect(url_for('other_devices_menu'))
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
            device=device,
            borrower=name,
            borrower_email=email or None,
            borrowed_at=device.borrowed_at,
            requested_days=requested_days,
        )
        db.session.add(history)
        db.session.commit()
        flash(f"{device.name} borrowed by {name}.", 'success')
        return redirect(url_for('other_devices_menu'))
    return render_template('other_borrow.html', device=device)


@app.route('/other-devices/return/<int:device_id>', methods=['GET', 'POST'])
def other_return(device_id):
    device = db.session.get(OtherDevice, device_id)
    if device is None:
        from flask import abort
        abort(404)
    if not device.is_borrowed:
        flash('Device is not currently borrowed.', 'warning')
        return redirect(url_for('other_devices_menu'))
    if request.method == 'POST':
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
        return redirect(url_for('other_devices_menu'))
    return render_template('other_return.html', device=device)


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


@app.route('/analytics')
def analytics():
    # Total borrows from laptops and other devices
    laptop_borrows = db.session.query(func.count(BorrowHistory.id)).scalar() or 0
    other_borrows = db.session.query(func.count(OtherDeviceHistory.id)).scalar() or 0
    total_borrows = laptop_borrows + other_borrows

    # Avg duration for completed borrows
    laptop_histories = BorrowHistory.query.filter(BorrowHistory.returned_at.isnot(None)).all()
    other_histories = OtherDeviceHistory.query.filter(OtherDeviceHistory.returned_at.isnot(None)).all()
    durations = []
    for h in laptop_histories + other_histories:
        if h.returned_at and h.borrowed_at:
            durations.append((h.returned_at - h.borrowed_at).days)
    avg_duration_days = sum(durations) / len(durations) if durations else None

    # Top borrowers from both tables
    laptop_top = db.session.query(
        BorrowHistory.borrower,
        func.count(BorrowHistory.id).label('count')
    ).group_by(BorrowHistory.borrower).order_by(func.count(BorrowHistory.id).desc()).limit(10).all()
    
    other_top = db.session.query(
        OtherDeviceHistory.borrower,
        func.count(OtherDeviceHistory.id).label('count')
    ).group_by(OtherDeviceHistory.borrower).order_by(func.count(OtherDeviceHistory.id).desc()).limit(10).all()
    
    # Combine and sort
    all_top = {}
    for borrower, count in laptop_top:
        all_top[borrower] = all_top.get(borrower, 0) + count
    for borrower, count in other_top:
        all_top[borrower] = all_top.get(borrower, 0) + count
    
    top_borrowers = sorted(all_top.items(), key=lambda x: x[1], reverse=True)[:10]
    top_borrowers = [{'borrower': b, 'count': c} for b, c in top_borrowers]

    return render_template('analytics.html', total_borrows=total_borrows, avg_duration_days=round(avg_duration_days, 1) if avg_duration_days else None, top_borrowers=top_borrowers)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_admin:
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/edit-comment/<int:laptop_id>', methods=['GET', 'POST'])
def edit_comment(laptop_id):
    # Check if user is logged in as admin
    if 'user_id' not in session:
        flash('You must be logged in as an admin to edit comments.', 'danger')
        return redirect(url_for('login'))
    
    laptop = Laptop.query.get_or_404(laptop_id)
    
    if request.method == 'POST':
        comment = request.form.get('comment', '').strip()
        laptop.comments = comment if comment else None
        db.session.commit()
        flash('Comment updated successfully.', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit_comment.html', laptop=laptop)


# history route removed to revert to previous state
