from calendar import Calendar
import datetime
import random
import uuid
from flask import Flask, request, jsonify
from model import CalendarSource, CalendarSubscriber, User, verificationcode,db
from sqlalchemy.dialects.mysql import mysqlconnector
import mysql.connector
import smtplib
from flasgger import Swagger, swag_from
from email.mime.text import MIMEText
from email_validator import validate_email, EmailNotValidError



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:Fire12345@pinng-dev.cmyva7x3ctnc.ap-southeast-2.rds.amazonaws.com:3306/dev'
db.init_app(app)
Swagger(app)

db.dialect = mysqlconnector.dialect()


app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'DBAPI': mysql.connector.connect}}




@app.route('/search-invitees', methods=['POST'])
@swag_from('search_invitees.yml')
def search_invitees():
    input_data = request.json

    if 'search_phrase' not in input_data:
        return jsonify({'status': 'Error', 'message': 'search_phrase is required'}), 422

    search_phrase = input_data['search_phrase']

   
    matched_users = User.query.filter(User.email.like(f"%{search_phrase}%") |
                                      User.name.like(f"%{search_phrase}%")).all()

    results = {user.email: user.name for user in matched_users}

    return jsonify(results)





# Helper function to validate email format
def validate_email_format(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

# Helper function to generate a random 6-digit verification code
def generate_verification_code():
    return str(random.randint(100000, 999999))

# Temporary storage for verification codes (replace with a database in production)
verification_codes = {}

# Helper function to store the verification code
def store_verification_code(email, code):
    verification_codes[email] = code
    verification_entry = verificationcode(email=email, code=code)
    db.session.add(verification_entry)
    db.session.commit()

# Helper function to retrieve the verification code
def retrieve_verification_code(email):
    verification_entry = verificationcode.query.filter_by(email=email).first()
    return verification_entry.code if verification_entry else None


# Helper function to send verification email
def send_verification_email(email, code):
    sender_email = "asimr7145@gmail.com"
    sender_password = "ztiaydqtcalrhxel"
    subject = "Your Verification Code"
    body = f"Your verification code is: {code}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [email], msg.as_string())

@app.route('/send-2fa-code', methods=['POST'])
@swag_from('send_2fa_code.yml')
def send_2fa_code():
    input_data = request.json

    if 'email' not in input_data:
        return jsonify({'status': 'Error', 'message': 'email is required'}), 422

    email = input_data['email']

    if not validate_email_format(email):
        return jsonify({'status': 'Error', 'message': 'Invalid email format'}), 400

    verification_code = generate_verification_code()
    store_verification_code(email, verification_code)
    send_verification_email(email, verification_code)

    return jsonify({'status': 'Success', 'message': 'Verification code sent successfully'}), 200

@app.route('/confirm-2fa-code', methods=['POST'])
@swag_from('confirm_2fa_code.yml') 
def confirm_2fa_code():
    input_data = request.json

    if 'email' not in input_data or 'code' not in input_data:
        return jsonify({'status': 'Error', 'message': 'email and code are required'}), 422

    email = input_data['email']
    code = input_data['code']
    stored_code = retrieve_verification_code(email)

    if stored_code is None or code != stored_code:
        return jsonify({'status': 'Error', 'message': 'Invalid verification code'}), 401

    return jsonify({'status': 'Success', 'message': 'Account verified successfully'}), 200


@app.route('/user/calendars', methods=['GET'])

@swag_from('link_calendar.yml') 
def get_linked_calendars():
    user_id = request.args.get('user_id')
    
    # Retrieve linked calendars based on user_id
    linked_calendars = retrieve_linked_calendars(user_id)
    
    # Format the response
    metadata = {
        "page": 1,
        "per_page": 20,
        "page_count": 20,
        "total_count": len(linked_calendars),
        "links": [
            {"self": f"/user/calendars?page=1&per_page=20"},
            {"first": f"/user/calendars?page=1&per_page=20"},
            {"previous": ""},
            {"next": f"/user/calendars?page=2&per_page=20"},
            {"last": f"/user/calendars?page=2&per_page=20"}
        ]
    }

    records = [{"id": calendar.id, "name": calendar.display_name, "type": calendar.source_type_id} for calendar in linked_calendars]

    response = {
        "_metadata": metadata,
        "records": records
    }

    return jsonify(response)

# Helper function to retrieve linked calendars based on user ID
def retrieve_linked_calendars(user_id):
    linked_calendars = CalendarSource.query.filter_by(owner_id=user_id).all()
    return linked_calendars


# Create API endpoint for unlinking a calendar
@app.route('/user/calendars/unlink', methods=['POST'])

@swag_from('unlink_calendar.yml')  # Specify the path to the YAML file for this API
def unlink_calendar():
    input_data = request.json
    
    if 'user_id' not in input_data or 'calendar_id' not in input_data:
        return jsonify({'status': 'Error', 'message': 'user_id and calendar_id are required'}), 422

    user_id = input_data['user_id']
    calendar_id = input_data['calendar_id']

    # Delete the calendar source based on user_id and calendar_id
    delete_calendar_source(user_id, calendar_id)

    return jsonify({'status': 'Success', 'message': 'Calendar unlinked successfully'}), 200

# Helper function to delete a calendar source
def delete_calendar_source(user_id, calendar_id):
    calendar_source = CalendarSource.query.filter_by(owner_id=user_id, id=calendar_id).first()
    if calendar_source:
        db.session.delete(calendar_source)
        db.session.commit()

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
        # Create a new entry in the calendar_subscriber table
        new_subscription = CalendarSubscriber(
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



@app.route('/subscribe', methods=['POST'])
def subscribe_to_calendar():
    input_data = request.json

    if 'user_id' not in input_data or 'calendar_id' not in input_data:
        return jsonify({'status': 'Error', 'message': 'user_id and calendar_id are required'}), 422

    user_id = input_data['user_id']
    calendar_id = input_data['calendar_id']

    # Subscribe the user to the specified calendar
    subscribe_result = subscribe_user_to_calendar(user_id, calendar_id)

    if subscribe_result:
        return jsonify({'status': 'Success', 'message': 'Subscribed to the calendar'}), 200
    else:
        return jsonify({'status': 'Error', 'message': 'Failed to subscribe to the calendar'}), 500


def unsubscribe_user_from_calendar(user_id, calendar_id):
    try:
        # Find and delete the subscription entry
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

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe_from_calendar():
    input_data = request.json

    if 'user_id' not in input_data or 'calendar_id' not in input_data:
        return jsonify({'status': 'Error', 'message': 'user_id and calendar_id are required'}), 422

    user_id = input_data['user_id']
    calendar_id = input_data['calendar_id']

    # Unsubscribe the user from the specified calendar
    unsubscribe_result = unsubscribe_user_from_calendar(user_id, calendar_id)

    if unsubscribe_result:
        return jsonify({'status': 'Success', 'message': 'Unsubscribed from the calendar'}), 200
    else:
        return jsonify({'status': 'Error', 'message': 'Failed to unsubscribe from the calendar'}), 500


@app.route('/user/subscriptions', methods=['GET'])
def list_subscriptions():
    user_id = request.args.get('user_id')
    
    # Retrieve the subscriptions for the user
    subscriptions = retrieve_subscriptions(user_id)
    
    # Format the response
    response = {
        "user_id": user_id,
        "subscriptions": subscriptions
    }

    return jsonify(response)

@app.route('/user/subscriptions/authorized', methods=['GET'])
def list_subscriptions_authorized():
    user_id = request.args.get('user_id')

    # Retrieve the subscriptions for the authorized user
    subscriptions = retrieve_subscriptions(user_id)

    # Format the response
    response = {
        "user_id": user_id,
        "subscriptions": subscriptions
    }

    return jsonify(response)






if __name__ == '__main__':
    app.run()


