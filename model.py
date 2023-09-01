from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class LinkedCalendar(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class CalendarSourceType(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255))
    display_name = db.Column(db.String(255))

    def __repr__(self):
        return f'<CalendarSourceType {self.name}>'

class CalendarSource(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    owner_id = db.Column(db.String(36))
    source_type_id = db.Column(db.String(36))
    display_name = db.Column(db.String(250))
    config = db.Column(db.JSON)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<CalendarSource {self.display_name}>'

class CalendarSubscriber(db.Model):
    __tablename__ = 'calendar_subscriber'

    id = db.Column(db.String(36), primary_key=True,autoincrement=True)
    user_id = db.Column(db.String(36), nullable=False)
    calendar_id = db.Column(db.String(36), nullable=False)
    is_subscribed = db.Column(db.Boolean, nullable=False, default=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)







    # Add more fields as needed
class verificationcode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(6), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'
