import requests
import logging
import hashlib, binascii, os
import pyrebase
import uuid, json

from flask import Flask, jsonify
from flask import request
from send_email import publish

# Initialize the Flask Application
application = Flask(__name__)

# Initialize Firebase
def initDB():
    pyConfig = {}
    with open('config.json', 'r') as outfile:
        pyConfig = json.load(outfile)

    config = pyConfig["firebaseConfig"]
    log(json.dumps(config))

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    auth = firebase.auth()
    return db

# Set the logging rules for gunicorn
if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    application.logger.handlers = gunicorn_logger.handlers
    application.logger.setLevel(gunicorn_logger.level)

# Creating a generic log method for short writes
def log(message):
    return application.logger.info(message)

# Creating a generic log method for errors
def error(message):
    return application.logger.error(message)

# Hash password for storing
def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

# Verify password after retreiving
def verify_password(stored_password, provided_password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


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
    
    data = {
        "name": name,
        "email": email,
        "password": hash_password(password),
        "active": False
    }

    db = initDB()

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
    except Excetion as e:
        error(str(e))
        return jsonify({"error": str(e)})

@application.route("/")
def hello():
    application.logger.info(request.headers)
    return 'Hello, World!'

if __name__ == "__main__":
    application.run(host='0.0.0.0')