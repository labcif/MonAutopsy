#PSUtil doc: https://psutil.readthedocs.io/en/latest/
#threading doc: https://docs.python.org/2/library/threading.html
import psutil, threading, mail_notif, json, datetime, os
#from arguments import arguments
from database import add_cpu_record, add_IO_record, add_memory_record, createTables
from graphics import cpuGraph
from mail_notif import send_notif, check_authentication

            #Not necessary for the time being:
                #Variables for disk monitorization
                #previousDiskBusyTime = psutil.disk_io_counters().read_time + psutil.disk_io_counters().write_time
                #print(str(previousDiskBusyTime))

#Load JSON File
with open(os.path.dirname(os.path.abspath(__file__)) + '\\config.json') as f:
    config = json.load(f)
    #TODO: JSON parameter validation

#SMTP Password
smtp_password = input("Enter SMTP password: ")
#check_authentication(config["notify"]["SMTPServer"], config["notify"]["senderEmail"], smtp_password)

#Usar 'config' para definir todos os intervalos de valores a monitorizar

#All processes
print("All processes CPU Times:\n")
print(psutil.cpu_times())
print("\n-----------------------\n\nAll processes virtual memory:\n")
print(psutil.virtual_memory())

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
if mainProcess == None :
	print("No process named "+str(PROCNAME))
	exit(2)

#Create database tables
createTables()


#Overall CPU percentage
cpus_percent = psutil.cpu_percent(percpu=True)
for _ in range(psutil.cpu_count()):
    print("%-10s" % cpus_percent.pop(0), end="")

print()

#-----------------------


#Threads declarations
processesThread = None
reportThread = None


#Process(es) monitorization
def checkProcesses():
    global processesThread
    try:
        processesThread = threading.Timer(int(config["time_interval"]["process"]), checkProcesses) #mudar para parametro JSON
        processesThread.start()
        
        cpuUsage = 0.0
        #diskUsage = 0.0

        processesCPUTimes = []
        processesCPUAfinnity = set() #Unique values only
        processesIOCounters = []
        processesMemoryInfo = []
        totalThreads = 0

        processes = mainProcess.children(recursive=True) #Get all processes descendants
        processes.append(mainProcess)

        for proc in processes:
            cpuUsage += proc.cpu_percent() / psutil.cpu_count()
            cpuUsage = round(cpuUsage, 2)

            totalThreads += proc.num_threads()

            processesCPUAfinnity.add(proc.cpu_affinity())

            processesCPUTimes.append(proc.cpu_times())
            processesIOCounters.append(proc.io_counters())
            processesMemoryInfo.append(proc.memory_full_info())



        #Getting 1 record of cpu, which is the sum of the cpu fields of the processes

        processesNumCores = len(processesCPUAfinnity)
        totalUserTime = 0
        totalSystemTime = 0
        totalIdleTime = 0

        #Updating the database with 1 record of IO, which is the sum of the IO fields of the processes

        totalReadCount = 0
        totalWriteCount = 0
        totalReadBytes = 0
        totalWriteBytes = 0

        for IOCounter in processesIOCounters:
            totalReadCount += IOCounter.read_count
            totalWriteCount += IOCounter.write_count
            totalReadBytes += IOCounter.read_bytes
            totalWriteBytes += IOCounter.write_bytes
            
        #print("Total read count: " + str(totalReadCount))
        #print("Total write count: " + str(totalWriteCount))
        #print("Total read bytes: " + str(totalReadBytes))
        #print("Total write bytes: " + str(totalWriteBytes))



                        #Not working as expected:
                            #In milliseconds (supposedly, might be in nanoseconds)
                            #diskIOCounters = psutil.disk_io_counters()
                            #global previousDiskBusyTime

                            #diskBusyTime = diskIOCounters.read_time + diskIOCounters.write_time
                            #diskUsage = round((diskBusyTime - previousDiskBusyTime) / 1000 * 100,  5)
                            #diskBusyTimeDifference = diskBusyTime - previousDiskBusyTime
                            #previousDiskBusyTime = diskBusyTime

                            #print("Disk usage: " + str(diskUsage) + "%")
                            #print("DiskBusyTime: " + str(diskBusyTimeDifference))

        #Updating the database with 1 record of memory, which is the sum of the memory fields of the processes

        totalMemoryUsage = 0
        totalPageFaults = 0

        for memoryInfo in processesMemoryInfo:
            totalMemoryUsage += memoryInfo.uss
            totalPageFaults += memoryInfo.num_page_faults

        #print("Total memory usage: " + str(totalMemoryUsage))
        #print("Total page faults: " + str(totalPageFaults))

        #Add CPU information to database
        #TODO: Check affinity and threads for autopsy and photorek and join them (hardcoded for now)
        #---WAITING FOR DATABASE METHODS---
        #values = (cpuUsage, ..., ..., ..., ..., ...)
        #add_cpu_values(values)

        # Send mail if...
        if cpuUsage > int(config["cpu_usage"]["max"], 10) or cpuUsage < int(config["cpu_usage"]["min"], 10) :
            #TODO: Create CPU usage anomaly and call it here
            print("NOTIFICATION HERE! PLEASE LET ME KNOW VIA EMAIL!")

        #TODO: Create IO and memory anomaly notification and call it here

        #print("Median CPU Usage for " + str(PROCNAME) + " processes = " + str(cpuUsage) + "%")

    except psutil.NoSuchProcess:
        for proc in processes:

            #Remove processes not running anymore
            if not proc.is_running():
                processes.remove(proc)

        #If there are no remaining processes
        if len(processes) == 0 :
            print("All processes are dead!!!")
            stopThreads()
            #Notificacao ao admin


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
    send_notif(config["notify"]["SMTPServer"], config["notify"]["senderEmail"], config["notify"]["receiverEmail"], smtp_password)

#CPU, IO and memory charts creation
def createGraphic():
    cpuGraph(str(PROCNAME), "cpu_graph")
    #TODO: Add IO and memory charts


#Upon starting the script will begin the monitorization and period report cicle
def main():
	checkProcesses()
	periodicReport()


#EXECUTION
if __name__ == '__main__':
	main()