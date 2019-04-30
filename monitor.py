#PSUtil doc: https://psutil.readthedocs.io/en/latest/
#threading doc: https://docs.python.org/2/library/threading.html
import psutil, threading, mail_notif, json, datetime, os
from getpass import getpass
#from arguments import arguments
from database import add_jobs_record, update_jobs_record, add_updates_record, createTables
from database import retrieve_cpu_values_report, retrieve_memory_values_report, retrieve_IO_values_report
from graphics import cpuUsageGraph, ioGraph, memoryGraph
from mail_notif import send_notif, check_authentication

            #Not necessary for the time being:
                #Variables for disk monitorization
                #previousDiskBusyTime = psutil.disk_io_counters().read_time + psutil.disk_io_counters().write_time
                #print(str(previousDiskBusyTime))

#Load JSON File
with open(os.path.dirname(os.path.abspath(__file__)) + '\\config.json') as f:
    config = json.load(f)
    #TODO: Change to ini file type (easier)

#SMTP Password
smtp_password = getpass(prompt='Enter SMTP password: ')
check_authentication(config["notify"]["SMTPServer"], config["notify"]["senderEmail"], smtp_password)

#Usar 'config' para definir todos os intervalos de valores a monitorizar

#Selected process monitorization
PROCNAME = ["autopsy64.exe"]
#TODO: Change to autopsy64.exe children
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
processesThread = None
reportThread = None


#Database ID
id = 0


#Process(es) monitorization
def checkProcesses():
    global processesThread
    try:
        processesThread = threading.Timer(int(config["time_interval"]["process"]), checkProcesses)
        processesThread.start()
        
        cpuUsage = 0.0

        processesCPUTimes = []
        processesCPUAfinnity = set() #Unique values only
        processesIOCounters = []
        processesMemoryInfo = []
        totalThreads = 0

        processes = mainProcess.children(recursive=True) #Get all processes descendants
        processes.append(mainProcess)
        i=0
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
                    stopThreads()
                    update_jobs_record()
                    print("Something died!")
            except KeyboardInterrupt:
                stopThreads()
                update_jobs_record()


        #Getting 1 record of cpu, which is the sum of the cpu fields of the processes

        processesNumCores = len(processesCPUAfinnity)
        totalUserTime = 0
        totalSystemTime = 0
        #totalIdleTime = 0

        for CPUTimes in processesCPUTimes:
            totalUserTime += CPUTimes.user
            totalSystemTime += CPUTimes.system

        totalCPUTime = totalUserTime + totalSystemTime

        cpuRecord = (cpuUsage, processesNumCores, totalThreads, totalCPUTime, 0)

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
        if cpuUsage > int(config["cpu_usage"]["max"], 10) or cpuUsage < int(config["cpu_usage"]["min"], 10) :
            #TODO: Create CPU usage anomaly and call it here
            print("[CPU USAGE] NOTIFICATION HERE! PLEASE LET ME KNOW VIA EMAIL!")

        #TODO: Create IO and memory anomaly notification and call it here

        if totalMemoryUsage > int(config["memory"]["max"], 10) or totalMemoryUsage < int(config["memory"]["min"]) :
            print("[MEMORY USAGE] NOTIFICATION HERE! PLEASE LET ME KNOW VIA EMAIL!")

    except psutil.NoSuchProcess:
        if not mainProcess.is_running():
            print("All processes are dead!!!")
            stopThreads()
            update_jobs_record()
            # Notificacao ao admin
    except KeyboardInterrupt:
        stopThreads()
        update_jobs_record()


def stopThreads():
    if isinstance(processesThread, threading.Timer) is True:
        processesThread.cancel()
    if isinstance(reportThread, threading.Timer) is True:
        reportThread.cancel()

#Periodic report creation
def periodicReport():
    global reportThread
    #Define and start cicle
    reportThread = threading.Timer(int(config["time_interval"]["report"]), periodicReport)
    reportThread.start()

    #Call charts creation and send them in the notifications
    createGraphic()
    send_notif(config, config["notify"]["SMTPServer"], config["notify"]["senderEmail"], config["notify"]["receiverEmail"], smtp_password)

#CPU, IO and memory charts creation
def createGraphic():
    global id
    cpuData = retrieve_cpu_values_report(id)
    memoryData = retrieve_memory_values_report(id)
    ioData = retrieve_IO_values_report(id)
    cpuUsageGraph("cpu_graph", cpuData, int(config["cpu_usage"]["min"]), int(config["cpu_usage"]["max"]))
    ioGraph("io_graph", ioData)
    memoryGraph("memory_graph", memoryData,int(config["memory"]["min"]), int(config["memory"]["max"]))
    #Verificar se cpuData[len(cpuData) - 1] corresponde ao ultimo id
    row = cpuData[len(cpuData) - 1]
    id = int(row[0]) + 1
    #TODO: Add IO and memory charts


#Upon starting the script will begin the monitorization and period report cicle
def main():
	checkProcesses()
	periodicReport()


#EXECUTION
if __name__ == '__main__':
	main()