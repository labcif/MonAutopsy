import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

port = 465 #SSL

#Secure SSL Context
context = ssl.create_default_context()

message = """\
Subject: Hi there

This message is sent from Python."""

def send_notif(email, password):
	with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
		server.login(email, password)
		server.sendmail("noreply@MonAutopsy.pt", email, message)