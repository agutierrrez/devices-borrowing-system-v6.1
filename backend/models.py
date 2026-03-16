from . import db
from datetime import datetime


class Laptop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    is_borrowed = db.Column(db.Boolean, default=False, nullable=False)
    borrower = db.Column(db.String(100), nullable=True)
    borrower_email = db.Column(db.String(200), nullable=True)
    borrowed_at = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Laptop {self.name}>'

    @property
    def history(self):
        return BorrowHistory.query.filter_by(laptop_id=self.id).order_by(BorrowHistory.id).all()



class BorrowHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    laptop_id = db.Column(db.Integer, db.ForeignKey('laptop.id'), nullable=False)
    laptop = db.relationship('Laptop')
    borrower = db.Column(db.String(100), nullable=False)
    borrower_email = db.Column(db.String(200), nullable=True)
    borrowed_at = db.Column(db.DateTime, nullable=False)
    returned_at = db.Column(db.DateTime, nullable=True)
    observation = db.Column(db.Text, nullable=True)
    # Number of days the borrower requested when borrowing (nullable)
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

    @property
    def history(self):
        from backend.models import OtherDeviceHistory as _ODH
        return _ODH.query.filter_by(device_id=self.id).order_by(_ODH.id).all()


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
