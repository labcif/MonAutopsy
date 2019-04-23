import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage



port = 465 #SSL

#Secure SSL Context
context = ssl.create_default_context()

html = """<h1 style="text-align: center;"><strong>Periodic Report</strong></h1>
<p>&nbsp;</p>
<h2><strong>Par&acirc;metros:</strong></h2>
<ul>
<li><strong>CPU Usage</strong>:
<ul>
<li>Minimum: 10%</li>
<li>Maximum: 95%</li>
</ul>
</li>
<li><strong>Virtual Memory Usage</strong>:
<ul>
<li>Minimum: 10%</li>
<li>Maximum: 95%</li>
</ul>
</li>
</ul>
<p>&nbsp;</p>
<h2><strong>Statistics:</strong></h2>
<p><strong>CPU:</strong></p>
<p><strong><img src="cid:cpu" alt="" width="836" height="526" /></strong></p>
<p>&nbsp;</p>
<p><strong>IO:</strong></p>
<p><strong><img src="cid:io" alt="" width="836" height="526" /></strong></p>
<p>&nbsp;</p>
<p><strong>Memory:</strong></p>
<p><strong><img src="cid:memory" alt="" width="836" height="526" /></strong></p>
<p>&nbsp;</p>
<p>&nbsp;</p>
<p>&nbsp;</p>
<p>&nbsp;</p>
<h2><strong>Program Execution:</strong></h2>
<p><img src="cid:status" alt="" width="1920" height="1080" /></p>
<p>&nbsp;</p>"""


message = MIMEMultipart("related")
message["Subject"] = "Periodic Report"
message["From"] = "noreply@MonAutopsy.pt"
msgAlternative = MIMEMultipart('alternative')
message.attach(msgAlternative)

part1 = MIMEText(html, "html")
msgAlternative.attach(part1)

fp = open("cpu_graph.jpg", "rb")
msgImage = MIMEImage(fp.read())
msgImage.add_header('Content-ID', '<cpu>')
message.attach(msgImage)


fp = open("io_graph.jpg", "rb")
msgImage = MIMEImage(fp.read())
msgImage.add_header('Content-ID', '<io>')
message.attach(msgImage)


fp = open("memory_graph.jpg", "rb")
msgImage = MIMEImage(fp.read())
msgImage.add_header('Content-ID', '<memory>')
message.attach(msgImage)


fp = open("screenshot.jpg", "rb")
msgImage = MIMEImage(fp.read())
msgImage.add_header('Content-ID', '<status>')
message.attach(msgImage)

def send_notif(SMTPServer, senderEmail, receiverEmail, password):
	with smtplib.SMTP_SSL(SMTPServer, port, context=context) as server:
		server.login(senderEmail, password)
		server.sendmail(senderEmail, receiverEmail, message.as_string())