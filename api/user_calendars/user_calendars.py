from model import CalendarSource
from flask import jsonify
from model import db

def retrieve_linked_calendars(user_id):
    linked_calendars = CalendarSource.query.filter_by(owner_id=user_id).all()
    return linked_calendars


def delete_calendar_source(user_id, calendar_id):
    calendar_source = CalendarSource.query.filter_by(owner_id=user_id, id=calendar_id).first()
    if calendar_source:
        db.session.delete(calendar_source)
        db.session.commit()
