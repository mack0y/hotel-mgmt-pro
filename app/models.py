# app/models.py
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='staff')  # admin or staff

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Available')

    def __repr__(self):
        return f"<Room {self.room_number}>"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(150), nullable=False)
    guest_email = db.Column(db.String(120))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    booking_date = db.Column(db.Date, default=date.today)
    notes = db.Column(db.Text, nullable=True)

    room = db.relationship('Room', backref='bookings')
    user = db.relationship('User', backref='bookings')
    special_requests = db.Column(db.Text)  # e.g., "Late check-in"
    needs_cleaning = db.Column(db.Boolean, default=False)
    needs_linens_change = db.Column(db.Boolean, default=False)
    
    
    @staticmethod
    def is_room_booked(room_id, check_in, check_out):
        """
        Check if a room is already booked for the given dates.
        Returns True if there's a conflict.
        """
        if not room_id or not check_in or not check_out:
            return True
        if not isinstance(check_in, date) or not isinstance(check_out, date):
            return True
        if check_out <= check_in:
            return True

        conflict = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.check_in < check_out,
            Booking.check_out > check_in
        ).first()

        return conflict is not None