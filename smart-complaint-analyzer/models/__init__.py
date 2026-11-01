from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

def now(): return datetime.now(timezone.utc).replace(tzinfo=None)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(12), nullable=False, default='citizen')
    created_at = db.Column(db.DateTime, default=now, nullable=False)
    complaints = db.relationship('Complaint', backref='citizen', lazy='dynamic')
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    landmark = db.Column(db.String(150))
    predicted_category = db.Column(db.String(80), nullable=False)
    confirmed_category = db.Column(db.String(80))
    assigned_department = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(10), nullable=False)
    priority_reason = db.Column(db.String(300), nullable=False)
    model_confidence = db.Column(db.Float)
    status = db.Column(db.String(30), default='Submitted', nullable=False, index=True)
    image_filename = db.Column(db.String(100))
    possible_duplicate = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(db.DateTime, default=now, onupdate=now, nullable=False)
    resolved_at = db.Column(db.DateTime)
    history = db.relationship('StatusHistory', backref='complaint', order_by='StatusHistory.changed_at', cascade='all, delete-orphan')
class StatusHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False, index=True)
    old_status = db.Column(db.String(30))
    new_status = db.Column(db.String(30), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note = db.Column(db.String(500))
    changed_at = db.Column(db.DateTime, default=now, nullable=False)
    actor = db.relationship('User')


class AuthorityContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(254))
    phone = db.Column(db.String(20))  # E.164 format, e.g. +919876543210
    email_enabled = db.Column(db.Boolean, default=True, nullable=False)
    sms_enabled = db.Column(db.Boolean, default=False, nullable=False)
    whatsapp_enabled = db.Column(db.Boolean, default=False, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    consent_confirmed = db.Column(db.Boolean, default=False, nullable=False)

class NotificationDelivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False, index=True)
    authority_id = db.Column(db.Integer, db.ForeignKey('authority_contact.id'), nullable=False)
    channel = db.Column(db.String(12), nullable=False)
    status = db.Column(db.String(16), nullable=False)  # sent, failed, skipped
    detail = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=now, nullable=False)
    authority = db.relationship('AuthorityContact')
