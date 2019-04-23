import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from dateutil import parser
from matplotlib import style
from database import retrieve_cpu_values, retrieve_latest_cpu_values, retrieve_memory_values
style.use('fivethirtyeight')

def cpuGraph(process, name):

	data = retrieve_cpu_values()
	times = []
	cpu_usages = []
	date = None
	for row in data:
		date = parser.parse(row[2])
		times.append(date)
		cpu_usages.append(row[1])
	plt.xticks(rotation=25)
	ax = plt.gca()
	xfmt = mdates.DateFormatter('%H:%M:%S')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(times, cpu_usages, label=str(process))
	plt.xlabel("Time")
	plt.ylabel("CPU Usage")
	plt.title("CPU Usage over time (" + str(datetime.datetime.strftime(date, '%d-%m-%Y')) + ")")
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.savefig(name, bbox_inches='tight')
	plt.cla()

#def ioGraph():


def memoryGraph(process, name):
	data = retrieve_memory_values() #Not working yet
	times = []
	cpu_usages = []
	date = None
	for row in data:
		date = parser.parse(row[2])
		times.append(date)
		cpu_usages.append(row[1])
	plt.xticks(rotation=25)
	ax = plt.gca()
	xfmt = mdates.DateFormatter('%H:%M:%S')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(times, cpu_usages, label=str(process))
	plt.xlabel("Time")
	plt.ylabel("Memory Usage")
	plt.title("Memory Usage over time (" + str(datetime.datetime.strftime(date, '%d-%m-%Y')) + ")")
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.savefig(name, bbox_inches='tight')
	plt.cla()