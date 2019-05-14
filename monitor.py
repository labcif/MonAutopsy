#PSUtil doc: https://psutil.readthedocs.io/en/latest/
#threading doc: https://docs.python.org/2/library/threading.html
import psutil, threading, time, configparser
from getpass import getpass
#from arguments import arguments
from modules.database import add_jobs_record, update_jobs_record, add_updates_record, createTables
from modules.database import retrieve_cpu_values_report, retrieve_memory_values_report, retrieve_IO_values_report, retrieve_memory_values_notif, retrieve_cpu_values_notif
from modules.graphics import *
from modules.mail_notif import send_report, check_authentication, send_cpu_notif, send_memory_notif, sendErrorMail
from modules.screenshot import screenshotAutopsy
from modules.ini_validation import iniValidator
import math

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
    authenticated = check_authentication(config["SMTP"]["smtp_server"], config["SMTP"]["sender_email"], smtp_password)

#Usar 'config' para definir todos os intervalos de valores a monitorizar

#Selected process monitorization
PROCNAME = ["autopsy.exe", "autopsy64.exe"]
print("\n-----------------------\n\nProcess: " + str(PROCNAME))
print("\nCPU PERCENT")
mainProcess = None

#Check if process(es) exist and get them in an array
for proc in psutil.process_iter():
	if proc.name() in PROCNAME:
		mainProcess = proc
if mainProcess is None :
	print("No process named "+str(PROCNAME))
	exit(2)


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

#Number of values for the X axis
xNumValues = math.floor(int(config["TIME INTERVAL"]["report"]) / int(config["TIME INTERVAL"]["process"])) + 1
if xNumValues > 11:
    xNumValues = 11


#Process(es) monitorization
def checkProcesses():
    errorOccurred = False
    cpu_occurrences_min = 0
    cpu_occurrences_max = 0
    memory_occurrences_min = 0
    memory_occurrences_max = 0
    notif_thread = None

    while not threads_exit_event.is_set() and not errorOccurred: # Loops while the event flag has not been set
        print("[checkProcessesThread] The event flag is not set yet, continuing operation")
        cpuUsage = 0.0

        processesCPUTimes = []
        processesCPUAfinnity = set() #Unique values only
        processesIOCounters = []
        processesMemoryInfo = []
        totalThreads = 0

        #Try catch here in case the mainProcess dies
        try:
            processes = mainProcess.children(recursive=True) #Get all processes descendants
            processes.append(mainProcess)
        except psutil.NoSuchProcess:
            if not mainProcess.is_running():
                print("All processes are dead!!!")
                errorOccurred = True
                continue

        for proc in processes:
            #Try catch in case some process besides main process dies, this way the execution won't stop due to a secondary process
            try:
                cpuUsage += proc.cpu_percent() / psutil.cpu_count()
                cpuUsage = round(cpuUsage, 2)

                totalThreads += proc.num_threads()

                processesCPUAfinnity.update(proc.cpu_affinity())

                processesCPUTimes.append(proc.cpu_times())
                processesIOCounters.append(proc.io_counters())
                processesMemoryInfo.append(proc.memory_full_info())
            except psutil.NoSuchProcess:
                if not mainProcess.is_running():
                    print("All processes are dead!!!")
                    errorOccurred = True
                    break
                else:
                    print("Something died!")

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

        totalCPUTime = int(totalUserTime + totalSystemTime)

        cpuRecord = (cpuUsage, processesNumCores, totalThreads, totalCPUTime)

        #Getting 1 record of IO, which is the sum of the IO fields of the processes

        totalReadCount = 0
        totalWriteCount = 0
        totalReadBytes = 0
        totalWriteBytes = 0

        for IOCounter in processesIOCounters:
            totalReadCount += IOCounter.read_count
            totalWriteCount += IOCounter.write_count
            totalReadBytes += IOCounter.read_bytes
            totalWriteBytes += IOCounter.write_bytes
        

        IORecord = (totalReadCount, totalWriteCount, totalReadBytes, totalWriteBytes)

        totalMemoryUsage = 0
        totalPageFaults = 0

        for memoryInfo in processesMemoryInfo:
            totalMemoryUsage += memoryInfo.uss
            totalPageFaults += memoryInfo.num_page_faults

        memoryRecord = (totalMemoryUsage, totalPageFaults)

        #Add all the records to the database

        add_updates_record(cpuRecord, IORecord, memoryRecord)

        #Send notifications if...
        if cpuUsage < int(config["CPU USAGE"]["min"], 10):
            if cpu_occurrences_min == int(config["NOTIFICATIONS"]["cpu_usage"]):
                cpu_min_notif_data = retrieve_cpu_values_notif()
                cpuUsageGraph("cpu_notif_min", cpu_min_notif_data, int(config["CPU USAGE"]["min"]), int(config["CPU USAGE"]["max"]), xNumValues)
                lastCpuValue = cpu_min_notif_data[-1][0]
                notif_thread = threading.Thread(target=send_cpu_notif, args=(config, config["SMTP"]["smtp_server"], config["SMTP"]["sender_email"], receivers, smtp_password, lastCpuValue, True))
                notif_thread.start()
                print("[CPU USAGE] NOTIFICATION HERE! PLEASE LET ME KNOW VIA EMAIL!")
                cpu_occurrences_min = 0
            else:
                cpu_occurrences_min += 1
        else:
            cpu_occurrences_min = 0


        if cpuUsage > int(config["CPU USAGE"]["max"], 10):
            if cpu_occurrences_max == int(config["NOTIFICATIONS"]["cpu_usage"]):
                cpu_max_notif_data = retrieve_cpu_values_notif()
                cpuUsageGraph("cpu_notif_max", cpu_max_notif_data, int(config["CPU USAGE"]["min"]), int(config["CPU USAGE"]["max"]), xNumValues)
                lastCpuValue = cpu_max_notif_data[-1][0]
                notif_thread = threading.Thread(target=send_cpu_notif, args=(config, config["SMTP"]["smtp_server"], config["SMTP"]["sender_email"], receivers, smtp_password, lastCpuValue, False))
                notif_thread.start()
                print("[CPU USAGE] NOTIFICATION HERE! PLEASE LET ME KNOW VIA EMAIL!")
                cpu_occurrences_max = 0
            else:
                cpu_occurrences_max += 1
        else:
            cpu_occurrences_max = 0
        #TODO: Create IO anomaly notification and call it here

        if totalMemoryUsage / 1000000 < int(config["MEMORY"]["min"]):
            if memory_occurrences_min == int(config["NOTIFICATIONS"]["memory_usage"]):
                memory_min_notif_data = retrieve_memory_values_notif()
                memoryUsageGraph("memory_notif_min", memory_min_notif_data, int(config["MEMORY"]["min"]), int(config["MEMORY"]["max"]), xNumValues)
                lastMemoryValue = int(memory_min_notif_data[-1][0]) / 1000000
                notif_thread = threading.Thread(target=send_memory_notif, args=(config, config["SMTP"]["smtp_server"], config["SMTP"]["sender_email"], receivers, smtp_password, lastMemoryValue, True))
                notif_thread.start()
                print("[MEMORY USAGE] NOTIFICATION HERE! PLEASE LET ME KNOW VIA EMAIL!")
                memory_occurrences_min = 0
            else:
                memory_occurrences_min += 1
        else:
            memory_occurrences_min = 0

        if totalMemoryUsage / 1000000 > int(config["MEMORY"]["max"]):
            if memory_occurrences_max == int(config["NOTIFICATIONS"]["memory_usage"]):
                memory_max_notif_data = retrieve_memory_values_notif()
                memoryUsageGraph("memory_notif_max", memory_max_notif_data, int(config["MEMORY"]["min"]),int(config["MEMORY"]["max"]), xNumValues)
                lastMemoryValue = int(memory_max_notif_data[-1][0]) / 1000000
                notif_thread = threading.Thread(target=send_memory_notif, args=(config, config["SMTP"]["smtp_server"], config["SMTP"]["sender_email"], receivers, smtp_password, lastMemoryValue, False))
                notif_thread.start()
                print("[MEMORY USAGE] NOTIFICATION HERE! PLEASE LET ME KNOW VIA EMAIL!")
                memory_occurrences_max = 0
            else:
                memory_occurrences_max += 1
        else:
            memory_occurrences_max = 0

        # The thread will get blocked here unless the event flag is already set, and will break if it set at any time during the timeout
        threads_exit_event.wait(timeout=float(config["TIME INTERVAL"]["process"]))

    if not errorOccurred:
        print("[checkProcessesThread] Event flag has been set")

    print("[checkProcessesThread] Updating current job in the database")
    update_jobs_record()

    if notif_thread is not None:
        notif_thread.join()
    
    print("[checkProcessesThread] Powering off")

#Periodic report creation
def periodicReport():
    notif_thread_list = []

    #Database ID
    id = 0

    #Define and start cycle
    while not threads_exit_event.is_set(): # Loops while the event flag has not been set
        # The thread will get blocked here unless the event flag is already set, and will break if it set at any time during the timeout
        threads_exit_event.wait(timeout=float(config["TIME INTERVAL"]["report"]))

        if not threads_exit_event.is_set(): # Thread could be unblocked in the above line because the event flag has actually been set, not because the time has run out
            print("[reportThread] The event flag is not set yet, continuing operation")

            #Call charts creation and send them in the notifications
            id = createGraphic(id)
            screenshotAutopsy(mainProcess.pid)
            notif_thread = threading.Thread(target=send_report, args=(config, config["SMTP"]["smtp_server"], config["SMTP"]["sender_email"], receivers, smtp_password))
            notif_thread.start()
            notif_thread_list.append(notif_thread)

    print("[reportThread] Event flag has been set, powering off")

    for thread in notif_thread_list:
        thread.join()

#CPU, IO and memory charts creation
def createGraphic(id):
    cpuData = retrieve_cpu_values_report(id)
    memoryData = retrieve_memory_values_report(id)
    ioData = retrieve_IO_values_report(id)
    cpuUsageGraph("cpu_usage", cpuData, int(config["CPU USAGE"]["min"]), int(config["CPU USAGE"]["max"]), xNumValues)
    cpuCoresGraph("cpu_cores", cpuData, xNumValues)
    cpuThreadsGraph("cpu_threads", cpuData, xNumValues)
    cpuTimeGraph("cpu_time", cpuData, xNumValues)
    ioGraph("io", ioData, xNumValues)
    memoryUsageGraph("memory_usage", memoryData,int(config["MEMORY"]["min"]), int(config["MEMORY"]["max"]), xNumValues)
    #Verificar se cpuData[len(cpuData) - 1] corresponde ao ultimo id
    row = cpuData[len(cpuData) - 1]
    id = int(row[4]) + 1
    return id

def terminateReadLogFileThread(readLogFileThread):
    print("[MainThread] Setting event flag for readLogFileThread")

    readLogFileThread_exit_event.set() # Event flag to signal the thread to finish

    # Wait for the thread to finish
    print("[MainThread] Event flag set, waiting for the thread to finish")

    readLogFileThread.join()

    print("[MainThread] readLogFileThread has finished")

def terminateThreads(allThreads):
    print("[MainThread] Setting event flag for all threads")

    # Event flag to signal the threads to finish
    threads_exit_event.set() 

    # Wait for the threads to finish
    print("[MainThread] Event flag set, waiting for the threads to finish")
    
    for thread in allThreads:
        thread.join()

    threads_exit_event.clear() # In case a job has finished but the program is not going to terminate

    print("[MainThread] All threads have finished")

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
                print("[readLogFileThread] AUTOPSY ERROR DETECTED - the job could not be started")

            continue
        # If it reaches EOF, it returns an empty string; set the ongoing_job flag if there was a startIngestJob declaration and no finishIngestJob one
        elif log_line == "" and has_job_started and not ongoing_job_event.is_set(): 
            ongoing_job_event.set()
    
    print("[readLogFileThread] Event flag has been set, powering off")

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

            print("[MainThread] Waiting for a job to start")

            while not ongoing_job_event.is_set() and readLogFileThread.is_alive() and mainProcess.is_running():
                time.sleep(0.1)

            if not readLogFileThread.is_alive():
                print("[MainThread] readLogFileThread has stopped unexpectedly, shutting down program...")
                errorOccurred = True
                continue
            elif not mainProcess.is_running():
                print("[MainThread] The main Autopsy process has stopped, shutting down program...")
                terminateReadLogFileThread(readLogFileThread)
                errorOccurred = True
                continue

            # At this point, the flag has been set and there are no errors, which means there's an ongoing job
            print("[MainThread] Ongoing job detected")

            add_jobs_record()

            print("[MainThread] Starting up threads")

            checkProcessesThread = threading.Thread(target=checkProcesses, name="checkProcessesThread")
            reportThread = threading.Thread(target=periodicReport, name="reportThread")
            checkProcessesThread.start()
            reportThread.start()

            print("[MainThread] All threads have started, going to sleep")

            # Without the following loop, it will leave the try-except block and won't catch any exceptions
            #while True: 
            #    time.sleep(100)

            # Alternative loop that will detect if any of the threads have ended unexpectedly and if the job has finished
            while checkProcessesThread.is_alive() and reportThread.is_alive() and readLogFileThread.is_alive() and ongoing_job_event.is_set():
                time.sleep(0.1)

            # If the flag has been reset, which means the job has ended and no errors occured
            if not ongoing_job_event.is_set():
                if not job_error_event.is_set():
                    print("[MainThread] The job has finished, shutting down threads...")
                else:
                    print("[MainThread] AUTOPSY ERROR - the job could not be started, shutting down threads...")
                    job_error_event.clear()

                terminateThreads([checkProcessesThread, reportThread])
                continue

            # If it gets here, it means one or more of the threads has ended unexpectedly

            print("[MainThread] Something unexpected happened, shutting down program...")


            allThreads = []

            if checkProcessesThread.is_alive():
                print("[MainThread] checkProcessesThread is still running, shutting it down")
                allThreads.append(checkProcessesThread)
            else:
                print("[MainThread] checkProcessesThread has stopped unexpectedly")

            if reportThread.is_alive():
                print("[MainThread] reportThread is still running, shutting it down")
                allThreads.append(reportThread)
            else:
                print("[MainThread] reportThread has stopped unexpectedly")

            terminateThreads(allThreads)

            if readLogFileThread.is_alive():
                print("[MainThread] readLogFileThread is still running, shutting it down")
                terminateReadLogFileThread(readLogFileThread)
            
            errorOccurred = True

        print("[MainThread] Goodbye")

    except KeyboardInterrupt:
        print("[MainThread] CTRL-C detected")

        print("[MainThread] Testing if the threads are running")

        if checkProcessesThread is not None and reportThread is not None and ongoing_job_event.is_set():
            if checkProcessesThread.is_alive() or reportThread.is_alive() or readLogFileThread.is_alive(): 
                print("[MainThread] At least one thread is running, shutting them down")
                allThreads = [checkProcessesThread, reportThread]
                terminateThreads(allThreads)
                terminateReadLogFileThread(readLogFileThread)
            else:
                print("[MainThread] No thread is running")
        else:
            if readLogFileThread.is_alive():
                print("[MainThread] There's one thread running, shutting it down")
                terminateReadLogFileThread(readLogFileThread)

        print("[MainThread] Goodbye")
        sendErrorMail(config["SMTP"]["smtp_server"], config["SMTP"]["sender_email"], receivers, smtp_password)

#EXECUTION
if __name__ == '__main__':
	main()