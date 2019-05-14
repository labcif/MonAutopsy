import configparser, re
from pathlib import Path

sections = ['CPU USAGE', 'MEMORY', 'SMTP', 'TIME INTERVAL', 'AUTOPSY CASE']
cpu_mem_keys = ['min', 'max']
notify_keys = ['smtp_server', 'sender_email', 'receiver_email']
time_keys = ['process', 'report']
case_keys = ['working_directory']

def iniValidator(iniFile):
    if type(iniFile) is configparser.ConfigParser and len(iniFile.sections()) is not 0 and all(elem in iniFile.sections() for elem in sections) is True:

        #Check if every key for every sections is in place

        fileCpuKeys = [key for key in iniFile["CPU USAGE"]]

        if not all(elem in fileCpuKeys for elem in cpu_mem_keys):
            return "Invalid INI file - Error while getting [CPU USAGE] keys\nNeed: {}\nGot: {}".format(cpu_mem_keys, fileCpuKeys)

        fileMemoryKeys = [key for key in iniFile["MEMORY"]]

        if not all(elem in fileMemoryKeys for elem in cpu_mem_keys):
            return "Invalid INI file - Error while getting [MEMORY] keys\nNeed: {}\nGot: {}".format(cpu_mem_keys, fileMemoryKeys)

        fileNotifyKeys = [key for key in iniFile["SMTP"]]

        if not all(elem in fileNotifyKeys for elem in notify_keys):
            return "Invalid INI file - Error while getting [SMTP] keys\nNeed: {}\nGot: {}".format(notify_keys, fileNotifyKeys)

        fileTimeKeys = [key for key in iniFile["TIME INTERVAL"]]

        if not all(elem in fileTimeKeys for elem in time_keys):
            return "Invalid INI file - Error while getting [TIME INTERVAL] keys\nNeed: {}\nGot: {}".format(time_keys, fileTimeKeys)

        fileCaseKeys = [key for key in iniFile["AUTOPSY CASE"]]

        if not all(elem in fileCaseKeys for elem in case_keys):
            return "Invalid INI file - Error while getting [AUTOPSY CASE] keys\nNeed: {}\nGot: {}".format(case_keys, fileCaseKeys)

        #Check all int values
        #.isdigit() doesn't allow negative values

        if not iniFile["CPU USAGE"]["min"].isdigit() and int(iniFile["CPU USAGE"]["min"]) > 100:
            return "Invalid INI file - Invalid type [CPU USAGE] min = {} (should be an integer between 0 and 100)".format(iniFile["CPU USAGE"]["min"])

        cpuUsage_min = int(iniFile["CPU USAGE"]["min"])

        if not iniFile["CPU USAGE"]["max"].isdigit() and int(iniFile["CPU USAGE"]["max"]) > 100:
            return "Invalid INI file - Invalid type [CPU USAGE] max = {} (should be an integer between 0 and 100)".format(iniFile["CPU USAGE"]["max"])

        cpuUsage_max = int(iniFile["CPU USAGE"]["max"])

        if not iniFile["MEMORY"]["min"].isdigit():
            return "Invalid INI file - Invalid type [MEMORY] min = {} (should be a positive integer)".format(iniFile["MEMORY"]["min"])

        memory_min = int(iniFile["MEMORY"]["min"])

        if not iniFile["MEMORY"]["max"].isdigit():
            return "Invalid INI file - Invalid type [MEMORY] max = {} (should be a positive integer)".format(iniFile["MEMORY"]["max"])

        memory_max = int(iniFile["MEMORY"]["max"])

        if not iniFile["TIME INTERVAL"]["process"].isdigit():
            return "Invalid INI file - Invalid type [TIME INTERVAL] process = {} (should be a positive integer)".format(iniFile["TIME INTERVAL"]["process"])

        time_process = int(iniFile["TIME INTERVAL"]["process"])

        if not iniFile["TIME INTERVAL"]["report"].isdigit():
            return "Invalid INI file - Invalid type [TIME INTERVAL] report = {} (should be a positive integer)".format(iniFile["TIME INTERVAL"]["report"])

        time_report = int(iniFile["TIME INTERVAL"]["report"])

        if cpuUsage_min >= cpuUsage_max:
            return "Invalid INI file - Invalid type [CPU USAGE] min = {}; max = {} (minimum cpu usage can't be equal or greater than maximum cpu usage)".format(cpuUsage_min, cpuUsage_max)

        if memory_min >= memory_max:
            return "Invalid INI file - Invalid type [MEMORY] min = {}; max = {} (minimum memory usage can't be equal or greater than maximum memory usage)".format(memory_min, memory_max)

        if time_process > time_report:
            return "Invalid INI file - Invalid type [TIME INTERVAL] process = {}; report = {} (report time interval can't be lower than process time interval)".format(time_process, time_report)

        #Check all email values

        if not re.match("""^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$""", iniFile["SMTP"]["sender_email"]):
            return "Invalid INI file - Invalid type [SMTP] sender_email = {} (should be an email)".format(iniFile["SMTP"]["sender_email"])

        receivers = []
        # Check for several emails on receiver
        if ", " in iniFile["SMTP"]["receiver_email"]:
            receivers = iniFile["SMTP"]["receiver_email"].split(", ")
        else:
            receivers = [iniFile["SMTP"]["receiver_email"]]

        for mail in receivers:
            if not re.match("""^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$""", mail):
                 return "Invalid INI file - Invalid type [SMTP] receiver_email = {} (should be a domain or IPv4 address)".format(iniFile["SMTP"]["receiver_email"])


        #Check all IP and domain values

        if not re.match("^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$", iniFile["SMTP"]["smtp_server"]) and not re.match("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", iniFile["SMTP"]["smtp_server"]):
            return "Invalid INI file - Invalid type [SMTP] smtp_server = {} (should be a domain or IPv4 address)".format(iniFile["SMTP"]["smtp_server"])


        working_directory = iniFile["AUTOPSY CASE"]["working_directory"]

        if working_directory[-1:] != "\\":
            working_directory += "\\"

        if not Path(working_directory + "Log").exists():
            return "Invalid INI file - Invalid type [AUTOPSY CASE] working_directory = {} (should be a valid and existing Autopsy Case directory)".format(working_directory)

        #Valid ini file!

        return True
    else:
        return "Invalid INI file - Failed to get ini sections"