from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class LinkedCalendar(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String
    (100), nullable=False)
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

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), nullable=False)
    calendar_id = db.Column(db.String(36), nullable=False)
    is_subscribed = db.Column(db.Boolean, nullable=False, default=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CalendarSharedUser(db.Model):
    __tablename__ = 'calendar_shared_user'
    id = db.Column(db.String(36), primary_key=True)
    owner_id = db.Column(db.String(36))
    access_level = db.Column(db.Enum('booking_only', 'availability_only', 'limited_details', 'full_details'))


    user_id = db.Column(db.String(36), nullable=False)
    calendar_id = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)

class CalendarSharedUserInvite(Base):
    __tablename__ = 'calendar_shared_user_invite'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)


    owner_id = Column(VARCHAR(36), nullable=False)
    user_id = Column(VARCHAR(36), nullable=False)
    calendar_id = Column(VARCHAR(36), nullable=False)
    access_level = Column(Enum('booking_only', 'availability_only', 'limited_details', 'full_details'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Calendar(db.Model):
    __tablename__ = 'calendar'

    id = db.Column(db.String(36), primary_key=True)
    owner_id = db.Column(db.String(36))
    name = db.Column(db.String(250))
    alias = db.Column(db.String(250))
    location = db.Column(db.String(250))
    timezone = db.Column(db.String(250))
    visibility_status = db.Column(db.String(8))
    calendar_type_id = db.Column(db.Integer)
    first_day_of_week = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)




    # Add more fields as needed
class verificationcode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(6), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'
