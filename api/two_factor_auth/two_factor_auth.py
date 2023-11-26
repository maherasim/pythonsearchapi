# api/two_factor_auth/two_factor_auth.py

from flask import jsonify
from model import User, verificationcode, db
import random
from email.mime.text import MIMEText
from email_validator import validate_email, EmailNotValidError
import smtplib

def validate_email_format(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def generate_verification_code():
    return str(random.randint(100000, 999999))

def store_verification_code(email, code):
    verification_entry = verificationcode(email=email, code=code)
    db.session.add(verification_entry)
    db.session.commit()

def retrieve_verification_code(email):
    verification_entry = verificationcode.query.filter_by(email=email).first()
    return verification_entry.code if verification_entry else None

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

def send_2fa_code(email):
    if not validate_email_format(email):
        return jsonify({'status': 'Error', 'message': 'Invalid email format'}), 400

    verification_code = generate_verification_code()
    store_verification_code(email, verification_code)
    send_verification_email(email, verification_code)

    return jsonify({'status': 'Success', 'message': 'Verification code sent successfully'}), 200

def confirm_2fa_code(email, code):
    stored_code = retrieve_verification_code(email)

    if stored_code is None or code != stored_code:
        return jsonify({'status': 'Error', 'message': 'Invalid verification code'}), 401

    return jsonify({'status': 'Success', 'message': 'Account verified successfully'}), 200
