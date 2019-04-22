#PSUtil doc: https://psutil.readthedocs.io/en/latest/
#threading doc: https://docs.python.org/2/library/threading.html
import psutil, threading, mail_notif, json, datetime, os
from arguments import arguments
from database import add_cpu_values
from graphics import graphData
import sys

#Load JSON File
with open(os.path.dirname(__file__) + '\\config.json') as f:
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

def checkProcesses():
    try:
        thread = threading.Timer(1.0, checkProcesses)
        thread.start()
        usage = 0.0
        for proc in processes:
            usage += proc.cpu_percent() / psutil.cpu_count()
            usage = round(usage, 2)
        # Enviar mail se...
        if usage > config.cpu_usage.max or usage < config.cpu_usage.min :
            #Send a notif plz
        print("Median CPU Usage for " + str(PROCNAME) + " processes = " + str(usage) + "%")
        values = (usage, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        add_cpu_values(values)
    except psutil.NoSuchProcess:
        for proc in processes:
            # Remover todos os processos terminados
            if not proc.is_running():
                processes.remove(proc)
        # Se todos os processos terminados
        if len(processes) == 0 :
            print("All processes are dead!!!")
            thread.cancel()
            #Notificacao ao admin

i = 0
def createGraphic():
	threading.Timer(5.0, createGraphic).start()
	global i
	i += 1
	graphData(str(PROCNAME), "test_" + str(i))


def periodicReport():


def main():
	checkProcesses()
	createGraphic()


if __name__ == '__main__':
	main()