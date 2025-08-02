
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy object initialize
db = SQLAlchemy()

# User table define 
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)  
    otp = db.Column(db.String(6),nullable=True) 

    def __repr__(self):
        return f'<User {self.email}>'
