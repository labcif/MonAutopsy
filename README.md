
# Requirements
MonAutopsy requires [Python 3](https://www.python.org/downloads/) to run.

[pip](https://pip.pypa.io/en/stable/) is also required to install all the dependencies. (pip is already installed if you are using Python 2 >=2.7.9 or Python 3 >=3.4)

# Installation
Install the dependencies to execute the program.

Windows:
```sh
> py -m pip install -r requirements.txt
```
Linux:
```sh
$ python3 -m pip install -r requirements.txt
```

# Execution

MonAutopsy starts by calling monitor.py

Windows:
```sh
> py monitor.py
```
Linux:
```sh
$ python3 monitor.py
```

# INI File
MonAutopsy uses a INI file to store all the configurations necessary for it's correct execution

- CPU and memory Usage

|                |Max						   |
|----------------|-------------------------------|
|CPU Usage		           | Maximum CPU usage for a notification to be triggered           
|Memory          | Maximum memory usage for a notification to be triggered            

# 

- SMTP Settings

|      |SMTP Server                |Sender Email|Receiver Email| 
|------|---------------------------|------------------------------------------|---
|SMTP|SMTP server domain            |Server username and sender email for all emails sent by the program|Receiver email for all emails sent by the program|
#
 - Time intervals for monitorization and statistics

|      |Process                |Report| 
|------|---------------------------|------------------------------------------
|Time Interval|Interval (in seconds) for monitorization operations. It is recommended to keep this value at 1. Most statistics are set as values per second.            |Interval (in seconds) in which the periodic report is sent to the receiver email

#

- Autopsy case settings

|      |Working Case                |
|------|---------------------------|
|Autopsy Case|Full path directory for the current working case to monitor|

### Example:
```ini
#Example configuration
[CPU USAGE]
max = 90

[MEMORY]
max = 6000

[SMTP]
smtp_server = smtp.gmail.com 
sender_email = monautopsy.notify@gmail.com
receiver_email = 123456@email.pt 

[TIME INTERVAL]
process = 1
report = 3600

[NOTIFICATIONS]
cpu_usage = 15
memory_usage = 15

[AUTOPSY CASE]  
working_directory = C:\cases\case1
```

# NOTES
- If the PC goes into lockscreen the screenshot funcionality will not work correctly, instead of showing Autopsy's UI it will show the lockscreen.
- Beware of the SMTP Server daily threshold for sending mails. GMAIL's only allows 500 daily.
