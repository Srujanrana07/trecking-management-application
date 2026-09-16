from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db, Trek, Booking, User

staff = Blueprint("staff", __name__, url_prefix="/staff")


@staff.route("/dashboard")
@login_required
def dashboard():

    if current_user.role != "staff":
        return "Access Denied"

    assigned_count = Trek.query.filter_by(
        staff_id=current_user.id
    ).count()

    return render_template(
        "staff/dashboard.html",
        assigned_count=assigned_count
    )


@staff.route("/treks")
@login_required
def assigned_treks():

    if current_user.role != "staff":
        return "Access Denied"

    treks = Trek.query.filter_by(
        staff_id=current_user.id
    ).all()

    return render_template(
        "staff/assigned_treks.html",
        treks=treks
    )

@staff.route("/manage-trek/<int:trek_id>", methods=["GET", "POST"])
@login_required
def manage_trek(trek_id):

    if current_user.role != "staff":
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)

    
    if trek.staff_id != current_user.id:
        return "Access Denied"

    if request.method == "POST":

        trek.available_slots = int(request.form["available_slots"])
        trek.status = request.form["status"]

        db.session.commit()

        flash("Trek updated successfully!")

        return redirect(url_for("staff.assigned_treks"))

    return render_template(
        "staff/manage_trek.html",
        trek=trek
    )

@staff.route("/participants/<int:trek_id>")
@login_required
def view_participants(trek_id):

    if current_user.role != "staff":
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)


    if trek.staff_id != current_user.id:
        return "Access Denied"

    bookings = Booking.query.filter_by(
        trek_id=trek.id,
        status="Booked"
    ).all()

    user_dict = {
        user.id: user
        for user in User.query.all()
    }

    return render_template(
        "staff/participants.html",
        trek=trek,
        bookings=bookings,
        user_dict=user_dict
    )