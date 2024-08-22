from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User

auth = Blueprint("auth", __name__)


@auth.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                if user.role == role:
                    login_user(user, remember=True)
                    flash("Logged in", category="success")
                    if role == "Admin":
                        return redirect(url_for("admin.dashboard"))
                    elif role == "Sponsor":
                        return redirect(url_for("sponsor.dashboard"))
                    elif role == "Influencer":
                        return redirect(url_for("influencer.dashboard"))
                else:
                    flash(
                        "Incorrect role selected.",
                        category="error",
                    )
            else:
                flash("Incorrect password.", category="error")
        else:
            flash("Email does not exist.", category="error")

    return render_template("login.html", user=current_user)


@auth.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")
        role = request.form.get("role")
        niche = request.form.get("niche")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", category="error")
        else:
            new_user = User(
                email=email,
                role=role,
                name=name,
                user_niche=niche,
                password=generate_password_hash(password),
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created!", category="success")
            return redirect(url_for("auth.login"))

    return render_template("signup.html", user=current_user)


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out!", category="success")
    return redirect(url_for("auth.login"))
