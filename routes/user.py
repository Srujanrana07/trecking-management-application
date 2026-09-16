from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date

from models import db, Trek, Booking

user = Blueprint("user", __name__, url_prefix="/user")



@user.route("/dashboard")
@login_required
def dashboard():

    if current_user.role != "user":
        return "Access Denied"

    treks = Trek.query.filter_by(status="Open").all()

 
    available_treks = Trek.query.filter(
        Trek.status == "Open",
        Trek.available_slots > 0
    ).count()

    booked_treks = Booking.query.filter_by(
        user_id=current_user.id,
        status="Booked"
    ).count()

    user_bookings = Booking.query.filter_by(
        user_id=current_user.id,
        status="Booked"
    ).all()

    booked_trek_ids = {
        booking.trek_id
        for booking in user_bookings
    }

    return render_template(
        "user/dashboard.html",
        treks=treks,
        available_treks=available_treks,
        booked_treks=booked_treks,
        booked_trek_ids=booked_trek_ids
    )



@user.route("/treks")
@login_required
def available_treks():

    if current_user.role != "user":
        return "Access Denied"

    treks = Trek.query.filter_by(
        status="Open"
    ).all()

    return render_template(
        "user/available_treks.html",
        treks=treks
    )


@user.route("/book/<int:trek_id>")
@login_required
def book_trek(trek_id):

    if current_user.role != "user":
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)

    if trek.status != "Open":
        flash("This trek is not open for booking.")
        return redirect(url_for("user.dashboard"))


    existing = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek.id,
        status="Booked"
    ).first()

    if existing:
        flash("You have already booked this trek.")
        return redirect(url_for("user.dashboard"))
    
    if trek.available_slots <= 0:
        flash("No slots available.")
        return redirect(url_for("user.dashboard"))

    # Create booking
    booking = Booking(
        booking_date=date.today(),
        status="Booked",
        user_id=current_user.id,
        trek_id=trek.id
    )

    db.session.add(booking)

    trek.available_slots -= 1

    db.session.commit()

    flash("Trek booked successfully!")

    return redirect(url_for("user.my_bookings"))


# ==========================
# My Bookings
# ==========================
@user.route("/my-bookings")
@login_required
def my_bookings():

    if current_user.role != "user":
        return "Access Denied"

    bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).all()

    trek_dict = {
        trek.id: trek.name
        for trek in Trek.query.all()
    }

    return render_template(
        "user/my_bookings.html",
        bookings=bookings,
        trek_dict=trek_dict
    )