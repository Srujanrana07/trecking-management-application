from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)
    # admin
    # staff
    # user

    status = db.Column(db.String(20), default="pending")
    # pending
    # approved
    # blacklisted

    contact = db.Column(db.String(20))


class Trek(db.Model):

    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    location = db.Column(db.String(100))

    difficulty = db.Column(db.String(30))

    duration = db.Column(db.Integer)

    available_slots = db.Column(db.Integer)

    status = db.Column(db.String(20), default="Open")

    start_date = db.Column(db.Date)

    end_date = db.Column(db.Date)

    description = db.Column(db.Text)

    staff_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )


class Booking(db.Model):

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    booking_date = db.Column(db.Date)

    status = db.Column(db.String(20), default="Booked")

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("treks.id")
    )