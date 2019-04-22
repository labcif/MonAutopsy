import smtplib, ssl
from senderEmail.mime.text import MIMEText
from senderEmail.mime.multipart import MIMEMultipart
from xhtml2pdf import pisa

# Define your data
sourceHtml = "report.html"
outputFilename = "report.pdf"

# Utility function
def convertHtmlToPdf(sourceHtml, outputFilename):
    # open output file for writing (truncated binary)
    resultFile = open(outputFilename, "w+b")

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(open(sourceHtml).read(), resultFile)

    # close output file
    resultFile.close()

    # return True on success and False on errors
    return pisaStatus.err



port = 465 #SSL

#Secure SSL Context
context = ssl.create_default_context()

#message = """\
#Subject: Hi there
#
#This message is sent from Python."""

file = open("report.html")
html = file.read()
message = MIMEMultipart("alternative")
message["Subject"] = "Periodic Report"

#message["From"] = "noreply@MonAutopsy.pt"

part1 = MIMEText(html, "html")
message.attach(part1)

def send_notif(SMTPServer, senderEmail, receiverEmail, password):
	convertHtmlToPdf(sourceHtml, outputFilename)

	#message["To"] = receiverEmail

	with smtplib.SMTP_SSL(SMTPServer, port, context=context) as server:
		server.login(senderEmail, password)
		server.sendmail(senderEmail, receiverEmail, message.as_string())