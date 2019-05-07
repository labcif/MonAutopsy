#PSUtil doc: https://psutil.readthedocs.io/en/latest/
#threading doc: https://docs.python.org/2/library/threading.html
import psutil, threading, time, configparser
from getpass import getpass
#from arguments import arguments
from modules.database import add_jobs_record, update_jobs_record, add_updates_record, createTables
from modules.database import retrieve_cpu_values_report, retrieve_memory_values_report, retrieve_IO_values_report
from modules.graphics import cpuUsageGraph, ioGraph, memoryGraph
from modules.mail_notif import send_notif, check_authentication
from modules.screenshot import screenshotAutopsy
from modules.ini_validation import iniValidator

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
    authenticated = check_authentication(config["NOTIFY"]["smtp_server"], config["NOTIFY"]["sender_email"], smtp_password)

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
add_jobs_record()

#Threads declarations
#processesThread = None
#reportThread = None
threads_exit_event = threading.Event()

#Database ID
id = 0


#Process(es) monitorization
def checkProcesses():
    while not threads_exit_event.is_set(): # Loops while the event flag has not been set
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
                return

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
                    return
                else:
                    print("Something died!")

        #Getting 1 record of cpu, which is the sum of the cpu fields of the processes

        processesNumCores = len(processesCPUAfinnity)
        totalUserTime = 0
        totalSystemTime = 0
        #totalIdleTime = 0

        for CPUTimes in processesCPUTimes:
            totalUserTime += CPUTimes.user
            totalSystemTime += CPUTimes.system

        totalCPUTime = totalUserTime + totalSystemTime

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

        # Send mail if...
        if cpuUsage > int(config["CPU USAGE"]["max"], 10) or cpuUsage < int(config["CPU USAGE"]["min"], 10) :
            #TODO: Create CPU usage anomaly and call it here
            print("[CPU USAGE] NOTIFICATION HERE! PLEASE LET ME KNOW VIA EMAIL!")

        #TODO: Create IO and memory anomaly notification and call it here

        if totalMemoryUsage > int(config["MEMORY"]["max"], 10) or totalMemoryUsage < int(config["MEMORY"]["min"]) :
            print("[MEMORY USAGE] NOTIFICATION HERE! PLEASE LET ME KNOW VIA EMAIL!")

        # The thread will get blocked here unless the event flag is already set, and will break if it set at any time during the timeout
        threads_exit_event.wait(timeout=float(config["TIME INTERVAL"]["process"]))

    print("[checkProcessesThread] Event flag has been set, powering off")

#Periodic report creation
def periodicReport():
    notif_thread_list = []

    #Define and start cicle
    while not threads_exit_event.is_set(): # Loops while the event flag has not been set
        # The thread will get blocked here unless the event flag is already set, and will break if it set at any time during the timeout
        threads_exit_event.wait(timeout=float(config["TIME INTERVAL"]["report"]))

        if not threads_exit_event.is_set(): # Thread could be unblocked in the above line because the event flag has actually been set, not because the time has run out
            print("[reportThread] The event flag is not set yet, continuing operation")

            #Call charts creation and send them in the notifications
            createGraphic()
            screenshotAutopsy(mainProcess.pid)
            notif_thread = threading.Thread(target=send_notif, args=(config, config["NOTIFY"]["smtp_server"], config["NOTIFY"]["sender_email"], config["NOTIFY"]["receiver_email"], smtp_password))
            notif_thread.start()
            notif_thread_list.append(notif_thread)

    print("[reportThread] Event flag has been set, powering off")

    for thread in notif_thread_list:
        thread.join()

#CPU, IO and memory charts creation
def createGraphic():
    global id
    cpuData = retrieve_cpu_values_report(id)
    memoryData = retrieve_memory_values_report(id)
    ioData = retrieve_IO_values_report(id)
    cpuUsageGraph("cpu_graph", cpuData, int(config["CPU USAGE"]["min"]), int(config["CPU USAGE"]["max"]))
    ioGraph("io_graph", ioData)
    memoryGraph("memory_graph", memoryData,int(config["MEMORY"]["min"]), int(config["MEMORY"]["max"]))
    #Verificar se cpuData[len(cpuData) - 1] corresponde ao ultimo id
    row = cpuData[len(cpuData) - 1]
    id = int(row[4]) + 1

def terminateThreads(allThreads):
            print("[MainThread] Setting event flag")
            threads_exit_event.set() # Event flag to signal the thread to finish

            # Wait for the threads to finish
            print("[MainThread] Event flag set, waiting on the threads to finish")
            
            for thread in allThreads:
                thread.join()

            print("[MainThread] All threads have finished")

#Upon starting, the script will begin the monitorization and periodic report cicle
def main():
    try:
        print("[MainThread] Starting up threads")

        checkProcessesThread = threading.Thread(target=checkProcesses)
        reportThread = threading.Thread(target=periodicReport)
        checkProcessesThread.start()
        reportThread.start()

        print("[MainThread] All threads have started, going to sleep")

        # Without the following loop, it will leave the try-except block and won't catch any exceptions
        #while True: 
        #    time.sleep(100)

        # Alternative loop that will detect if any of the threads have ended unexpectedly
        while checkProcessesThread.is_alive() and reportThread.is_alive():
            time.sleep(0.1)

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

        print("[MainThread] Updating current job in the database")

        update_jobs_record()
        
        print("[MainThread] Goodbye")

    except KeyboardInterrupt:
        print("[MainThread] CTRL-C detected")

        print("[MainThread] Testing if the threads are running")

        if checkProcessesThread.is_alive() or reportThread.is_alive(): 
            print("[MainThread] At least one thread is running, shutting them down")
            allThreads = [checkProcessesThread, reportThread]
            terminateThreads(allThreads)
        else:
            print("[MainThread] No thread is running")
        
        print("[MainThread] Updating current job in the database")

        update_jobs_record()
        
        print("[MainThread] Goodbye")

#EXECUTION
if __name__ == '__main__':
	main()