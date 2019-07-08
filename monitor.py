#PSUtil doc: https://psutil.readthedocs.io/en/latest/
#threading doc: https://docs.python.org/2/library/threading.html
import psutil, threading, configparser, requests
from getpass import getpass
from modules.database import *
from modules.graphics import *
from modules.mail_notif import send_report, check_authentication, send_cpu_notif, send_memory_notif, sendErrorMailWithData, sendErrorMailNoData, send_final_report
from modules.screenshot import screenshotAutopsy
from modules.ini_validation import iniValidator
from xml.dom import minidom

#Not necessary for the time being:
#Variables for disk monitorization
#previousDiskBusyTime = psutil.disk_io_counters().read_time + psutil.disk_io_counters().write_time
#print(str(previousDiskBusyTime))

#Load INI
config = configparser.ConfigParser()
config.read('config.ini')
validation = iniValidator(config)
if type(validation) is not bool:
    print(validation)
    exit(2)

#SMTP Password
authenticated = False
while authenticated is False :
    smtp_password = getpass(prompt='Enter SMTP password: ')
    authenticated = check_authentication(smtp_password)

#Usar 'config' para definir todos os intervalos de valores a monitorizar

#Selected process monitorization
PROCNAME = ["autopsy.exe", "autopsy64.exe"]
print("\n-----------------------\n\nProcess: " + str(PROCNAME))
print("\nCPU PERCENT")
mainProcess = None

#Check if process exist and select it
for proc in psutil.process_iter():
    if proc.name() in PROCNAME:
        mainProcess = proc
if mainProcess is None:
    print("No process named "+str(PROCNAME))
    exit(2)

#Root directory
dirname = os.path.dirname(os.path.abspath(__file__))

#Create database directory
databaseDir = dirname + "\\database"
database = dirname + "\\database\\database.db"
if os.path.isdir(databaseDir) is not True:
    os.mkdir(databaseDir)

#Create miscellaneous directory
miscellaneousDir = dirname + "\\miscellaneous"
if os.path.isdir(miscellaneousDir) is not True:
    os.mkdir(miscellaneousDir)


#Create database tables
createTables()

#Threads declarations
#processesThread = None
#reportThread = None
threads_exit_event = threading.Event()
ongoing_job_event = threading.Event()
readLogFileThread_exit_event = threading.Event()
job_error_event = threading.Event()


#Email receivers
receivers = []
if ", " in config["SMTP"]["receiver_email"]:
    receivers = config["SMTP"]["receiver_email"].split(", ")
else:
    receivers = [config["SMTP"]["receiver_email"]]

# Number of values for the X axis
# xNumValues = math.floor(int(config["TIME INTERVAL"]["report"]) / int(config["TIME INTERVAL"]["process"])) + 1
# if xNumValues > 11:
#     xNumValues = 11

def diskSpaceDic():
    disk_autopsy = os.path.splitdrive(config["AUTOPSY CASE"]["working_directory"])[0]

    dps = psutil.disk_partitions()
    disksDic = {}

    try:
        for i in range(0, len(dps)):
            dp = dps[i]
            if dp.fstype != '' and 'cdrom' not in dp.opts:
                if str(dp.device).__contains__("\\"):
                    if str(dp.device).replace("\\", "") != disk_autopsy:
                        disksDic[dp.device] = []
                    else:
                        disksDic[str(dp.device) + " (disk used by Autopsy)"] = []
                else:
                    if str(dp.device) == disk_autopsy:
                        disksDic[str(dp.device) + " (disk used by Autopsy)"] = []
                    else:
                        disksDic[dp.device] = []
    except PermissionError:
        pass
    return disksDic


#Free Disk Space
disks = diskSpaceDic()
disksIter = 0


#Solr Memory
def solrCurrentMemory():
    response = requests.get("http://localhost:" + str(getSolrPort()) + "/solr/admin/info/system?wt=json")

    currentMemory = response.json()["jvm"]["memory"]["used"]

    currentMemory = str.rsplit(currentMemory, " ")[0]

    return currentMemory

def solrMaximumMemory():
    response = requests.get("http://localhost:" + str(getSolrPort()) + "/solr/admin/info/system?wt=json")

    maximumMemory = response.json()["jvm"]["memory"]["max"]

    maximumMemory = str.rsplit(maximumMemory, " ")[0]

    return int(float(maximumMemory))

def getSolrPort():
    path = mainProcess.exe()
    rootSolr = path.rsplit("bin", 1)[0] + "autopsy\solr\etc\jetty.xml"

    doc = minidom.parse(rootSolr)

    sets = doc.getElementsByTagName("SystemProperty")

    for set in sets:
        if set.attributes['name'].value == "jetty.port":
            return set.attributes['default'].value

#Process(es) monitorization
def checkProcesses():
    errorOccurred = False
    cpu_occurrences_max = 0
    memory_occurrences_max = 0
    notif_thread = None
    cpuTimeClosedProcesses = 0
    IOReadCountClosedProcesses = 0
    IOReadBytesClosedProcesses = 0
    IOWriteCountClosedProcesses = 0
    IOWriteBytesClosedProcesses = 0
    pageFaultsClosedProcesses = 0
    lastProcessesInfo = dict()
    processes = dict()
    processes[mainProcess.pid] = mainProcess

    while not threads_exit_event.is_set() and not errorOccurred: # Loops while the event flag has not been set
        start_timestamp = time.time()
        update_timeTuple = (round(start_timestamp),)
        #print("[" + time.strftime("%d/%m/%Y - %H:%M:%S", time.localtime(start_timestamp)) + " - " + str(start_timestamp) + "]" + "[checkProcessesThread] The event flag is not set yet, continuing operation")
        print("Monitoring...")
        cpuUsage = 0.0

        processesCPUTimes = []
        processesCPUAfinnity = set() #Unique values only
        processesIOCounters = []
        processesMemoryInfo = []
        totalThreads = 0

        lastProcessesList = []

        for lastProc, lastProcInfo in lastProcessesInfo.items():
            if not lastProc.is_running():
                print("[checkProcessesThread] Process with PID " + str(lastProc.pid) + " and name '" + lastProcInfo[3] + "' closed from last iteration to the current one.")
                #cpu_times()
                cpuTimeClosedProcesses += (lastProcInfo[0].user + lastProcInfo[0].system)

                #io_counters()
                IOReadCountClosedProcesses += lastProcInfo[1].read_count
                IOReadBytesClosedProcesses += lastProcInfo[1].read_bytes
                IOWriteCountClosedProcesses += lastProcInfo[1].write_count
                IOWriteBytesClosedProcesses += lastProcInfo[1].write_bytes

                #memory_full_info()
                pageFaultsClosedProcesses += lastProcInfo[2].num_page_faults

                lastProcessesList.append(lastProc)

        for lastProc in lastProcessesList:
            lastProcessesInfo.pop(lastProc)

        #Try catch here in case the mainProcess dies
        try:
            processesList = mainProcess.children(recursive=True) #Get all processes descendants

            for proc in processes.values():
                if not proc.is_running():
                    processes.pop(proc.pid)

            for process in processesList:
                if process.pid not in processes:
                    processes[process.pid] = process

        except psutil.NoSuchProcess:
            if not mainProcess.is_running():
                print("All processes are dead!!!")
                errorOccurred = True
                continue

        for proc in processes.values():
            #Try catch in case some process besides main process dies, this way the execution won't stop due to a secondary process
            try:
                cpuUsage += proc.cpu_percent() / psutil.cpu_count()
                cpuUsage = round(cpuUsage, 2)

                totalThreads += proc.num_threads()

                processesCPUAfinnity.update(proc.cpu_affinity())

                procCPUTimes = proc.cpu_times()
                procIOCounters = proc.io_counters()
                procMemoryInfo = proc.memory_full_info()
                procName = proc.name()

                processesCPUTimes.append(procCPUTimes)
                processesIOCounters.append(procIOCounters)
                processesMemoryInfo.append(procMemoryInfo)

                lastProcessesInfo[proc] = (procCPUTimes, procIOCounters, procMemoryInfo, procName)

            except psutil.NoSuchProcess:
                if not mainProcess.is_running():
                    print("All processes are dead!!!")
                    errorOccurred = True
                    break
                else:
                    print("Some processes were closed!")

        if errorOccurred:
            continue

        #Getting 1 record of cpu, which is the sum of the cpu fields of the processes

        processesNumCores = len(processesCPUAfinnity)
        totalUserTime = 0
        totalSystemTime = 0
        #totalIdleTime = 0

        for CPUTimes in processesCPUTimes:
            totalUserTime += CPUTimes.user
            totalSystemTime += CPUTimes.system

        totalCPUTime = round(totalUserTime + totalSystemTime + cpuTimeClosedProcesses)

        cpuRecord = (cpuUsage, processesNumCores, totalThreads, totalCPUTime)

        #Getting 1 record of IO, which is the sum of the IO fields of the processes

        totalReadCount = IOReadCountClosedProcesses
        totalWriteCount = IOWriteCountClosedProcesses
        totalReadBytes = IOReadBytesClosedProcesses
        totalWriteBytes = IOWriteBytesClosedProcesses

        for IOCounter in processesIOCounters:
            totalReadCount += IOCounter.read_count
            totalWriteCount += IOCounter.write_count
            totalReadBytes += IOCounter.read_bytes
            totalWriteBytes += IOCounter.write_bytes

        IORecord = (totalReadCount, totalWriteCount, totalReadBytes, totalWriteBytes)

        totalMemoryUsage = 0
        totalPageFaults = pageFaultsClosedProcesses

        for memoryInfo in processesMemoryInfo:
            totalMemoryUsage += memoryInfo.uss
            totalPageFaults += memoryInfo.num_page_faults

        systemMemoryUsage = psutil.virtual_memory().used

        solrMemory = solrCurrentMemory()

        memoryRecord = (totalMemoryUsage, totalPageFaults, systemMemoryUsage, solrMemory)

        # Get percentage of used disk space
        for key in disks:
            try:
                if key.__contains__("(disk used by Autopsy)"):
                    totalBytes = psutil.disk_usage(key.replace("(disk used by Autopsy)", ""))[0]
                    currentUsedBytes = psutil.disk_usage(key.replace("(disk used by Autopsy)", ""))[1]
                    percUsed = int(currentUsedBytes * 100 / totalBytes)
                else:
                    totalBytes = psutil.disk_usage(key)[0]
                    currentUsedBytes = psutil.disk_usage(key)[1]
                    percUsed = int(currentUsedBytes * 100 / totalBytes)
                disks[key].append(str(percUsed) +  ", " + str(datetime.now().timestamp()))
            except FileNotFoundError:
                disks[key].append("-1" + ", " + str(datetime.now().timestamp()))

        #Add all the records to the database

        add_updates_record(cpuRecord, IORecord, memoryRecord, update_timeTuple)

        #Send notifications if...

        if cpuUsage > int(config["CPU USAGE"]["max"], 10):
            if cpu_occurrences_max == int(config["NOTIFICATIONS"]["cpu_usage"]):
                cpu_max_notif_data = retrieve_cpu_values_notif()
                cpuUsageGraph("miscellaneous/cpu_notif_max", cpu_max_notif_data, int(config["CPU USAGE"]["max"]))
                lastCpuValue = cpu_max_notif_data[-1][0]
                notif_thread = threading.Thread(target=send_cpu_notif, args=(smtp_password, lastCpuValue))
                notif_thread.start()
                cpu_occurrences_max = 0
            else:
                cpu_occurrences_max += 1
        else:
            cpu_occurrences_max = 0
        #TODO: Create IO anomaly notification and call it here

        if totalMemoryUsage / 1000000 > int(config["MEMORY"]["max"]):
            if memory_occurrences_max == int(config["NOTIFICATIONS"]["memory_usage"]):
                memory_max_notif_data = retrieve_memory_values_notif()
                memoryUsageGraph("miscellaneous/memory_notif_max", memory_max_notif_data, int(config["MEMORY"]["max"]))
                lastMemoryValue = int(memory_max_notif_data[-1][0]) / 1000000
                notif_thread = threading.Thread(target=send_memory_notif, args=(smtp_password, lastMemoryValue))
                notif_thread.start()
                memory_occurrences_max = 0
            else:
                memory_occurrences_max += 1
        else:
            memory_occurrences_max = 0

        finish_timestamp = time.time()
        waiting_time = float(config["TIME INTERVAL"]["process"]) - (finish_timestamp - start_timestamp)

        # The thread will get blocked here unless the event flag is already set, and will break if it set at any time during the timeout
        if waiting_time > 0:
            threads_exit_event.wait(timeout=waiting_time)

    #if not errorOccurred:
    #    print("[checkProcessesThread] Event flag has been set")

    print("Updating current job in the database")
    update_jobs_record()

    if notif_thread is not None:
        notif_thread.join()

    print("Powering off")

#Periodic report creation
def periodicReport():
    notif_thread_list = []

    #Database ID
    id = 0

    waiting_time = float(config["TIME INTERVAL"]["report"])

    #Define and start cycle
    while not threads_exit_event.is_set(): # Loops while the event flag has not been set
        # The thread will get blocked here unless the event flag is already set, and will break if it set at any time during the timeout
        threads_exit_event.wait(timeout=waiting_time)

        start_timestamp = time.time()

        if not threads_exit_event.is_set(): # Thread could be unblocked in the above line because the event flag has actually been set, not because the time has run out

            #print("[reportThread] The event flag is not set yet, continuing operation")
            print("Sending report...")

            #Call charts creation and send them in the notifications
            id, last_cpu_time = createGraphic(id)
            screenshotAutopsy(mainProcess.pid)
            notif_thread = threading.Thread(target=send_report, args=(smtp_password, last_cpu_time))
            notif_thread.start()
            notif_thread_list.append(notif_thread)

        finish_timestamp = time.time()
        waiting_time = float(config["TIME INTERVAL"]["report"]) - (finish_timestamp - start_timestamp)


    #print("[reportThread] Event flag has been set, powering off")

    for thread in notif_thread_list:
        thread.join()


def freeDiskSpaceValue():
    global disksIter
    diskUsedSpace = {}
    numValues = -1
    for i in disks.values():
        if numValues == -1:
            numValues = len(i)
        else:
            if numValues == len(i):
                continue
            else:
                print("Error getting free disk space")
    for key in disks:
        diskUsedSpace[key] = disks[key][disksIter:numValues]
    disksIter = numValues
    return diskUsedSpace

#CPU, IO and memory charts creation
def createGraphic(id):
    cpuData = retrieve_cpu_values_report(id)
    memoryData = retrieve_memory_values_report(id)
    ioData = retrieve_IO_values_report(id)
    solrData = retrieve_solr_memory_report(id)
    disksFreeSpace = freeDiskSpaceValue()
    cpuUsageGraph("miscellaneous/cpu_usage", cpuData, int(config["CPU USAGE"]["max"]))
    cpuCoresGraph("miscellaneous/cpu_cores", cpuData)
    cpuThreadsGraph("miscellaneous/cpu_threads", cpuData)
    last_cpu_time = cpuTimeGraph("miscellaneous/cpu_time", cpuData)
    ioGraph("miscellaneous/io", ioData)
    memoryUsageGraph("miscellaneous/memory_usage", memoryData, int(config["MEMORY"]["max"]))
    solrMemory("miscellaneous/solr_memory", solrData, solrMaximumMemory())
    freeDiskSpaceGraph("miscellaneous/free_disk_space", disksFreeSpace)
    row = cpuData[len(cpuData) - 1]
    id = int(row[4])
    return id, last_cpu_time

def createGraphicTotal():
    cpuData = retrieve_cpu_values_final()
    memoryData = retrieve_memory_values_final()
    ioData = retrieve_IO_values_final()
    solrData = retrieve_solr_memory_final()
    cpuUsageGraph("miscellaneous/cpu_usage_final", cpuData, int(config["CPU USAGE"]["max"]))
    cpuCoresGraph("miscellaneous/cpu_cores_final", cpuData)
    cpuThreadsGraph("miscellaneous/cpu_threads_final", cpuData)
    last_cpu_time = cpuTimeGraph("miscellaneous/cpu_time_final", cpuData)
    ioGraph("miscellaneous/io_final", ioData)
    memoryUsageGraph("miscellaneous/memory_usage_final", memoryData, int(config["MEMORY"]["max"]))
    solrMemory("miscellaneous/solr_memory_final", solrData, solrMaximumMemory())
    freeDiskSpaceGraph("miscellaneous/free_disk_space_final", disks)
    return last_cpu_time


def terminateReadLogFileThread(readLogFileThread):
    #print("[MainThread] Setting event flag for readLogFileThread")

    readLogFileThread_exit_event.set() # Event flag to signal the thread to finish

    # Wait for the thread to finish
    #print("[MainThread] Event flag set, waiting for the thread to finish")

    readLogFileThread.join()

    #print("[MainThread] readLogFileThread has finished")

def terminateThreads(allThreads):
    #print("[MainThread] Setting event flag for all threads")

    # Event flag to signal the threads to finish
    threads_exit_event.set()

    # Wait for the threads to finish
    #print("[MainThread] Event flag set, waiting for the threads to finish")

    for thread in allThreads:
        thread.join()

    threads_exit_event.clear() # In case a job has finished but the program is not going to terminate

    #print("[MainThread] All threads have finished")

def readLogFile():
    working_directory = config["AUTOPSY CASE"]["working_directory"]

    if working_directory[-1:] != "\\":
        working_directory += "\\"

    log_file = open(working_directory + "Log\\autopsy.log.0", encoding='utf-8')

    has_job_started = False

    while not readLogFileThread_exit_event.is_set(): # Loops while the event flag has not been set
        log_line = log_file.readline()

        if "startIngestJob" in log_line:
            has_job_started = True
            continue
        elif "finishIngestJob" in log_line:
            has_job_started = False

            # Reset the flag
            if ongoing_job_event.is_set(): # There might be jobs that the program has not monitored, since there was a finishIngestJob declaration before reaching EOF
                ongoing_job_event.clear()

            continue
        #If for some reason Autopsy doesn't manage to start the job
        elif "Ingest job" in log_line and "could not be started" in log_line:
            has_job_started = False

            if ongoing_job_event.is_set():
                ongoing_job_event.clear()
                job_error_event.set()
                print("AUTOPSY ERROR DETECTED - the job could not be started")

            continue
        # If it reaches EOF, it returns an empty string; set the ongoing_job flag if there was a startIngestJob declaration and no finishIngestJob one
        elif log_line == "" and has_job_started and not ongoing_job_event.is_set():
            ongoing_job_event.set()

        if log_line == "":
            readLogFileThread_exit_event.wait(1)

    print("Powering off")

    if not log_file.closed:
        log_file.close()


#Upon starting, the script will begin the monitorization and periodic report cicle
def main():
    try:
        errorOccurred = False
        readLogFileThread = threading.Thread(target=readLogFile, name="readLogFileThread")
        readLogFileThread.start()
        checkProcessesThread = None
        reportThread = None

        while not errorOccurred:
            # Check if there's an ongoing job

            print("Waiting for a job to start...")

            while not ongoing_job_event.is_set() and readLogFileThread.is_alive() and mainProcess.is_running():
                time.sleep(0.1)

            if not readLogFileThread.is_alive():
                print("readLogFileThread has stopped unexpectedly, shutting down program...")
                print("Sending email notifying there was an unexpected problem during MonAutopsy's execution")

                sendErrorMailNoData(smtp_password, "MonAutopsy Execution Error", "There was an unexpected MonAutopsy execution error and the program has been terminated.")
                errorOccurred = True

                continue
            elif not mainProcess.is_running():
                print("The main Autopsy process has stopped, shutting down program...")

                print("Sending email notifying Autopsy has terminated unexpectedly")
                sendErrorMailNoData(smtp_password, "Autopsy Termination", "Autopsy has terminated, possibly due to a crash.")

                terminateReadLogFileThread(readLogFileThread)
                errorOccurred = True

                continue

            # At this point, the flag has been set and there are no errors, which means there's an ongoing job
            print("Ongoing job detected")

            add_jobs_record()

            #print("[MainThread] Starting up threads")

            checkProcessesThread = threading.Thread(target=checkProcesses, name="checkProcessesThread")
            reportThread = threading.Thread(target=periodicReport, name="reportThread")
            checkProcessesThread.start()
            reportThread.start()

            #print("[MainThread] All threads have started, going to sleep")

            # Without the following loop, it will leave the try-except block and won't catch any exceptions
            #while True: 
            #    time.sleep(100)

            # Alternative loop that will detect if any of the threads have ended unexpectedly and if the job has finished
            while checkProcessesThread.is_alive() and reportThread.is_alive() and readLogFileThread.is_alive() and ongoing_job_event.is_set() and mainProcess.is_running():
                time.sleep(0.1)

            # If the flag has been reset, which means the job has ended and no errors occured
            if not ongoing_job_event.is_set():
                if not job_error_event.is_set():
                    print("The job has finished")
                    terminateThreads([checkProcessesThread, reportThread])

                    # SEND EMAIL NOTIFYING AUTOPSY JOB HAS ENDED HERE
                    print("Sending email with the final report.")
                    last_cpu_time = createGraphicTotal()
                    notif_thread = threading.Thread(target=send_final_report, args=(smtp_password, last_cpu_time))
                    notif_thread.start()

                else:
                    print("AUTOPSY ERROR - the job could not be started")
                    job_error_event.clear()
                    terminateThreads([checkProcessesThread, reportThread])

                    print("Sending email notifying there was a problem during an Autopsy job execution")

                    notif_thread = threading.Thread(target=sendErrorMailNoData, args=(smtp_password, "Autopsy Job Execution Error", "There was a problem in a Autopsy job execution and it has stopped."))
                    notif_thread.start()

                continue

            # Check if the main Autopsy process stopped

            if not mainProcess.is_running():
                print("The main Autopsy process has stopped, shutting down program...")

                print("Sending email notifying Autopsy has terminated unexpectedly")
                last_cpu_time = createGraphicTotal()
                sendErrorMailWithData(smtp_password, "Autopsy Termination", "Autopsy has terminated, possibly due to a crash.", last_cpu_time)

                terminateThreads([checkProcessesThread, reportThread])
                terminateReadLogFileThread(readLogFileThread)

                errorOccurred = True

                continue

            # If it gets here, it means one or more of the threads has ended unexpectedly

            print("Something unexpected happened, shutting down program...")

            allThreads = []

            if checkProcessesThread.is_alive():
                #print("[MainThread] checkProcessesThread is still running, shutting it down")
                allThreads.append(checkProcessesThread)
            #else:
                #print("[MainThread] checkProcessesThread has stopped unexpectedly")

            if reportThread.is_alive():
                #print("[MainThread] reportThread is still running, shutting it down")
                allThreads.append(reportThread)
            #else:
                #print("[MainThread] reportThread has stopped unexpectedly")

            terminateThreads(allThreads)

            if readLogFileThread.is_alive():
                #print("[MainThread] readLogFileThread is still running, shutting it down")
                terminateReadLogFileThread(readLogFileThread)


            print("Sending email notifying there was an unexpected problem during MonAutopsy's execution")

            # Create charts and send notif
            last_cpu_time = createGraphicTotal()
            sendErrorMailWithData(smtp_password, "MonAutopsy Execution Error", "There was an unexpected MonAutopsy execution error and the program has been terminated.", last_cpu_time)
            errorOccurred = True

        print("Goodbye")

    except KeyboardInterrupt:
        print("CTRL-C detected")

        print("Testing if the threads are running")

        if checkProcessesThread is not None and reportThread is not None and ongoing_job_event.is_set():
            if checkProcessesThread.is_alive() or reportThread.is_alive() or readLogFileThread.is_alive():
                #print("[MainThread] At least one thread is running, shutting them down")
                allThreads = [checkProcessesThread, reportThread]
                terminateThreads(allThreads)
                terminateReadLogFileThread(readLogFileThread)
            #else:
                #print("[MainThread] No thread is running")
        else:
            if readLogFileThread.is_alive():
                #print("[MainThread] There's one thread running, shutting it down")
                terminateReadLogFileThread(readLogFileThread)

        if ongoing_job_event.is_set():
            print("Sending email notifying MonAutopsy has been closed")
            # Create charts and send notif
            last_cpu_time = createGraphicTotal()
            sendErrorMailWithData(smtp_password, "MonAutopsy Termination", "MonAutopsy has been terminated locally.", last_cpu_time)
        print("Goodbye")


#EXECUTION
if __name__ == '__main__':
    main()