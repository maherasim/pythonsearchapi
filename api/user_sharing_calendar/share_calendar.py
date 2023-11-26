# api/user_calendars/user_calendars.py
from model import db, Calendar, CalendarSharedUser, CalendarSubscriber, User
import datetime
import uuid

def retrieve_calendar_by_id(calendar_id):
    calendar = Calendar.query.get(calendar_id)
    return calendar

def retrieve_subscriptions(user_id):
    subscriptions = CalendarSubscriber.query.filter_by(user_id=user_id).all()
    subscription_details = []

    for subscription in subscriptions:
        subscription_details.append({
            "subscription_id": subscription.id,
            "calendar_id": subscription.calendar_id,
            "is_subscribed": subscription.is_subscribed,
            "created_at": subscription.created_at,
            "updated_at": subscription.updated_at
        })

    return subscription_details

def generate_unique_id():
    return str(uuid.uuid4())

def subscribe_user_to_calendar(user_id, calendar_id):
    try:
        subscription_id = str(uuid.uuid4())

        new_subscription = CalendarSubscriber(
            id=subscription_id,
            user_id=user_id,
            calendar_id=calendar_id,
            is_subscribed=True,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        db.session.add(new_subscription)
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        db.session.rollback()
        return False

def unsubscribe_user_from_calendar(user_id, calendar_id):
    try:
        subscription_to_delete = CalendarSubscriber.query.filter_by(user_id=user_id, calendar_id=calendar_id).first()
        if subscription_to_delete:
            db.session.delete(subscription_to_delete)
            db.session.commit()
            return True
        else:
            return False
    except Exception as e:
        print(e)
        db.session.rollback()
        return False

def get_shared_calendars_by_me(user_id):
    try:
        shared_calendars = db.session.query(Calendar).join(
            CalendarSharedUser,
            CalendarSharedUser.calendar_id == Calendar.id
        ).filter(CalendarSharedUser.user_id == user_id).all()

        response = [{'id': calendar.id, 'name': calendar.name} for calendar in shared_calendars]

        return response
    except Exception as e:
        return {'error': str(e)}, 500

def update_sharing_level(user_id, calendar_id, new_access_level):
    try:
        if user_id is None:
            return {'error': 'User is not authenticated.'}, 401

        shared_calendar_entry = CalendarSharedUser.query.filter_by(
            owner_id=user_id,
            calendar_id=calendar_id
        ).first()

        if shared_calendar_entry:
            shared_calendar_entry.access_level = new_access_level
            db.session.commit()
            return {'message': 'Sharing level updated successfully.'}, 200
        else:
            return {'error': 'Calendar share not found.'}, 404

    except Exception as e:
        return {'error': str(e)}, 500

def get_my_shared_calendars(page, per_page, user_id, search_phrase):
    try:
        offset = (page - 1) * per_page

        shared_calendars = db.session.query(CalendarSharedUser, User, Calendar).join(
            User,
            User.id == CalendarSharedUser.user_id
        ).join(
            Calendar,
            Calendar.id == CalendarSharedUser.calendar_id
        ).filter(
            CalendarSharedUser.owner_id == user_id,
            (Calendar.name.like(f"%{search_phrase}%") | User.name.like(f"%{search_phrase}%"))
        ).offset(offset).limit(per_page).all()

        response = {
            "page": page,
            "per_page": per_page,
            "total_count": len(shared_calendars),
            "shared_calendars": [
                {
                    "share_id": shared_user.id,
                    "shared_with_user": user.name,
                    "calendar_id": calendar.id,
                    "calendar_name": calendar.name,
                    "access_level": shared_user.access_level,
                }
                for shared_user, user, calendar in shared_calendars
            ]
        }

        return response, 200

    except Exception as e:
        return {'error': str(e)}, 500

def remove_calendar_share(user_id, calendar_id):
    try:
        shared_calendar_entry = CalendarSharedUser.query.filter_by(
            user_id=user_id,
            calendar_id=calendar_id
        ).first()

        if shared_calendar_entry:
            db.session.delete(shared_calendar_entry)
            db.session.commit()
            return {'message': 'Calendar share removed successfully.'}, 200
        else:
            return {'error': 'Calendar share not found.'}, 404

    except Exception as e:
        return {'error': str(e)}, 500
