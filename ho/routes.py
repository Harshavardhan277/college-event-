from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models import HodDean, Event, User
from extensions import db
from email_utils import send_event_status_email

ho_bp = Blueprint("ho", __name__, template_folder="templates")

@ho_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if hasattr(current_user, 'role') and current_user.role in ['HOD', 'Dean']:
            return redirect(url_for("ho.dashboard"))
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = HodDean.verify_password(username, password)
        if user:
            login_user(user)
            return redirect(url_for("ho.dashboard"))
        
        flash("Invalid username or password", "error")

    return render_template("ho_login.html")

@ho_bp.route("/dashboard")
@login_required
def dashboard():
    # Ensure only HOD/Dean can access
    if not isinstance(current_user, HodDean):
        return redirect(url_for("ho.login"))
    
    # Get events assigned to this HOD/Dean
    assigned_query = Event.query.filter((Event.approver_1 == current_user.username) | (Event.approver_2 == current_user.username))
    
    pending_count = assigned_query.filter(
        (Event.approval_status == "Pending Approval") |
        (Event.approval_status.like("Awaiting Approval from %"))
    ).count()
    approved_count = assigned_query.filter_by(approval_status="Approved").count()
    rejected_count = assigned_query.filter_by(approval_status="Rejected").count()
    
    recent_events = assigned_query.order_by(Event.created_at.desc()).limit(5).all()
    
    return render_template("ho_dashboard.html", 
                           pending_count=pending_count, 
                           approved_count=approved_count, 
                           rejected_count=rejected_count,
                           recent_events=recent_events)

@ho_bp.route("/event_approvals")
@login_required
def event_approvals():
    if not isinstance(current_user, HodDean):
        return redirect(url_for("ho.login"))
    
    status = request.args.get('status', 'Pending Approval')
    base_query = Event.query.filter(
        (Event.approver_1 == current_user.username) | (Event.approver_2 == current_user.username)
    )

    if status == "Pending Approval":
        events = base_query.filter(
            (Event.approval_status == "Pending Approval") |
            (Event.approval_status.like("Awaiting Approval from %"))
        ).all()
    else:
        events = base_query.filter(Event.approval_status == status).all()
    
    return render_template("ho_event_approvals.html", events=events, current_status=status)

@ho_bp.route("/approve_event/<int:event_id>")
@login_required
def approve_event(event_id):
    if not isinstance(current_user, HodDean):
        return redirect(url_for("ho.login"))
    
    event = Event.query.get_or_404(event_id)

    approver_1 = (event.approver_1 or "").strip()
    approver_2 = (event.approver_2 or "").strip()
    current_name = current_user.username

    if current_name not in [approver_1, approver_2]:
        flash("You are not assigned to approve this event.", "error")
        return redirect(url_for("ho.event_approvals", status="Pending Approval"))

    if event.approval_status == "Rejected":
        flash(f"Event '{event.title}' is already rejected.", "info")
        return redirect(url_for("ho.event_approvals", status="Rejected"))

    if event.approval_status == "Approved":
        flash(f"Event '{event.title}' is already fully approved.", "info")
        return redirect(url_for("ho.event_approvals", status="Approved"))

    second_approver_required = bool(approver_2) and approver_2 != approver_1

    final_approved = False
    if not second_approver_required:
        # Only one approver is assigned, so a single approval is enough.
        event.approval_status = "Approved"
        final_approved = True
    else:
        waiting_prefix = "Awaiting Approval from "
        if event.approval_status.startswith(waiting_prefix):
            waiting_for = event.approval_status.replace(waiting_prefix, "", 1).strip()
            if waiting_for != current_name:
                flash("You already approved this event. Waiting for the other approver.", "info")
                return redirect(url_for("ho.event_approvals", status="Pending Approval"))

            event.approval_status = "Approved"
            final_approved = True
        else:
            other_approver = approver_2 if current_name == approver_1 else approver_1
            event.approval_status = f"Awaiting Approval from {other_approver}"

    db.session.commit()
    
    # Notify Coordinator
    from models import Coordinator
    coordinator = Coordinator.query.get(event.created_by)
    if final_approved and coordinator:
        # Note: Coordinator model currently doesn't have email, falling back to name/placeholder
        # or checking User table if they exist there too
        from models import User
        user_backup = User.query.get(event.created_by)
        email = user_backup.email if user_backup else None
        if email:
            send_event_status_email(email, event.title, "Approved")

    if final_approved:
        flash(f"Event '{event.title}' approved successfully!", "success")
    else:
        flash(f"Event '{event.title}' approved by you. Waiting for final approver.", "info")
    return redirect(url_for("ho.event_approvals", status="Pending Approval"))

@ho_bp.route("/reject_event/<int:event_id>")
@login_required
def reject_event(event_id):
    if not isinstance(current_user, HodDean):
        return redirect(url_for("ho.login"))
    
    event = Event.query.get_or_404(event_id)
    event.approval_status = "Rejected"
    db.session.commit()
    
    # Notify Coordinator
    from models import Coordinator
    coordinator = Coordinator.query.get(event.created_by)
    if coordinator:
        from models import User
        user_backup = User.query.get(event.created_by)
        email = user_backup.email if user_backup else None
        if email:
            send_event_status_email(email, event.title, "Rejected")
        
    flash(f"Event '{event.title}' rejected.", "info")
    return redirect(url_for("ho.event_approvals", status="Pending Approval"))

@ho_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("ho.login"))
