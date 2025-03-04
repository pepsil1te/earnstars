from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from backend.config import Config

# Initialize Flask app
app = Flask(__name__, 
    static_folder='../static',
    static_url_path='',
    template_folder='../templates'
)
app.config.from_object(Config)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import routes after app initialization
from backend import routes

# Create database tables
with app.app_context():
    db.create_all()
