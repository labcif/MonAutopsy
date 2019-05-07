import configparser, re

sections = ['CPU USAGE', 'MEMORY', 'NOTIFY', 'TIME INTERVAL']
cpu_mem_keys = ['min', 'max']
notify_keys = ['smtp_server', 'sender_email', 'receiver_email']
time_keys = ['process', 'report']

def iniValidator(iniFile):
    if type(iniFile) is configparser.ConfigParser and len(iniFile.sections()) is not 0 and all(elem in iniFile.sections() for elem in sections) is True:

        #Check if every key for every sections is in place

        fileCpuKeys = [key for key in iniFile["CPU USAGE"]]

        if not all(elem in fileCpuKeys for elem in cpu_mem_keys):
            return "Invalid INI file - Error while getting [CPU USAGE] keys\nNeed: {}\nGot: {}".format(cpu_mem_keys, fileCpuKeys)

        fileMemoryKeys = [key for key in iniFile["MEMORY"]]

        if not all(elem in fileMemoryKeys for elem in cpu_mem_keys):
            return "Invalid INI file - Error while getting [MEMORY] keys\nNeed: {}\nGot: {}".format(cpu_mem_keys, fileMemoryKeys)

        fileNotifyKeys = [key for key in iniFile["NOTIFY"]]

        if not all(elem in fileNotifyKeys for elem in notify_keys):
            return "Invalid INI file - Error while getting [NOTIFY] keys\nNeed: {}\nGot: {}".format(notify_keys, fileNotifyKeys)

        fileTimeKeys = [key for key in iniFile["TIME INTERVAL"]]

        if not all(elem in fileTimeKeys for elem in time_keys):
            return "Invalid INI file - Error while getting [TIME INTERVAL] keys\nNeed: {}\nGot: {}".format(time_keys, fileTimeKeys)

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

        if not re.match("[^@]+@[^@]+\.[^@]+", iniFile["NOTIFY"]["sender_email"]):
            return "Invalid INI file - Invalid type [NOTIFY] sender_email = {} (should be an email)".format(iniFile["NOTIFY"]["sender_email"])

        if not re.match("[^@]+@[^@]+\.[^@]+", iniFile["NOTIFY"]["receiver_email"]):
            return "Invalid INI file - Invalid type [NOTIFY] receiver_email = {} (should be an email)".format(iniFile["NOTIFY"]["receiver_email"])

        #Check all URL/IP values

        if not re.match("^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$", iniFile["NOTIFY"]["smtp_server"]) and not re.match("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", iniFile["NOTIFY"]["smtp_server"]):
            return "Invalid INI file - Invalid type [NOTIFY] smtp_server = {} (should be a domain or IPv4 address)".format(iniFile["NOTIFY"]["smtp_server"])

        #Valid ini file!

        return True
    else:
        return "Invalid INI file - Failed to get ini sections"