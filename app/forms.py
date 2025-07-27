# app/forms.py
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField,
    SelectField, DateField, TextAreaField
)
from wtforms.validators import DataRequired, Email, Length
from app.models import Room
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from app.models import Room
from datetime import date

class BookingForm(FlaskForm):
    guest_name = StringField('Guest Name', validators=[DataRequired()])
    guest_email = StringField('Email', validators=[DataRequired(), Email()])
    room_id = SelectField('Room', coerce=int, validators=[DataRequired()])
    check_in = DateField('Check-In', format='%Y-%m-%d', validators=[DataRequired()])
    check_out = DateField('Check-Out', format='%Y-%m-%d', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Book Room')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Always reload available rooms
        self.room_id.choices = [
            (r.id, f"{r.room_number} ({r.room_type} - ₱{r.price})")
            for r in Room.query.filter_by(status='Available').all()
        ]
        # Add fallback message if no rooms
        if not self.room_id.choices:
            self.room_id.choices = [(-1, "No rooms available")]