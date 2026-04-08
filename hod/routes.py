from flask import Blueprint, render_template
from flask_login import login_required

hod_bp = Blueprint("hod", __name__, template_folder="templates")

@hod_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("hod_dashboard.html")
