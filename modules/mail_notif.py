import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from modules.database import retrieve_latest_job, retrieve_cpu_values_report, retrieve_first_cpu_value
import math, os, socket, psutil, time, configparser
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))

port = 465  # SSL

#Read config
config = configparser.ConfigParser()
config.read('config.ini')

# Secure SSL Context
context = ssl.create_default_context()

def getBasicInfo():
	caseName = os.path.basename(config["AUTOPSY CASE"]["working_directory"])

	disk_autopsy = os.path.splitdrive(config["AUTOPSY CASE"]["working_directory"])[0]
	diskUsageAutopsy = str(
		round(psutil.disk_usage(config["AUTOPSY CASE"]["working_directory"])[2] * 0.000000000931323, 2)) + "GB"
	remainingDisks = str()
	dps = psutil.disk_partitions()

	try:
		for i in range(0, len(dps)):
			dp = dps[i]
			if dp.fstype != '' and 'cdrom' not in dp.opts:
				if str(dp.device).__contains__("\\"):
					if str(dp.device).replace("\\", "") != disk_autopsy:
						remainingDisks += str(dp.device) + " - " + str(round(psutil.disk_usage(dp.device)[2] * 0.000000000931323, 2)) + "GB" + " remaining; "
					else:
						disk_autopsy = str(dp.device) + " - " + diskUsageAutopsy + " remaining"
				elif str(dp.device) != disk_autopsy:
					remainingDisks += str(dp.device) + " - " + str(round(psutil.disk_usage(dp.device)[2] * 0.000000000931323, 2)) + "GB" + " remaining; "
	except PermissionError:
		pass

	return caseName, disk_autopsy, diskUsageAutopsy, remainingDisks

def getCompleteInfo(last_cpu_time):
	caseName, disk_autopsy, diskUsageAutopsy, remainingDisks = getBasicInfo()

	job = retrieve_latest_job()
	start_time = job['start_time']
	finish_time = job['finish_time']
	
	curr_time = round(time.time())
	elapsed_time = curr_time - start_time

	elapsed_time_str = "{:02d}h {:02d}m {:02d}s".format(elapsed_time // 3600, (elapsed_time % 3600 // 60), (elapsed_time % 3600 % 60))

	start_time = time.localtime(start_time)

	finish_time = time.localtime(finish_time)

	start_cpu_time = retrieve_first_cpu_value()['cpu_time']

	elapsed_cpu_time = last_cpu_time - start_cpu_time

	elapsed_cpu_time_str = "{:02d}h {:02d}m {:02d}s".format(elapsed_cpu_time // 3600, (elapsed_cpu_time % 3600 // 60), (elapsed_cpu_time % 3600 % 60))

	return caseName, disk_autopsy, diskUsageAutopsy, remainingDisks, start_time, elapsed_time_str, elapsed_cpu_time_str, finish_time

def createMemMaxNotif(memoryValue):

	caseName, disk_autopsy, diskUsageAutopsy, remainingDisks = getBasicInfo()

	html_memory_notif = """<style>.center {{
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;
}}</style>
<h1 style="text-align: center; font-size: 50px;"><strong>Memory Notification</strong></h1>
<p>&nbsp;</p>
<h2>General information</h2>
<p><strong>Machine name: </strong>{}</p>
<p><strong>IP Address: </strong>{}</p>
<p><strong>Free disk space: </strong></p>
	<ul>
	<li>Disk being used by Autopsy:
	<ul>
	<li>{}</li>
	</ul>
	</li>
	<li>Remaining Disks:
	<ul>
	<li>{}</li>
	</ul>
	</li>
	</ul>
<p><strong>Autopsy case name: </strong>{}</p>
<p>&nbsp;</p>
<h2>WARNING:</h2>
<p style="padding-left: 60px;">Memory usage is higher than maximum value established ({}MB).</p>
<p style="padding-left: 60px;">Current memory value is&nbsp;&asymp; <strong>{}MB</strong></p>
<img src="cid:memory_usage" alt="" style="display: block; margin-left: auto; margin-right: auto; width:50%"/>""".format(socket.gethostname(), s.getsockname()[0], disk_autopsy + " - " + diskUsageAutopsy + " remaining", remainingDisks, caseName, config["MEMORY"]["max"], math.floor(memoryValue))

	message = MIMEMultipart("related")
	message["Subject"] = str(caseName) + ": " + "Memory notification"
	message["From"] = "noreply@MonAutopsy.pt"
	msgAlternative = MIMEMultipart('alternative')
	message.attach(msgAlternative)

	part1 = MIMEText(html_memory_notif, "html")
	msgAlternative.attach(part1)

	fp = open("miscellaneous/memory_notif_max.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<memory_usage>')
	message.attach(msgImage)
	fp.close()

	return message

def createCpuMaxNotif(cpuValue):

	caseName, disk_autopsy, diskUsageAutopsy, remainingDisks = getBasicInfo()

	html_cpu_notif = """<style>.center {{
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;
}}</style>
<h1 style="text-align: center; font-size: 50px;"><strong>CPU Notification</strong></h1>
<p>&nbsp;</p>
<h2>General information</h2>
<p><strong>Machine name: </strong>{}</p>
<p><strong>IP Address: </strong>{}</p>
<p><strong>Free disk space: </strong></p>
	<ul>
	<li>Disk being used by Autopsy:
	<ul>
	<li>{}</li>
	</ul>
	</li>
	<li>Remaining Disks:
	<ul>
	<li>{}</li>
	</ul>
	</li>
	</ul>
<p><strong>Autopsy case name: </strong>{}</p>
<p>&nbsp;</p>
<h2>WARNING:</h2>
<p style="padding-left: 60px;">CPU usage is lower than maximum value established ({}%).</p>
<p style="padding-left: 60px;">Current CPU value is&nbsp;&asymp; <strong>{}%</strong></p>
<img src="cid:cpu_usage" alt="" style="display: block; margin-left: auto; margin-right: auto; width:50%"/>""".format(socket.gethostname(), s.getsockname()[0], disk_autopsy, remainingDisks, caseName, config["CPU USAGE"]["max"], cpuValue)

	message = MIMEMultipart("related")
	message["Subject"] = str(caseName) + ": " + "CPU notification"
	message["From"] = "noreply@MonAutopsy.pt"
	msgAlternative = MIMEMultipart('alternative')
	message.attach(msgAlternative)

	part1 = MIMEText(html_cpu_notif, "html")
	msgAlternative.attach(part1)

	fp = open("miscellaneous/cpu_notif_max.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_usage>')
	message.attach(msgImage)
	fp.close()

	return message

def createPeriodicReport(last_cpu_time):

	caseName, disk_autopsy, diskUsageAutopsy, remainingDisks, start_time, elapsed_time_str, elapsed_cpu_time_str, finishTime = getCompleteInfo(last_cpu_time)

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
	<h2>General information</h2>
	<p><strong>Machine name: </strong>{}</p>
	<p><strong>IP Address: </strong>{}</p>
	<p><strong>Free disk space: </strong></p>
	<ul>
	<li>Disk being used by Autopsy:
	<ul>
	<li>{}</li>
	</ul>
	</li>
	<li>Remaining Disks:
	<ul>
	<li>{}</li>
	</ul>
	</li>
	</ul>
	<p><strong>Autopsy case name: </strong>{}</p>
	<p><strong>Job start time: </strong>{}</p>
	<p><strong>Elapsed time: </strong>{}</p>
	<p><strong>CPU elapsed time: </strong>{}</p>
	<p>&nbsp;</p>
	<h2>Configurations:</h2>
	<table style="display: inline-block; font-family: arial, sans-serif; border-collapse: collapse;">
		<thead>
			<tr>
				<th style="font-weight: 800; border: 1px solid #dddddd; text-align: left; padding: 8px;">CPU/Memory configuration</th>
				<th style="font-weight: bolder; border: 1px solid #dddddd; text-align: left; padding: 8px;">Maximum threshold</th>
			</tr>
		</thead>
			<tbody>
				<tr>
				<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">CPU usage</td>
				<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">{} %</td>
			</tr>
			<tr>
				<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Virtual memory usage</td>
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
	<p style="clear: both;">
	<p>&nbsp;</p>
	<p><strong>IO:</strong></p>
	<!--<img src="cid:io" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>-->
	<img src="cid:io" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<p style="clear: both;">
	<p>&nbsp;</p>
	<p><strong>Memory:</strong></p>
	<img src="cid:memory" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<img src="cid:solr_memory" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<p style="clear: both;">
	<p>&nbsp;</p>
	<p><strong>Disk Space:</strong></p>
	<img src="cid:free_disk_space" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<p style="clear: both;">
	<p>&nbsp;</p>
	<p>&nbsp;</p>
	<p>&nbsp;</p>
	<p>&nbsp;</p>
	<h2><strong>Program Execution:</strong></h2>
	<p><img src="cid:status" alt="" width="1920" height="1080" /></p>
	<p>&nbsp;</p>""".format(socket.gethostname(), s.getsockname()[0], disk_autopsy, remainingDisks, caseName, time.strftime("%d/%m/%Y - %H:%M:%S", start_time), elapsed_time_str, elapsed_cpu_time_str, config["CPU USAGE"]["max"], config["MEMORY"]["max"], config["TIME INTERVAL"]["process"], config["SMTP"]["receiver_email"], config["TIME INTERVAL"]["report"])



	message = MIMEMultipart("related")
	message["Subject"] = str(caseName) + ": " + "Periodic Report"
	message["From"] = "noreply@MonAutopsy.pt"
	msgAlternative = MIMEMultipart('alternative')
	message.attach(msgAlternative)

	part1 = MIMEText(html_periodic, "html")
	msgAlternative.attach(part1)

	fp = open("miscellaneous/cpu_usage.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_usage>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/cpu_cores.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_cores>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/cpu_threads.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_threads>')
	message.attach(msgImage)
	fp.close()

	# fp = open("miscellaneous/cpu_time.png", "rb")
	# msgImage = MIMEImage(fp.read())
	# msgImage.add_header('Content-ID', '<cpu_time>')
	# message.attach(msgImage)
	# fp.close()

	fp = open("miscellaneous/io.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<io>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/memory_usage.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<memory>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/solr_memory.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<solr_memory>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/free_disk_space.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<free_disk_space>')
	message.attach(msgImage)
	fp.close()

	#Change when screenshot.py works
	fp = open("miscellaneous/autopsy.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<status>')
	message.attach(msgImage)
	fp.close()

	return message

def createErrorNotifWithData(title, message, last_cpu_time):

	caseName, disk_autopsy, diskUsageAutopsy, remainingDisks, start_time, elapsed_time_str, elapsed_cpu_time_str, finishTime = getCompleteInfo(last_cpu_time)

	html_error_notif = """<style>.center {{
	display: block;
	margin-left: auto;
	margin-right: auto;
	width: 50%;
	}}</style>
	<h1 style="text-align: center; font-size: 50px;"><strong>{} Notification</strong></h1>
	<p>&nbsp;</p>
	<h2>WARNING:</h2>
	<p style="padding-left: 60px; text-decoration: underline;">{}</p>
	<p>&nbsp;</p>
	<h2>General information</h2>
	<p><strong>Machine name: </strong>{}</p>
	<p><strong>IP Address: </strong>{}</p>
	<p><strong>Free disk space: </strong></p>
	<ul>
	<li>Disk being used by Autopsy:
	<ul>
	<li>{}</li>
	</ul>
	</li>
	<li>Remaining Disks:
	<ul>
	<li>{}</li>
	</ul>
	</li>
	</ul>
	<p><strong>Autopsy case name: </strong>{}</p>
	<p><strong>Job start time: </strong>{}</p>
	<p><strong>Elapsed time: </strong>{}</p>
	<p><strong>CPU elapsed time: </strong>{}</p>
	<p>&nbsp;</p>
	<h2>Configurations:</h2>
	<table style="display: inline-block; font-family: arial, sans-serif; border-collapse: collapse;">
		<thead>
			<tr>
				<th style="font-weight: 800; border: 1px solid #dddddd; text-align: left; padding: 8px;">CPU/Memory configuration</th>
				<th style="font-weight: bolder; border: 1px solid #dddddd; text-align: left; padding: 8px;">Maximum threshold</th>
			</tr>
		</thead>
			<tbody>
				<tr>
				<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">CPU usage</td>
				<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">{} %</td>
			</tr>
			<tr>
				<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Virtual memory usage</td>
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
	<img src="cid:cpu_usage_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<img src="cid:cpu_cores_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<p style="clear: both;">
	<img src="cid:cpu_threads_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<p style="clear: both;">
	<p>&nbsp;</p>
	<p><strong>IO:</strong></p>
	<!--<img src="cid:io_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>-->
	<img src="cid:io_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<p style="clear: both;">
	<p>&nbsp;</p>
	<p><strong>Memory:</strong></p>
	<img src="cid:memory_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<img src="cid:solr_memory_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<p style="clear: both;">
	<p>&nbsp;</p>
	<p><strong>Disk Space:</strong></p>
	<img src="cid:free_disk_space" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
	<p style="clear: both;">
	<p>&nbsp;</p>
	<p>&nbsp;</p>
	<p>&nbsp;</p>
	<p>&nbsp;</p>
	<p>&nbsp;</p>""".format(title, message, socket.gethostname(), s.getsockname()[0], disk_autopsy, remainingDisks, caseName, time.strftime("%d/%m/%Y - %H:%M:%S", start_time), elapsed_time_str, elapsed_cpu_time_str, config["CPU USAGE"]["max"], config["MEMORY"]["max"], config["TIME INTERVAL"]["process"], config["SMTP"]["receiver_email"], config["TIME INTERVAL"]["report"])

	message = MIMEMultipart("related")
	message["Subject"] = str(caseName) + ": " + title + " Notification"
	message["From"] = "noreply@MonAutopsy.pt"
	msgAlternative = MIMEMultipart('alternative')
	message.attach(msgAlternative)

	part1 = MIMEText(html_error_notif, "html")
	msgAlternative.attach(part1)

	fp = open("miscellaneous/cpu_usage_final.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_usage_final>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/cpu_cores_final.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_cores_final>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/cpu_threads_final.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_threads_final>')
	message.attach(msgImage)
	fp.close()

	# fp = open("miscellaneous/cpu_time_final.png", "rb")
	# msgImage = MIMEImage(fp.read())
	# msgImage.add_header('Content-ID', '<cpu_time_final>')
	# message.attach(msgImage)
	# fp.close()

	fp = open("miscellaneous/io_final.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<io_final>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/free_disk_space.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<free_disk_space>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/memory_usage_final.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<memory_final>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/solr_memory_final.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<solr_memory_final>')
	message.attach(msgImage)
	fp.close()

	return message

def createErrorNotifNoData(title, message):
	caseName, disk_autopsy, diskUsageAutopsy, remainingDisks = getBasicInfo()

	html_error_notif = """<style>.center {{
	display: block;
	margin-left: auto;
	margin-right: auto;
	width: 50%;
	}}</style>
	<h1 style="text-align: center; font-size: 50px;"><strong>{} Notification</strong></h1>
	<p>&nbsp;</p>
	<h2>WARNING:</h2>
	<p style="padding-left: 60px; text-decoration: underline;">{}</p>
	<p>&nbsp;</p>
	<h2>General information</h2>
	<p><strong>Machine name: </strong>{}</p>
	<p><strong>IP Address: </strong>{}</p>
	<p><strong>Free disk space: </strong></p>
	<ul>
	<li>Disk being used by Autopsy:
	<ul>
	<li>{}</li>
	</ul>
	</li>
	<li>Remaining Disks:
	<ul>
	<li>{}</li>
	</ul>
	</li>
	</ul>
	<p><strong>Autopsy case name: </strong>{}</p>""".format(title, message, socket.gethostname(), s.getsockname()[0], disk_autopsy, remainingDisks, caseName)

	message = MIMEMultipart("related")
	message["Subject"] = str(caseName) + ": " + title + " Notification"
	message["From"] = "noreply@MonAutopsy.pt"
	msgAlternative = MIMEMultipart('alternative')
	message.attach(msgAlternative)

	part1 = MIMEText(html_error_notif, "html")
	msgAlternative.attach(part1)

	return message

def createFinalReport(last_cpu_time):
	caseName, disk_autopsy, diskUsageAutopsy, remainingDisks, start_time, elapsed_time_str, elapsed_cpu_time_str, finish_time = getCompleteInfo(last_cpu_time)

	html_error_notif = """<style>.center {{
		display: block;
		margin-left: auto;
		margin-right: auto;
		width: 50%;
		}}</style>
		<h1 style="text-align: center; font-size: 50px;"><strong>{}</strong></h1>
		<p>&nbsp;</p>
		<h2>General information</h2>
		<p><strong>Machine name: </strong>{}</p>
		<p><strong>IP Address: </strong>{}</p>
		<p><strong>Free disk space: </strong></p>
		<ul>
		<li>Disk being used by Autopsy:
		<ul>
		<li>{}</li>
		</ul>
		</li>
		<li>Remaining Disks:
		<ul>
		<li>{}</li>
		</ul>
		</li>
		</ul>
		<p><strong>Autopsy case name: </strong>{}</p>
		<p><strong>Job start time: </strong>{}</p>
		<p><strong>Elapsed time: </strong>{}</p>
		<p><strong>CPU elapsed time: </strong>{}</p>
		<p><strong>Job finish time: </strong>{}</p>
		<p>&nbsp;</p>
		<h2>Configurations:</h2>
		<table style="display: inline-block; font-family: arial, sans-serif; border-collapse: collapse;">
			<thead>
				<tr>
					<th style="font-weight: 800; border: 1px solid #dddddd; text-align: left; padding: 8px;">CPU/Memory configuration</th>
					<th style="font-weight: bolder; border: 1px solid #dddddd; text-align: left; padding: 8px;">Maximum threshold</th>
				</tr>
			</thead>
				<tbody>
					<tr>
					<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">CPU usage</td>
					<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">{} %</td>
				</tr>
				<tr>
					<td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Virtual memory usage</td>
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
		<img src="cid:cpu_usage_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
		<img src="cid:cpu_cores_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
		<p style="clear: both;">
		<img src="cid:cpu_threads_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
		<p style="clear: both;">
		<p>&nbsp;</p>
		<p><strong>IO:</strong></p>
		<!--<img src="cid:io_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>-->
		<img src="cid:io_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
		<p style="clear: both;">
		<p>&nbsp;</p>
		<p><strong>Memory:</strong></p>
		<img src="cid:memory_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
		<img src="cid:solr_memory_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
		<p style="clear: both;">
		<p>&nbsp;</p>
		<p><strong>Disk Space:</strong></p>
		<img src="cid:free_disk_space_final" alt="" style="float: left; width: 45%; margin-right: 1%; margin-bottom: 0.5em;"/>
		<p style="clear: both;">
		<p>&nbsp;</p>
		<p>&nbsp;</p>
		<p>&nbsp;</p>
		<p>&nbsp;</p>
		<p>&nbsp;</p>""".format("Final Report", socket.gethostname(), s.getsockname()[0], disk_autopsy, remainingDisks, caseName,
								time.strftime("%d/%m/%Y - %H:%M:%S", start_time), elapsed_time_str, elapsed_cpu_time_str, time.strftime("%d/%m/%Y - %H:%M:%S", finish_time),
								config["CPU USAGE"]["max"], config["MEMORY"]["max"], config["TIME INTERVAL"]["process"],
								config["SMTP"]["receiver_email"], config["TIME INTERVAL"]["report"])

	message = MIMEMultipart("related")
	message["Subject"] = str(caseName) + ": " + "Job finished - final report"
	message["From"] = "noreply@MonAutopsy.pt"
	msgAlternative = MIMEMultipart('alternative')
	message.attach(msgAlternative)

	part1 = MIMEText(html_error_notif, "html")
	msgAlternative.attach(part1)

	fp = open("miscellaneous/cpu_usage_final.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_usage_final>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/cpu_cores_final.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_cores_final>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/cpu_threads_final.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<cpu_threads_final>')
	message.attach(msgImage)
	fp.close()

	# fp = open("miscellaneous/cpu_time_final.png", "rb")
	# msgImage = MIMEImage(fp.read())
	# msgImage.add_header('Content-ID', '<cpu_time_final>')
	# message.attach(msgImage)
	# fp.close()

	fp = open("miscellaneous/io_final.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<io_final>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/free_disk_space_final.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<free_disk_space_final>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/memory_usage_final.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<memory_final>')
	message.attach(msgImage)
	fp.close()

	fp = open("miscellaneous/solr_memory_final.png", "rb")
	msgImage = MIMEImage(fp.read())
	msgImage.add_header('Content-ID', '<solr_memory_final>')
	message.attach(msgImage)
	fp.close()

	return message


def send_cpu_notif(password, cpuValue):

	message = createCpuMaxNotif(cpuValue)

	send_mail(password, message)

def send_memory_notif(password, memoryValue):

	message = createMemMaxNotif(memoryValue)

	send_mail(password, message)

def send_report(password, last_cpu_time):

	message = createPeriodicReport(last_cpu_time)
	send_mail(password, message)

def send_final_report(password, last_cpu_time):
	message = createFinalReport(last_cpu_time)
	send_mail(password, message)

def send_mail(password, message):
	with smtplib.SMTP_SSL(config["SMTP"]["smtp_server"], port, context=context) as server:
		server.login(config["SMTP"]["sender_email"], password)
		if ", " in config["SMTP"]["receiver_email"]:
			receivers = str.split(config["SMTP"]["receiver_email"], ", ")
		else:
			receivers = config["SMTP"]["receiver_email"]
		server.sendmail(config["SMTP"]["sender_email"], receivers, message.as_string())
		#for mail in receivers:
		#	server.sendmail(config["SMTP"]["sender_email"], mail, message.as_string())

def sendErrorMailWithData(password, title, message, last_cpu_time):

	mail_message = createErrorNotifWithData(title, message, last_cpu_time)

	send_mail(password, mail_message)

def sendErrorMailNoData(password, title, message):

	mail_message = createErrorNotifNoData(title, message)

	send_mail(password, mail_message)

def check_authentication(password):
	with smtplib.SMTP_SSL(config["SMTP"]["smtp_server"], port, context=context) as server:
		try:
			server.login(config["SMTP"]["sender_email"], password)
			return True
		except smtplib.SMTPException as e:
			print(e)
			return False