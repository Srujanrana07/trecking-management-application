from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from models import db, User, Trek, Booking

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/dashboard")
@login_required
def dashboard():

    # Only admin can access
    if current_user.role != "admin":
        return "Access Denied"

    total_treks = Trek.query.count()

    total_users = User.query.filter_by(role="user").count()

    total_staff = User.query.filter_by(role="staff").count()

    total_bookings = Booking.query.count()

    return render_template(
        "admin/dashboard.html",
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings
    )

@admin.route("/treks")
@login_required
def view_treks():

    if current_user.role != "admin":
        return "Access Denied"

    treks = Trek.query.all()

   
    staff_dict = {
        staff.id: staff.name
        for staff in User.query.filter_by(role="staff").all()
    }

    return render_template(
        "admin/treks.html",
        treks=treks,
        staff_dict=staff_dict
    )

@admin.route("/add-trek", methods=["GET", "POST"])
@login_required
def add_trek():

    if current_user.role != "admin":
        return "Access Denied"

    if request.method == "POST":

        trek = Trek(

            name=request.form["name"],

            location=request.form["location"],

            difficulty=request.form["difficulty"],

            duration=int(request.form["duration"]),

            available_slots=int(request.form["available_slots"]),

            status=request.form["status"],

            start_date=datetime.strptime(
                request.form["start_date"],
                "%Y-%m-%d"
            ).date(),

            end_date=datetime.strptime(
                request.form["end_date"],
                "%Y-%m-%d"
            ).date(),

            description=request.form["description"]

        )

        db.session.add(trek)

        db.session.commit()

        flash("Trek Added Successfully!")

        return redirect(url_for("admin.view_treks"))

    return render_template("admin/add_trek.html")

@admin.route("/edit-trek/<int:trek_id>", methods=["GET", "POST"])
@login_required
def edit_trek(trek_id):

    if current_user.role != "admin":
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)

    if request.method == "POST":

        trek.name = request.form["name"]
        trek.location = request.form["location"]
        trek.difficulty = request.form["difficulty"]
        trek.duration = int(request.form["duration"])
        trek.available_slots = int(request.form["available_slots"])
        trek.status = request.form["status"]

        trek.start_date = datetime.strptime(
            request.form["start_date"],
            "%Y-%m-%d"
        ).date()

        trek.end_date = datetime.strptime(
            request.form["end_date"],
            "%Y-%m-%d"
        ).date()

        trek.description = request.form["description"]

        db.session.commit()

        flash("Trek Updated Successfully!")

        return redirect(url_for("admin.view_treks"))

    return render_template(
        "admin/edit_trek.html",
        trek=trek
    )

@admin.route("/delete-trek/<int:trek_id>")
@login_required
def delete_trek(trek_id):

    if current_user.role != "admin":
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)

    db.session.commit()

    flash("Trek Deleted Successfully!")

    return redirect(url_for("admin.view_treks"))

@admin.route("/approve-staff")
@login_required
def approve_staff():

    if current_user.role != "admin":
        return "Access Denied"

    pending_staff = User.query.filter_by(
        role="staff",
        status="pending"
    ).all()

    return render_template(
        "admin/approve_staff.html",
        pending_staff=pending_staff
    )

@admin.route("/approve-staff/<int:staff_id>")
@login_required
def approve_staff_member(staff_id):

    if current_user.role != "admin":
        return "Access Denied"

    staff = User.query.get_or_404(staff_id)

    staff.status = "approved"

    db.session.commit()

    flash("Staff approved successfully!")

    return redirect(url_for("admin.approve_staff"))


@admin.route("/assign-staff/<int:trek_id>", methods=["GET", "POST"])
@login_required
def assign_staff(trek_id):

    if current_user.role != "admin":
        return "Access Denied"

    trek = Trek.query.get_or_404(trek_id)

    approved_staff = User.query.filter_by(
        role="staff",
        status="approved"
    ).all()

    if request.method == "POST":

        trek.staff_id = int(request.form["staff_id"])

        db.session.commit()

        flash("Staff assigned successfully!")

        return redirect(url_for("admin.view_treks"))

    return render_template(
        "admin/assign_staff.html",
        trek=trek,
        approved_staff=approved_staff
    )

@admin.route("/users")
@login_required
def view_users():

    if current_user.role != "admin":
        return "Access Denied"

    users = User.query.all()

    return render_template(
        "admin/users.html",
        users=users
    )


@admin.route("/toggle-blacklist/<int:user_id>")
@login_required
def toggle_blacklist(user_id):

    if current_user.role != "admin":
        return "Access Denied"

    user = User.query.get_or_404(user_id)


    if user.role == "admin":
        flash("Admin cannot be blacklisted.")
        return redirect(url_for("admin.view_users"))

    if user.status == "blacklisted":


        if user.role == "staff":
            user.status = "approved"
        else:
            user.status = "approved"

        flash("User removed from blacklist successfully!")

    else:

        user.status = "blacklisted"

        flash("User blacklisted successfully!")

    db.session.commit()

    return redirect(url_for("admin.view_users"))


@admin.route("/bookings")
@login_required
def view_bookings():

    if current_user.role != "admin":
        return "Access Denied"

    bookings = Booking.query.all()

    user_dict = {
        user.id: user
        for user in User.query.all()
    }

    trek_dict = {
        trek.id: trek
        for trek in Trek.query.all()
    }

    return render_template(
        "admin/bookings.html",
        bookings=bookings,
        user_dict=user_dict,
        trek_dict=trek_dict
    )

@admin.route("/search")
@login_required
def search():

    if current_user.role != "admin":
        return "Access Denied"

    query = request.args.get("q", "").strip()

    treks = []
    users = []
    staff = []

    if query:


        treks = Trek.query.filter(
            db.or_(
                Trek.name.ilike(f"%{query}%"),
                db.cast(Trek.id, db.String).ilike(f"%{query}%")
            )
        ).all()

        users = User.query.filter(
            User.role == "user",
            db.or_(
                User.name.ilike(f"%{query}%"),
                db.cast(User.id, db.String).ilike(f"%{query}%")
            )
        ).all()


        staff = User.query.filter(
            User.role == "staff",
            db.or_(
                User.name.ilike(f"%{query}%"),
                db.cast(User.id, db.String).ilike(f"%{query}%")
            )
        ).all()

    return render_template(
        "admin/search.html",
        query=query,
        treks=treks,
        users=users,
        staff=staff
    )