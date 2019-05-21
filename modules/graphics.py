import matplotlib
matplotlib.use('Agg') # Fixes a runtime error (related to tkinter and it's execution not being in the main thread)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from matplotlib import style
from psutil import virtual_memory
import math, numpy as np
from collections import deque
style.use('fivethirtyeight')
#TODO: Median values in graphics
#
def cpuUsageGraph(name, data, max, xNumValues):
	times = []
	cpu_usages = []
	date = None
	for row in data:
		date = datetime.fromtimestamp(row[6])
		times.append(date)
		cpu_usages.append(math.floor(row[0]))
	ax = plt.gca()
	xfmt = mdates.DateFormatter('%H:%M:%S')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(times, cpu_usages, label="Autopsy", linewidth=0.7)
	plt.xticks(times, rotation=25)
	plt.locator_params(axis='x', nbins=xNumValues)
	plt.axhline(max, label="Maximum CPU Usage ({}%)".format(max), linestyle='--', color='r', linewidth=2)
	plt.xlabel("Time")
	plt.ylabel("CPU Usage (%)")
	plt.ylim(0, 100)
	plt.title("CPU Usage (" + str(datetime.strftime(date, '%d-%m-%Y')) + ")")
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.savefig(name, bbox_inches='tight')
	plt.cla()

def cpuCoresGraph(name, data, xNumValues):
	times = []
	cpu_cores = []
	date = None
	for row in data:
		date = datetime.fromtimestamp(row[6])
		times.append(date)
		cpu_cores.append(math.floor(row[1]))
	plt.xticks(times, rotation=25)
	ax = plt.gca()
	xfmt = mdates.DateFormatter('%H:%M:%S')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(times, cpu_cores, label="Autopsy", linewidth=0.7)
	plt.locator_params(axis='x', nbins=xNumValues)
	plt.xlabel("Time")
	plt.ylabel("CPU cores")
	plt.yticks(list(range(0, 21, 4)))
	plt.title("CPU affinity number (" + str(datetime.strftime(date, '%d-%m-%Y')) + ")")
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.savefig(name, bbox_inches='tight')
	plt.cla()

def cpuThreadsGraph(name, data, xNumValues):
	times = []
	cpu_threads = []
	date = None
	for row in data:
		date = datetime.fromtimestamp(row[6])
		times.append(date)
		cpu_threads.append(math.floor(row[2]))
	plt.xticks(times, rotation=25)
	ax = plt.gca()
	xfmt = mdates.DateFormatter('%H:%M:%S')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(times, cpu_threads, label="Autopsy", linewidth=0.7)
	plt.locator_params(axis='x', nbins=xNumValues)
	plt.xlabel("Time")
	plt.ylabel("CPU threads (%)")
	#plt.ylim(0, 100)
	plt.title("CPU threads (" + str(datetime.strftime(date, '%d-%m-%Y')) + ")")
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.savefig(name, bbox_inches='tight')
	plt.cla()

def cpuTimeGraph(name, data, xNumValues):
	times = []
	cpu_times = []
	date = None
	for row in data:
		date = datetime.fromtimestamp(row[6])
		times.append(date)
		cpu_times.append(math.floor(row[3]))
	plt.xticks(times, rotation=25)
	ax = plt.gca()
	xfmt = mdates.DateFormatter('%H:%M:%S')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(times, cpu_times, label="Autopsy", linewidth=0.7)
	plt.locator_params(axis='x', nbins=xNumValues)
	plt.xlabel("Time")
	plt.ylabel("CPU time (seconds)")
	#plt.ylim(0, 100)
	plt.title("CPU time (" + str(datetime.strftime(date, '%d-%m-%Y')) + ")")
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.savefig(name, bbox_inches='tight')
	plt.cla()

def ioGraph(name, data):
	times = []
	io_read_bytes = []
	io_read_MBs = []
	io_write_bytes = []
	io_write_MBs = []
	date = None
	for row in data:
		date = datetime.fromtimestamp(row[6])
		times.append(date)
		io_read_bytes.append(int(row[2]))
		io_write_bytes.append(int(row[3]))

	for i in range(0, len(io_write_bytes) - 1):
		io_write_MBs.append(abs(math.floor((io_write_bytes[i+1] - io_write_bytes[i]) * 0.000000953674)))

	for i in range(0, len(io_read_bytes) - 1):
		io_read_MBs.append(abs(math.floor((io_read_bytes[i+1] - io_read_bytes[i]) * 0.000000953674)))

	x = deque(times)
	x.popleft()
	x = list(x)

	#plt.xticks(rotation=25)
	ax = plt.gca()
	xfmt = mdates.DateFormatter('%H:%M:%S')
	ax.xaxis.set_major_formatter(xfmt)
	#plt.plot(times, io_read_count, label="Autopsy read count")
	#plt.plot(times, io_write_count, label="Autopsy write count")
	plt.plot(x, io_read_MBs, label="Autopsy read MB/s", linewidth=0.7)
	plt.plot(x, io_write_MBs, label="Autopsy write MB/s", linewidth=0.7)
	plt.ylim(bottom=0)
	plt.xlabel("Time")
	plt.ylabel("MB/s")
	plt.title("IO read/write MBytes (" + str(datetime.strftime(date, '%d-%m-%Y')) + ")")
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.gcf().autofmt_xdate()
	plt.savefig(name, bbox_inches='tight')
	plt.cla()


def memoryUsageGraph(name, data, max, xNumValues):
	#Needs pagefaults
	totalMemory = int(virtual_memory()[0]) / 1000000
	times = []
	mem_usages = []
	date = None
	for row in data:
		date = datetime.fromtimestamp(row[4])
		times.append(date)
		mem_usages.append(int(row[0]) / 1000000)
	plt.xticks(times, rotation=25)
	ax = plt.gca()
	xfmt = mdates.DateFormatter('%H:%M:%S')
	ax.xaxis.set_major_formatter(xfmt)
	plt.plot(times, mem_usages, label="Autopsy", linewidth=0.7)
	plt.locator_params(axis='x', nbins=xNumValues)
	plt.axhline(max, label="Maximum Memory Usage ({}MB)".format(max), linestyle='--', color='r', linewidth=2)
	plt.xlabel("Time")
	plt.ylabel("Memory usage (MB)")
	plt.ylim(0, totalMemory)
	plt.title("Memory usage (" + str(datetime.strftime(date, '%d-%m-%Y')) + ")")
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.savefig(name, bbox_inches='tight')
	plt.cla()