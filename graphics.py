import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.axes import Axes
from datetime import datetime
from matplotlib import style
from psutil import virtual_memory
import math
style.use('fivethirtyeight')

def cpuUsageGraph(name, data, min, max):
	times = []
	cpu_usages = []
	date = None
	for row in data:
		date = datetime.fromtimestamp(row[8])
		times.append(date)
		cpu_usages.append(math.floor(row[1]))
	plt.xticks(rotation=25)
	ax = plt.gca()
	xfmt = mdates.DateFormatter('%H:%M:%S')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(times, cpu_usages, label="Autopsy")
	plt.axhline(min, label="Minimum CPU Usage", linestyle='--', color='g', linewidth=2)
	plt.axhline(max, label="Maximum CPU Usage", linestyle='--', color='r', linewidth=2)
	plt.xlabel("Time")
	plt.ylabel("CPU Usage (%)")
	plt.ylim(0, 100)
	plt.title("CPU Usage over time (" + str(datetime.strftime(date, '%d-%m-%Y')) + ")")
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.savefig(name, bbox_inches='tight')
	plt.cla()

def ioGraph(name, data):
	times = []
	#io_write_count = []
	#io_read_count = []
	io_read_bytes = []
	io_write_bytes = []
	date = None
	for row in data:
		date = datetime.fromtimestamp(row[7])
		times.append(date)
		#io_read_count.append(row[1])
		#io_write_count.append(row[2])
		io_read_bytes.append(int(row[3]) / 1000000)
		io_write_bytes.append(int(row[4]) / 1000000)
	plt.xticks(rotation=25)
	ax = plt.gca()

	xfmt = mdates.DateFormatter('%H:%M:%S')
	ax.xaxis.set_major_formatter(xfmt)
	#plt.plot(times, io_read_count, label="Autopsy read count")
	#plt.plot(times, io_write_count, label="Autopsy write count")
	plt.plot(times, io_read_bytes, label="Autopsy read MB")
	plt.plot(times, io_write_bytes, label="Autopsy write MB")
	plt.xlabel("Time")
	plt.ylabel("MBytes")
	plt.title("IO Read/Write MBytes (" + str(datetime.strftime(date, '%d-%m-%Y')) + ")")
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.savefig(name, bbox_inches='tight')
	plt.cla()


def memoryGraph(name, data, min, max):
	#Needs pagefaults
	totalMemory = int(virtual_memory()[0]) / 1000000
	times = []
	mem_usages = []
	date = None
	for row in data:
		date = datetime.fromtimestamp(row[5])
		times.append(date)
		mem_usages.append(int(row[1]) / 1000000)
	plt.xticks(rotation=25)
	ax = plt.gca()
	xfmt = mdates.DateFormatter('%H:%M:%S')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(times, mem_usages, label="Autopsy")
	plt.axhline(min, label="Minimum Memory Usage", linestyle='--', color='g', linewidth=2)
	plt.axhline(max, label="Maximum Memory Usage", linestyle='--', color='r', linewidth=2)
	plt.xlabel("Time")
	plt.ylabel("Memory Usage (MB)")
	plt.ylim(0, totalMemory)
	plt.title("Memory Usage over time (" + str(datetime.strftime(date, '%d-%m-%Y')) + ")")
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.savefig(name, bbox_inches='tight')
	plt.cla()