#PSUtil doc: https://psutil.readthedocs.io/en/latest/
#threading doc: https://docs.python.org/2/library/threading.html
import psutil, threading, mail_notif, json, datetime, os
from arguments import arguments
from database import add_cpu_values
from graphics import graphData
import sys

            #Not necessary for the time being:
                #Variables for disk monitorization
                #previousDiskBusyTime = psutil.disk_io_counters().read_time + psutil.disk_io_counters().write_time
                #print(str(previousDiskBusyTime))

#Load JSON File
with open(os.path.dirname(os.path.abspath(__file__)) + '\\config.json') as f:
    config = json.load(f)

#Usar 'config' para definir todos os intervalos de valores a monitorizar

#All processes
print("\nAll processes CPU Times:\n")
print(psutil.cpu_times())
print("\n-----------------------\n\nAll processes virtual memory:\n")
print(psutil.virtual_memory())

#Selected process monitorization (process passed as an argument, ex: 'python monitor.py -p chrome.exe')
PROCNAME = arguments.process
print("\n-----------------------\n\nProcess: " + str(PROCNAME))
print("\nCPU PERCENT")
processes = []
for proc in psutil.process_iter():
	if proc.name() == PROCNAME:
		processes.append(proc)
if len(processes) == 0 :
	print("No process named "+str(PROCNAME))
	exit(2)

cpus_percent = psutil.cpu_percent(percpu=True)
for _ in range(psutil.cpu_count()):
    print("%-10s" % cpus_percent.pop(0), end="")

print()

#-----------------------

processesThread = None
chartsThread = None
reportThread = None


def checkProcesses():
    global processesThread
    try:
        processesThread = threading.Timer(1.0, checkProcesses) #mudar para parametro JSON
        processesThread.start()
        #thread.start()
        
        cpuUsage = 0.0
        #diskUsage = 0.0

        processesIOCounters = []

        for proc in processes:
            cpuUsage += proc.cpu_percent() / psutil.cpu_count()
            cpuUsage = round(cpuUsage, 2)
            processesIOCounters.append(proc.io_counters())

        #Updating the database with 1 record, which is the sum of the fields of the processes

        totalReadCount = 0
        totalWriteCount = 0
        totalReadBytes = 0
        totalWriteBytes = 0

        for IOCounter in processesIOCounters:
            totalReadCount += IOCounter.read_count
            totalWriteCount += IOCounter.write_count
            totalReadBytes += IOCounter.read_bytes
            totalWriteBytes += IOCounter.write_bytes
            
        #Call the function to insert the new record in the database here
        print("Total read count: " + str(totalReadCount))
        print("Total write count: " + str(totalWriteCount))
        print("Total read bytes: " + str(totalReadBytes))
        print("Total write bytes: " + str(totalWriteBytes))

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

        # Enviar mail se...
        #if cpuUsage >= config.cpu_usage.max or cpuUsage <= config.cpu_usage.min:
            #Send a notif plz
        print("Median CPU Usage for " + str(PROCNAME) + " processes = " + str(cpuUsage) + "%")
        values = (cpuUsage, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        add_cpu_values(values)
    except psutil.NoSuchProcess:
        for proc in processes:
            # Remover todos os processos terminados
            if not proc.is_running():
                processes.remove(proc)
        # Se todos os processos terminados
        if len(processes) == 0 :
            print("All processes are dead!!!")
            #thread.cancel()
            processesThread.cancel()
            #Notificacao ao admin

i = 0
def createGraphic():
	threading.Timer(5.0, createGraphic).start()
	global i
	i += 1
	graphData(str(PROCNAME), "test_" + str(i))


#def periodicReport():


def main():
	checkProcesses()
	createGraphic()


if __name__ == '__main__':
	main()