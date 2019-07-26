import smtplib, ssl, os, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import Celery

app = Celery("send_email_task", broker = "amqp://admin:password@localhost")

@app.task
def publish(receiver_email, subject, body):

    config = {}
    with open('config.json', 'r') as outfile:
        config = json.load(outfile)

    sender_email = config["mailConfig"]["email"]
    receiver_email = receiver_email
    password = config["mailConfig"]["password"]

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Turn these into html MIMEText objects
    part = MIMEText(body, "html")

    # Add HTML parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )