import random
from flask import Flask, request, jsonify
from model import User, verificationcode,db
from sqlalchemy.dialects.mysql import mysqlconnector
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email_validator import validate_email, EmailNotValidError



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:Fire12345@pinng-dev.cmyva7x3ctnc.ap-southeast-2.rds.amazonaws.com:3306/dev'
db.init_app(app)


db.dialect = mysqlconnector.dialect()


app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'DBAPI': mysql.connector.connect}}

@app.route('/search-invitees', methods=['POST'])
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


if __name__ == '__main__':
    app.run()


