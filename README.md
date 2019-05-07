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

|                |Min                            |Max						   |
|----------------|-------------------------------|-----------------------------|
|CPU Usage		 | Minimum CPU usage for a notification to be triggered           | Maximum CPU usage for a notification to be triggered           
|Memory          | Minimum memory usage for a notification to be triggered           |Maximum memory usage for a notification to be triggered            

# 

- Notifications Setting

|      |SMTP Server                |Sender Email|Receiver Email| 
|------|---------------------------|------------------------------------------|---
|Notify|SMTP server domain            |Server username and sender email for all emails sent by the program|Receiver email for all emails sent by the program|
#
 - Time intervals for monitorization and statistics

|      |Process                |Report| 
|------|---------------------------|------------------------------------------
|Time Interval|Interval (in seconds) for monitorization operations            |Interval (in seconds) in which the periodic report is sent to the receiver email

### Example:
```ini
#Example configuration
[CPU USAGE]
Min = 10
Max = 90

[MEMORY]
Min = 1000
Max = 6000

[NOTIFY]
SMTPServer = smtp.gmail.com 
SenderMail = monautopsy.notify@gmail.com
ReceiverMail = 123456@email.pt 

[TIME INTERVAL]
Process = 2
Report = 10
```
