import requests
import logging
import hashlib, binascii, os
import pyrebase
import uuid, json
import jwt
import datetime
from functools import wraps

from flask import Flask, jsonify
from flask import request
from send_email import publish

from werkzeug.routing import BaseConverter

# Initialize the Flask Application
application = Flask(__name__)

# App Config for Secret Key
pyConfig = {}
with open('config.json', 'r') as outfile:
    pyConfig = json.load(outfile)
application.config['SECRET_KEY'] = pyConfig["secret_key"]

# Decorator for token authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'error': 'Token is missing'}), 403

        try:
            data = jwt.decode(token, application.config['SECRET_KEY'])
            email = data['user']

            all_users = db.child("users").get()
            for userKey in all_users.each():
                if userKey.val()["email"] == email and userKey.val()["token"] == token:
                    return f(*args, **kwargs)
            return jsonify({'error': 'Your token does not match with our records'}), 403
        except Exception as e:
            error(str(e))
            return jsonify({'error': 'Token is invalid'}), 403

        return f(*args, **kwargs)
    return decorated

# Creating a generic log method for short writes
def log(message):
    return application.logger.info(message)

# Creating a generic log method for errors
def error(message):
    return application.logger.error(message)

# Initialize Firebase
def initDB():
    config = pyConfig["firebaseConfig"]
    log(json.dumps(config))

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    auth = firebase.auth()
    return db

db = initDB()

# Implement a RegexConvertor regex based routing in Flask
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

application.url_map.converters['regex'] = RegexConverter

# Set the logging rules for gunicorn
if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    application.logger.handlers = gunicorn_logger.handlers
    application.logger.setLevel(gunicorn_logger.level)

# Hash password for storing
def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

# Verify password after retrieving
def verify_password(stored_password, provided_password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

# Check if the user already exists in the users table
def check_if_user_already_exists_in_users(email):
    all_users = db.child("users").get()
    for userKey in all_users.each():
        if userKey.val()["email"] == email:
            return True
    return False

# Check if the user already exists in the auth_tokens table
def check_if_user_already_exists_in_auth_tokens(given_email):
    all_tokens = db.child("auth_tokens").get()
    if all_tokens.val():
        for gKey in all_tokens.each():
            for token, email in gKey.val().items():
                if email == given_email:
                    return True
    return False

# Create a user who can access this DB
@application.route("/create_account", methods = ["POST"])
def create_account():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not name:
        name = ''

    if not email:
        return jsonify({"error": "Email cannot be empty"})

    if not password:
        return jsonify({"error": "Password cannot be empty"})

    if not check_if_user_already_exists_in_users(email):
        data = {
            "name": name,
            "email": email,
            "password": hash_password(password),
            "active": False
        }

        try:
            results = db.child("users").push(data)
            token = str(uuid.uuid1())
            url = "http://localhost:8000/verify_account/" + token 
            body = """\
            <html>
            <body>
                <p>Hi,<br>
                Please verify your email in order to start using AranciaDB<br>
                <a href='""" + url + """'>"""+ url +"""</a> 
                </p>
            </body>
            </html>
            """
            subject = "Verify your account with AranciaDB"

            try:
                publish(email, subject, body)
                token_data = {token: email}
                try:
                    response = db.child("auth_tokens").push(token_data)
                    return jsonify({"success": "Created the DB account. Please verify the email to access it"})
                except Exception as e:
                    error(str(e))
                    return jsonify({"error": str(e)})
            except Exception as e:
                error(str(e))
                return jsonify({"error": str(e)})
        except Exception as e:
            error(str(e))
            return jsonify({"error": str(e)})
    return jsonify({"error": "This email already exists, please select a new email address"})

# Update the active status of the user
def updateUser(email):
    all_users = db.child("users").get()
    for userKey in all_users.each():
        if userKey.val()["email"] == email:
            db.child("users").child(userKey.key()).update({"active": True})

@application.route('/verify_account/<regex("[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"):uid>')
def verify_account(uid):
    all_tokens = db.child("auth_tokens").get()
    if all_tokens.val():
        for gKey in all_tokens.each():
            for token, email in gKey.val().items():
                if token == uid: 
                    updateUser(email)
                    db.child("auth_tokens").child(gKey.key()).remove()       
                    return jsonify({"success": "Your email address is successfully verified. You can now start exploring AranciaDB"})
    return jsonify({"error": "Invalid token."})


@application.route('/resend_token', methods = ["POST"])
def resend_token():
    email = request.form.get("email")
    password = request.form.get("password")

    if not check_if_user_already_exists_in_auth_tokens(email):
        all_users = db.child("users").get()
        for userKey in all_users.each():
            if userKey.val()["email"] == email and verify_password(userKey.val()["password"], password):
                token = str(uuid.uuid1())
                token_data = {token: email}
                url = "http://localhost:8000/verify_account/" + token 
                body = """\
                <html>
                <body>
                    <p>Hi,<br>
                    Please verify your email in order to start using AranciaDB<br>
                    <a href='""" + url + """'>"""+ url +"""</a> 
                    </p>
                </body>
                </html>
                """
                subject = "Verify your account with AranciaDB"
                try: 
                    publish(email, subject, body)
                    try:
                        response = db.child("auth_tokens").push(token_data)
                        return jsonify({"success": "New verification link has been sent to your email address."})
                    except Exception as e:
                        error(str(e))
                        return jsonify({"error": str(e)})
                except Exception as e:
                    error(str(e))
                    return jsonify({"error": str(e)})
        return jsonify({"error": "Invalid Email/Password."})
    return jsonify({"error": "You cannot generate duplicate tokens."})


def check_if_email_password_match(email, password):
    all_users = db.child("users").get()
    for userKey in all_users.each():
        if userKey.val()["email"] == email and verify_password(userKey.val()["password"], password):
            if not userKey.val()["active"]:
                return "User is not active"
            return "Success"
    return "Invalid Email/Password."

@application.route("/create_access_tokens", methods = ["POST"])
def create_access_tokens():
    email = request.form.get("email")
    password = request.form.get("password")

    result = check_if_email_password_match(email, password)
    if result == "Success":
        token = jwt.encode({'user': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes = 30)}, application.config['SECRET_KEY'])

        all_users = db.child("users").get()
        for userKey in all_users.each():
            if userKey.val()["email"] == email:
                db.child("users").child(userKey.key()).update({"token": token.decode('utf-8')})

        return jsonify({"token": token.decode('utf-8')})
    else:
        return jsonify({"error": result})

@application.route("/unprotected")
def unprotected():
    return jsonify({"message": "Anyone can access this route"})

@application.route("/protected")
@token_required
def protected():
    return jsonify({"message": "Available for only those who have valid tokens"})

@application.route("/")
def hello():
    application.logger.info(request.headers)
    return 'Hello, World!'

if __name__ == "__main__":
    application.run(host='0.0.0.0')