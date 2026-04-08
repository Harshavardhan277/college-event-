from app import app
from extensions import db
from models import User

def seed():
    with app.app_context():
        # Drop and recreate tables to apply schema changes
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        
        # Check if users already exist
        if not User.query.filter_by(username="club_hero").first():
            print("Creating test coordinator: club_hero")
            User.create_user(
                username="club_hero",
                password="password123",
                role="clu",
                email="club@example.com",
                club_name="Hero Club"
            )
            
        if not User.query.filter_by(username="admin").first():
            print("Creating test admin: admin")
            User.create_user(
                username="admin",
                password="adminpassword",
                role="adm",
                email="admin@example.com"
            )

        if not User.query.filter_by(username="student").first():
            print("Creating test student: student")
            User.create_user(
                username="student",
                password="studentpassword",
                role="stu",
                email="student@example.com",
                name="Test Student"
            )
        
        from models import Admin, Club, Coordinator
        if not Admin.query.filter_by(username="admin").first():
            print("Creating System Admin: admin")
            Admin.create_admin(
                username="admin",
                password="adminpassword",
                name="System Administrator"
            )
        
        if not Club.query.filter_by(club_name="Tech Innovations").first():
            print("Creating sample club: Tech Innovations")
            club = Club(club_name="Tech Innovations", description="Advancing technology and innovation in college.")
            db.session.add(club)
            db.session.commit()

        if not Coordinator.query.filter_by(username="coordinator").first():
            print("Creating test coordinator: coordinator")
            Coordinator.create_coordinator(
                username="coordinator",
                password="coordinatorpassword",
                name="Club Lead",
                club_name="Tech Innovations"
            )
            
        from models import HodDean
        if not HodDean.query.filter_by(username="hod").first():
            print("Creating test HOD: Dr. Pavan Kumar")
            HodDean.create_hod(
                username="hod",
                password="password123",
                name="Dr. Pavan Kumar",
                department="CSE",
                role="HOD"
            )

        if not Club.query.filter_by(club_name="GeeksforGeeks").first():
            print("Creating sample club: GeeksforGeeks")
            club = Club(club_name="GeeksforGeeks", description="Data structures and Algorithms coding club")
            db.session.add(club)
            db.session.commit()

        if not Coordinator.query.filter_by(username="gfg01").first():
            print("Creating test coordinator: gfg01")
            Coordinator.create_coordinator(
                username="gfg01",
                password="password123",
                name="GFG Lead",
                club_name="GeeksforGeeks"
            )
            User.create_user(
                username="gfg01",
                password="password123",
                role="clu",
                email="gfg@example.com",
                club_name="GeeksforGeeks"
            )

        gfg_user = User.query.filter_by(username="gfg01").first()
        from models import Event
        from datetime import datetime
        if gfg_user and not Event.query.filter_by(title="ALGORITHMIS").first():
            print("Creating sample event: ALGORITHMIS")
            event_data = {
                "title": "ALGORITHMIS",
                "club_name": "GeeksforGeeks",
                "description": "Coding competition covering DSA and competitive programming.",
                "event_date": "2026-04-25",
                "fee": "100",
                "team_size": 1,
                "no_of_teams": 100,
                "max_participants": 100,
                "created_by": gfg_user.id,
                "created_at": datetime.now()
            }
            Event.create_event(event_data)
            
            # Auto-approve it so it shows up
            new_event = Event.query.filter_by(title="ALGORITHMIS").first()
            if new_event:
                new_event.approval_status = "Approved"
                db.session.commit()

        print("Database seeded successfully!")

if __name__ == "__main__":
    seed()
