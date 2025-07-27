# app/routes.py
from datetime import datetime  # Make sure this is imported
from datetime import date, timedelta
from datetime import date
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request
)
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Room, Booking
from app.forms import LoginForm, BookingForm
from datetime import date


bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome, {user.username}!', 'success')
            return redirect(url_for('routes.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/dashboard')
@login_required
def dashboard():
    total_rooms = Room.query.count()
    available_rooms = Room.query.filter_by(status='Available').count()
    rooms = Room.query.all()  # ← Add this line

    # Get recent active request
    recent_request = Booking.query.filter(
        Booking.check_out > date.today(),
        (Booking.needs_cleaning == True) | (Booking.needs_linens_change == True)
    ).order_by(Booking.id.desc()).first()

    bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        total_rooms=total_rooms,
        available_rooms=available_rooms,
        rooms=rooms,  # ← Pass rooms to template
        bookings=bookings,
        recent_request=recent_request
    )

@bp.route('/bookings')
@login_required
def bookings():
    all_bookings = Booking.query.all()
    return render_template('bookings.html', bookings=all_bookings)

@bp.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    form = BookingForm()
    if form.validate_on_submit():
        # Extract data
        room_id = form.room_id.data
        check_in = form.check_in.data
        check_out = form.check_out.data

        # Validate check-in is not in the past
        if check_in < date.today():
            flash('Check-in date cannot be in the past.', 'danger')
            return render_template('book.html', form=form, today=date.today())

        # Validate check-out is after check-in
        if check_out <= check_in:
            flash('Check-out must be after check-in.', 'danger')
            return render_template('book.html', form=form, today=date.today())

        # Prevent double booking
        if Booking.is_room_booked(room_id, check_in, check_out):
            flash('❌ Room is already booked for those dates.', 'danger')
            return render_template('book.html', form=form, today=date.today())

        # Create new booking
        booking = Booking(
            guest_name=form.guest_name.data,
            guest_email=form.guest_email.data,
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            user_id=current_user.id,
            notes=form.notes.data
        )

        # Update room status to 'Booked'
        room = Room.query.get(room_id)
        if room:
            room.status = 'Booked'

        # Save to database
        db.session.add(booking)
        db.session.commit()

        flash(f'✅ Booking created for {booking.guest_name}!', 'success')
        return redirect(url_for('routes.bookings'))

    # GET request or form not submitted — show the form
    return render_template('book.html', form=form, today=date.today())
     
      

@bp.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    room = booking.room

    # Free up the room
    room.status = 'Available'

    # Remove the booking
    db.session.delete(booking)
    db.session.commit()

    flash(f'✅ Booking for {booking.guest_name} has been canceled.', 'info')
    return redirect(url_for('routes.bookings'))

@bp.route('/calendar')
@login_required
def calendar():
    import calendar as py_calendar
    from datetime import datetime

    today = datetime.today()
    year = today.year
    month = today.month
    cal = py_calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    # ✅ Use a different variable name
    all_bookings = Booking.query.all()

    calendar_bookings = {}
    for b in all_bookings:  # ✅ Now it's clear
        date = b.check_in
        while date < b.check_out:
            key = date.strftime('%Y-%m-%d')
            if key not in calendar_bookings:
                calendar_bookings[key] = []
            calendar_bookings[key].append({
                'guest': b.guest_name,
                'room': b.room.room_number,
                'type': 'stay'
            })
            if date == b.check_in:
                if key not in calendar_bookings:
                    calendar_bookings[key] = []
                calendar_bookings[key].append({
                    'guest': b.guest_name,
                    'room': b.room.room_number,
                    'type': 'check-in'
                })
            date += timedelta(days=1)

    return render_template(
        'calendar.html',
        year=year,
        month=month,
        month_name=py_calendar.month_name[month],
        month_days=month_days,
        calendar_bookings=calendar_bookings,
        datetime=datetime
    )

@bp.route('/rooms')
@login_required
def room_status():
    rooms = Room.query.all()
    active_bookings = Booking.query.filter(Booking.check_out > date.today()).all()

    room_status = {}
    for room in rooms:
        room_status[room] = None
        for b in active_bookings:
            if b.room_id == room.id:
                room_status[room] = b
                break

    return render_template('rooms.html', room_status=room_status)


@bp.route('/checkout/<int:booking_id>', methods=['POST'])
@login_required
def checkout(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    room = booking.room
    room.status = 'Available'
    # Optional: mark booking as checked out instead of deleting
    db.session.commit()
    flash(f'✅ {booking.guest_name} has checked out. Room {room.room_number} is now available.', 'info')
    return redirect(url_for('routes.room_status'))


@bp.route('/mark_maintenance/<int:room_id>')
@login_required
def mark_maintenance(room_id):
    room = Room.query.get_or_404(room_id)
    room.status = 'Maintenance'
    db.session.commit()
    flash(f'🔧 Room {room.room_number} is now marked as needing maintenance.', 'warning')
    return redirect(url_for('routes.room_status'))


@bp.route('/unmark_maintenance/<int:room_id>')
@login_required
def unmark_maintenance(room_id):
    room = Room.query.get_or_404(room_id)
    room.status = 'Available'
    db.session.commit()
    flash(f'✅ Room {room.room_number} is back in service.', 'success')
    return redirect(url_for('routes.room_status'))

@bp.route('/request_cleaning/<int:booking_id>', methods=['POST'])
@login_required
def request_cleaning(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.needs_cleaning = True
    db.session.commit()
    flash(f'✅ Housekeeping request: {booking.guest_name} in Room {booking.room.room_number} needs cleaning.', 'info')
    return redirect(url_for('routes.room_status'))


@bp.route('/request_linens/<int:booking_id>', methods=['POST'])
@login_required
def request_linens(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.needs_linens_change = True
    db.session.commit()
    flash(f'✅ Housekeeping request: {booking.guest_name} in Room {booking.room.room_number} needs linens changed.', 'info')
    return redirect(url_for('routes.room_status'))

@bp.route('/extend_stay/<int:booking_id>')
@login_required
def extend_stay(booking_id):
    flash("✅ Extend Stay: Coming soon!", "info")
    return redirect(url_for('routes.room_status'))


@bp.route('/room_transfer/<int:booking_id>')
@login_required
def room_transfer(booking_id):
    flash("✅ Room Transfer: Coming soon!", "info")
    return redirect(url_for('routes.room_status'))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('routes.login'))