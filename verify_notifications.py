from app import app
from extensions import db
from models import User, Event, Registration
from datetime import datetime, timedelta
import remind_events

# Better to just copy the logic or import correctly
import sys
import os

# To import from remind_events
import remind_events

def verify_system():
    with app.app_context():
        print("--- Verification Setup ---")
        
        # 1. Create a test coordinator
        coord = User.query.filter_by(username="test_coord").first()
        if not coord:
            User.create_user(
                username="test_coord",
                password="password123",
                role="clu",
                email="itismeyoursfriend@gmail.com", # Use a real email you control for testing if possible
                club_name="Test Club"
            )
            coord = User.query.filter_by(username="test_coord").first()
        
        # 2. Create an event happening tomorrow
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        event = Event.query.filter_by(title="Test Tomorrow Event").first()
        if not event:
            event_data = {
                "title": "Test Tomorrow Event",
                "club_name": "Test Club",
                "event_date": tomorrow,
                "approval_status": "Approved",
                "created_by": coord.id
            }
            event = Event.create_event(event_data)
            print(f"Created event '{event.title}' for tomorrow ({tomorrow})")
        
        # 3. Create a test student
        student = User.query.filter_by(username="test_student").first()
        if not student:
            User.create_user(
                username="test_student",
                password="password123",
                role="stu",
                email="itismeyoursfriend@gmail.com", # Same email for convenience
                name="Test Student"
            )
            student = User.query.filter_by(username="test_student").first()
        
        # 4. Register student for event
        reg = Registration.query.filter_by(event_id=event.id, student_id=student.id).first()
        if not reg:
            reg = Registration(event_id=event.id, student_id=student.id, payment_status="Confirmed")
            db.session.add(reg)
            db.session.commit()
            print(f"Registered student '{student.username}' for event '{event.title}'")

        print("\n--- Testing Reminder Script ---")
        remind_events.check_and_send_reminders()
        
        print("\n--- Verification Complete ---")

if __name__ == "__main__":
    verify_system()
