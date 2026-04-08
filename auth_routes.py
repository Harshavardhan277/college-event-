from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from models import User
from email_utils import send_otp_email, generate_otp
from utils import generate_qr_code
import time

auth_bp = Blueprint("auth", __name__)


# SEND OTP
@auth_bp.route("/send_otp", methods=["POST"])
def send_otp():

    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400

    otp_code = generate_otp()

    # store in session
    session["registration_otp"] = otp_code
    session["registration_email"] = email
    session["otp_expiry"] = time.time() + 600   # 10 minutes

    if send_otp_email(email, otp_code):
        return jsonify({"message": "OTP sent successfully"}), 200

    return jsonify({"error": "Failed to send OTP"}), 500


# REGISTER
@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("stu.dashboard"))

    if request.method == "POST":

        register_number = request.form.get("register_number")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        user_otp = request.form.get("otp")

        if not register_number or not register_number.isdigit():
            flash("Register Number must contain only numbers.", "error")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.register"))

        if time.time() > session.get("otp_expiry", 0):
            flash("OTP expired. Please request again.", "error")
            return redirect(url_for("auth.register"))

        if email != session.get("registration_email") or user_otp != session.get("registration_otp"):
            flash("Invalid OTP.", "error")
            return redirect(url_for("auth.register"))

        # create user
        student_id = User.create_user(
            username=register_number,
            password=password,
            role="stu",
            email=email,
            register_number=register_number,
            name=register_number
        )

        # generate QR
        qr_path = generate_qr_code(str(student_id), register_number)
        User.update_qr_path(student_id, qr_path)

        # clear session
        session.pop("registration_otp", None)
        session.pop("registration_email", None)
        session.pop("otp_expiry", None)

        flash("Registration successful! Please login.", "success")

        return redirect(url_for("auth.login"))

    return render_template("student_register.html")


# LOGIN — redirect to main landing page (each portal has its own login)
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # If already authenticated, redirect to their respective dashboard
    if current_user.is_authenticated:
        role = getattr(current_user, 'role', None)
        if role == 'adm':
            return redirect(url_for("adm.dashboard"))
        if role == 'clu':
            return redirect(url_for("clu.dashboard"))
        if role in ['HOD', 'Dean', 'hod']:
            return redirect(url_for("ho.dashboard"))
        return redirect(url_for("stu.dashboard"))

    # No generic login — redirect to the landing page where users choose their portal
    return redirect(url_for("index"))



# LOGOUT
@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("auth.login"))


# FORGOT PASSWORD
@auth_bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if current_user.is_authenticated:
        return redirect(url_for("stu.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        user = User.find_by_email(email)

        if user:
            otp_code = generate_otp()
            session["password_reset_otp"] = otp_code
            session["password_reset_email"] = email
            session["otp_expiry"] = time.time() + 600   # 10 minutes

            if send_otp_email(email, otp_code):
                flash("OTP sent to your email.", "success")
                return redirect(url_for("auth.reset_password"))
            else:
                flash("Failed to send OTP. Please try again.", "error")
        else:
            flash("Email not found.", "error")

    return render_template("forgot_password.html")


# RESET PASSWORD
@auth_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():

    if current_user.is_authenticated:
        return redirect(url_for("stu.dashboard"))

    if request.method == "POST":
        otp = request.form.get("otp")
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        email = session.get("password_reset_email")

        if not email:
            flash("Session expired. Please start again.", "error")
            return redirect(url_for("auth.forgot_password"))

        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("reset_password.html")

        if time.time() > session.get("otp_expiry", 0):
            flash("OTP expired. Please request again.", "error")
            return redirect(url_for("auth.forgot_password"))

        if otp != session.get("password_reset_otp"):
            flash("Invalid OTP.", "error")
            return render_template("reset_password.html")

        user = User.find_by_email(email)
        if user:
            User.update_password(user.id, new_password)
            
            # clear session
            session.pop("password_reset_otp", None)
            session.pop("password_reset_email", None)
            session.pop("otp_expiry", None)

            flash("Password updated successfully! Please login.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("User not found.", "error")
            return redirect(url_for("auth.forgot_password"))

    return render_template("reset_password.html")