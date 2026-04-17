import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Secret Key
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "fallback_secret_key_12345")

# ✅ DATABASE CONFIGURATION (PostgreSQL for production, SQLite for local)
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # Render provides DATABASE_URL in postgresql:// format
    # SQLAlchemy 2.0+ requires postgresql+psycopg2://
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # Fallback to SQLite for local development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Email Configuration
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "True") == "True"
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME")

# Initialize Extensions
from extensions import db, bcrypt, login_manager, mail

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
mail.init_app(app)

# ✅ SAFE DB CREATE (avoid crash on startup)
if os.environ.get("RENDER") != "1":
    with app.app_context():
        db.create_all()
        from seeding_utils import ensure_demo_accounts
        ensure_demo_accounts()

login_manager.login_view = "index"
login_manager.login_message_category = "info"

# Import Blueprints
from stu.routes import stu_bp
from hod.routes import hod_bp
from clu.routes import clu_bp
from adm.routes import adm_bp
from auth_routes import auth_bp
from ho.routes import ho_bp

# Register Blueprints
app.register_blueprint(stu_bp, url_prefix="/stu")
app.register_blueprint(hod_bp, url_prefix="/hod")
app.register_blueprint(clu_bp, url_prefix="/clu")
app.register_blueprint(adm_bp, url_prefix="/adm")
app.register_blueprint(auth_bp)
app.register_blueprint(ho_bp, url_prefix="/ho")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()