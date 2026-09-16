from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User

auth = Blueprint("auth", __name__)


@auth.route("/dashboard")
@login_required
def dashboard():

    if current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))

    elif current_user.role == "staff":
        return redirect(url_for("staff.dashboard"))

    else:
        return redirect(url_for("user.dashboard"))

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        contact = request.form["contact"]
        role = request.form["role"]

        existing = User.query.filter_by(email=email).first()

        if existing:
            flash("Email already exists!")
            return redirect(url_for("auth.register"))

        hashed = generate_password_hash(password)

        status = "approved"

        if role == "staff":
            status = "pending"

        new_user = User(
            name=name,
            email=email,
            password=hashed,
            role=role,
            status=status,
            contact=contact
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful")

        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user is None:
            flash("Invalid Email")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password, password):
            flash("Wrong Password")
            return redirect(url_for("auth.login"))

        if user.status == "blacklisted":
            flash("Account Blacklisted")
            return redirect(url_for("auth.login"))

        if user.role == "staff" and user.status == "pending":
            flash("Waiting for Admin Approval")
            return redirect(url_for("auth.login"))

        login_user(user)

        return redirect(url_for("auth.dashboard"))

    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged Out Successfully")

    return redirect(url_for("auth.login"))