import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import math

port = 465  # SSL

# Secure SSL Context
context = ssl.create_default_context()

def createMemMinNotif(config, memoryValue):
	html_memory_notif = """<style>.center {{
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;
}}</style>
<h1 style="text-align: center; font-size: 50px;"><strong>Memory Notification</strong></h1>
<p>&nbsp;</p>
<h2>WARNING:</h2>
<p style="padding-left: 60px;">Memory usage is lower than minimum value established ({}MB).</p>
<p style="padding-left: 60px;">Current memory value is&nbsp;&asymp; <strong>{}MB</strong></p>
<img src="cid:memory_usage" alt="" style="display: block; margin-left: auto; margin-right: auto; width:50%"/>""".format(config["MEMORY"]["min"], math.floor(memoryValue))

	message = MIMEMultipart("related")
	message["Subject"] = "Memory notification"
	message["From"] = "noreply@MonAutopsy.pt"
	msgAlternative = MIMEMultipart('alternative')
	message.attach(msgAlternative)

	part1 = MIMEText(html_memory_notif, "html")
	msgAlternative.attach(part1)

	fp = open("memory_notif_min.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<memory_usage>')
	message.attach(msgImage)
	fp.close()

	return message


def createMemMaxNotif(config, memoryValue):
	html_memory_notif = """<style>.center {{
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;
}}</style>
<h1 style="text-align: center; font-size: 50px;"><strong>Memory Notification</strong></h1>
<p>&nbsp;</p>
<h2>WARNING:</h2>
<p style="padding-left: 60px;">Memory usage is higher than maximum value established ({}MB).</p>
<p style="padding-left: 60px;">Current memory value is&nbsp;&asymp; <strong>{}MB</strong></p>
<img src="cid:memory_usage" alt="" style="display: block; margin-left: auto; margin-right: auto; width:50%"/>""".format(config["MEMORY"]["max"], math.floor(memoryValue))

	message = MIMEMultipart("related")
	message["Subject"] = "Memory notification"
	message["From"] = "noreply@MonAutopsy.pt"
	msgAlternative = MIMEMultipart('alternative')
	message.attach(msgAlternative)

	part1 = MIMEText(html_memory_notif, "html")
	msgAlternative.attach(part1)

	fp = open("memory_notif_max.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<memory_usage>')
	message.attach(msgImage)
	fp.close()

	return message

def createCpuMinNotif(config, cpuValue):
	html_cpu_notif = """<style>.center {{
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;
}}</style>
<h1 style="text-align: center; font-size: 50px;"><strong>CPU Notification</strong></h1>
<p>&nbsp;</p>
<h2>WARNING:</h2>
<p style="padding-left: 60px;">CPU usage is lower than minimum value established ({}%).</p>
<p style="padding-left: 60px;">Current CPU value is&nbsp;&asymp; <strong>{}%</strong></p>
<img src="cid:cpu_usage" alt="" style="display: block; margin-left: auto; margin-right: auto; width:50%"/>""".format(config["CPU USAGE"]["min"], cpuValue)

	message = MIMEMultipart("related")
	message["Subject"] = "CPU notification"
	message["From"] = "noreply@MonAutopsy.pt"
	msgAlternative = MIMEMultipart('alternative')
	message.attach(msgAlternative)

	part1 = MIMEText(html_cpu_notif, "html")
	msgAlternative.attach(part1)

	fp = open("cpu_notif_min.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_usage>')
	message.attach(msgImage)
	fp.close()

	return message


def createCpuMaxNotif(config, cpuValue):
	html_cpu_notif = """<style>.center {{
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;
}}</style>
<h1 style="text-align: center; font-size: 50px;"><strong>CPU Notification</strong></h1>
<p>&nbsp;</p>
<h2>WARNING:</h2>
<p style="padding-left: 60px;">CPU usage is lower than maximum value established ({}%).</p>
<p style="padding-left: 60px;">Current CPU value is&nbsp;&asymp; <strong>{}%</strong></p>
<img src="cid:cpu_usage" alt="" style="display: block; margin-left: auto; margin-right: auto; width:50%"/>""".format(config["CPU USAGE"]["max"], cpuValue)

	message = MIMEMultipart("related")
	message["Subject"] = "CPU notification"
	message["From"] = "noreply@MonAutopsy.pt"
	msgAlternative = MIMEMultipart('alternative')
	message.attach(msgAlternative)

	part1 = MIMEText(html_cpu_notif, "html")
	msgAlternative.attach(part1)

	fp = open("cpu_notif_max.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_usage>')
	message.attach(msgImage)
	fp.close()

	return message

def createPeriodicReport(config):

	html_periodic = """
	<style>
	.floatedTable {{
  		float:left;
	}}
	.inlineTable {{
  		display: inline-block;
	}}
	h1 {{
		font-size: 50px;
	}}
	
	table {{
		font-family: arial, sans-serif;
		border-collapse: collapse;
	}}
	
	td, th {{
		border: 1px solid #dddddd;
		text-align: left;
		padding: 8px;
	}}
	</style>
	<h1 style="text-align: center; font-size: 50px;"><strong>Periodic Report</strong></h1>
	<p>&nbsp;</p>
	<h2>Configurations:</h2>
	<table style="display: inline-block; font-family: arial, sans-serif; border-collapse: collapse;">
		<thead>
			<tr>
				<th style="font-weight: 800; border: 1px solid #dddddd; text-align: left; padding: 8px;">CPU/Memory configuration</th>
				<th style="font-weight: bolder; border: 1px solid #dddddd; text-align: left; padding: 8px;">Minimum</th>
				<th style="font-weight: bolder; border: 1px solid #dddddd; text-align: left; padding: 8px;">Maximum</th>
			</tr>
		</thead>
			<tbody>
				<tr>
				<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">CPU usage</td>
				<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">{} %</td>
				<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">{} %</td>
			</tr>
			<tr>
				<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Virtual memory usage</td>
				<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">{} MB</td>
				<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">{} MB</td>
			</tr>
		</tbody>
	</table>
	<table style="display: inline-block; font-family: arial, sans-serif; border-collapse: collapse;">
		<tr>
			<th width=70 style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Autopsy process</th>
			<th width=10 style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Periodic report</th>
		</tr>
		<tr>
			<td width=140 style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Autopsy processes are monitored every {} seconds</td>
			<td width=330 style="border: 1px solid #dddddd; text-align: left; padding: 8px;">The periodic report is sent to <u>{}</u> every {} seconds</td>
		</tr>
	</table>
	<p>&nbsp;</p>
	<h2><strong>Statistics:</strong></h2>
	<p><strong>CPU:</strong></p>
	<img src="cid:cpu_usage" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<img src="cid:cpu_cores" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<p style="clear: both;">
	<img src="cid:cpu_threads" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<img src="cid:cpu_time" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<p style="clear: both;">
	<p>&nbsp;</p>
	<p><strong>IO:</strong></p>
	<!--<img src="cid:io" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>-->
	<img src="cid:io" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<p style="clear: both;">
	<p>&nbsp;</p>
	<p><strong>Memory:</strong></p>
	<img src="cid:memory" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<p style="clear: both;">
	<p>&nbsp;</p>
	<p>&nbsp;</p>
	<p>&nbsp;</p>
	<p>&nbsp;</p>
	<h2><strong>Program Execution:</strong></h2>
	<p><img src="cid:status" alt="" width="1920" height="1080" /></p>
	<p>&nbsp;</p>""".format(config["CPU USAGE"]["min"], config["CPU USAGE"]["max"], config["MEMORY"]["min"], config["MEMORY"]["max"], config["TIME INTERVAL"]["process"], config["SMTP"]["receiver_email"], config["TIME INTERVAL"]["report"])

	message = MIMEMultipart("related")
	message["Subject"] = "Periodic Report"
	message["From"] = "noreply@MonAutopsy.pt"
	msgAlternative = MIMEMultipart('alternative')
	message.attach(msgAlternative)

	part1 = MIMEText(html_periodic, "html")
	msgAlternative.attach(part1)

	fp = open("cpu_usage.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_usage>')
	message.attach(msgImage)
	fp.close()

	fp = open("cpu_cores.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_cores>')
	message.attach(msgImage)
	fp.close()

	fp = open("cpu_threads.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_threads>')
	message.attach(msgImage)
	fp.close()

	fp = open("cpu_time.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_time>')
	message.attach(msgImage)
	fp.close()

	fp = open("io.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<io>')
	message.attach(msgImage)
	fp.close()

	fp = open("memory_usage.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<memory>')
	message.attach(msgImage)
	fp.close()

	#Change when screenshot.py works
	fp = open("autopsy.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<status>')
	message.attach(msgImage)
	fp.close()

	return message

def send_cpu_notif(config, SMTPServer, senderEmail, receiverEmail, password, cpuValue, min):
	if min is True:
		message = createCpuMinNotif(config, cpuValue)
	else:
		message = createCpuMaxNotif(config, cpuValue)

	send_mail(SMTPServer, senderEmail, receiverEmail, password, message)

def send_memory_notif(config, SMTPServer, senderEmail, receiverEmail, password, memoryValue, min):
	if min is True:
		message = createMemMinNotif(config, memoryValue)
	else:
		message = createMemMaxNotif(config, memoryValue)

	send_mail(SMTPServer, senderEmail, receiverEmail, password, message)

def send_report(config, SMTPServer, senderEmail, receiverEmail, password):
	message = createPeriodicReport(config)
	send_mail(SMTPServer, senderEmail, receiverEmail, password, message)

def send_mail(SMTPServer,senderEmail, receiverEmail, password, message):
	with smtplib.SMTP_SSL(SMTPServer, port, context=context) as server:
		server.login(senderEmail, password)
		for mail in receiverEmail:
			server.sendmail(senderEmail, mail, message.as_string())

def sendErrorMail(SMTPServer,senderEmail, receiverEmail, password):
	with smtplib.SMTP_SSL(SMTPServer, port, context=context) as server:
		server.login(senderEmail, password)
		html = """<h1 style="text-align: center; font-size: 50px;"><strong>ERROR, GO CHECK IT</strong></h1>"""
		message = MIMEMultipart("related")
		message["Subject"] = "ERROR - PROGRAM SHUTDOWN"
		msgAlternative = MIMEMultipart('alternative')
		message.attach(msgAlternative)
		html_email = MIMEText(html, "html")
		msgAlternative.attach(html_email)
		for mail in receiverEmail:
			server.sendmail(senderEmail, mail, message.as_string())

def check_authentication(SMTPServer, senderEmail, password):
	with smtplib.SMTP_SSL(SMTPServer, port, context=context) as server:
		try:
			server.login(senderEmail, password)
			return True
		except smtplib.SMTPException as e:
			print(e)
			return False