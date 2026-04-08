import os
from datetime import datetime, timedelta
from app import app
from extensions import db
from models import Event, Registration, User
from email_utils import send_event_reminder_email

def check_and_send_reminders():
    with app.app_context():
        # Calculate tomorrow's date string (YYYY-MM-DD)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"Checking for events on: {tomorrow}")

        # Find all approved events happening tomorrow
        upcoming_events = Event.query.filter_by(event_date=tomorrow, approval_status="Approved").all()

        if not upcoming_events:
            print("No events scheduled for tomorrow.")
            return

        for event in upcoming_events:
            print(f"Processing event: {event.title}")
            
            # Find all confirmed registrations for this event
            # (Note: depending on the system, we might want to remind even those 
            # whose payment is 'Pending' or 'Under Verification' so they complete it)
            registrations = Registration.query.filter_by(event_id=event.id).all()
            
            for reg in registrations:
                student = User.query.get(reg.student_id)
                if student and student.email:
                    print(f"Sending reminder to: {student.email} for {event.title}")
                    send_event_reminder_email(
                        recipient_email=student.email,
                        student_name=student.name or student.username,
                        event_title=event.title,
                        event_date=event.event_date
                    )

if __name__ == "__main__":
    check_and_send_reminders()
