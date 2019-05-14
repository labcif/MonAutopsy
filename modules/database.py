import sqlite3, os, time
dirname = os.path.dirname(os.path.abspath(__file__)).replace("\modules", "")
databaseDir = dirname + "\\database"
database = dirname + "\\database\\database.db"
#------------DATABASE/TABLES CREATION------------
def createTables():

	sql_create_jobs_table = '''CREATE TABLE IF NOT EXISTS jobs
							(
								id INTEGER PRIMARY KEY AUTOINCREMENT,
								start_time INTEGER NOT NULL,
								finish_time INTEGER
							)'''

	sql_create_updates_table = '''CREATE TABLE IF NOT EXISTS updates
							(
								id INTEGER NOT NULL,
								job_id INTEGER NOT NULL,
								update_time INTEGER NOT NULL,
								cpu_usage_percentage REAL NOT NULL,
								num_cores INTEGER NOT NULL,
								threads INTEGER NOT NULL,
								cpu_time INTEGER NOT NULL,
								read_count INTEGER NOT NULL,
								write_count INTEGER NOT NULL,
								read_bytes INTEGER NOT NULL,
								write_bytes INTEGER NOT NULL,
								memory_usage INTEGER NOT NULL,
								page_faults INTEGER NOT NULL,
								FOREIGN KEY(job_id) REFERENCES jobs(id),
								PRIMARY KEY(id, job_id)
							)'''

	#sql_create_cpu_table = ''' CREATE TABLE IF NOT EXISTS cpu
	#						(
	#							id INTEGER PRIMARY KEY,
	#							usage_percentage REAL NOT NULL,
	#							num_cores INTEGER NOT NULL,
	#							threads INTEGER NOT NULL,
	#							cpu_time INTEGER NOT NULL,
	#							idle_time INTEGER NOT NULL,
	#							FOREIGN KEY(id) REFERENCES updates(id)
	#						)'''

	#sql_create_IO_table = '''CREATE TABLE IF NOT EXISTS IO
	#						(
	#							id INTEGER PRIMARY KEY,
	#							read_count INTEGER NOT NULL,
	#							write_count INTEGER NOT NULL,
	#							read_bytes INTEGER NOT NULL,
	#							write_bytes INTEGER NOT NULL,
	#							FOREIGN KEY(id) REFERENCES updates(id)
	#						)'''

	#sql_create_memory_table = '''CREATE TABLE IF NOT EXISTS memory
	#						(
	#							id INTEGER PRIMARY KEY,
	#							memory_usage INTEGER NOT NULL,
	#							page_faults INTEGER NOT NULL,
	#							FOREIGN KEY(id) REFERENCES updates(id)
	#						)'''

	conn = create_connection(database)
	if conn is not None:
		create_table(conn, sql_create_jobs_table)
		create_table(conn, sql_create_updates_table)
		#create_table(conn, sql_create_cpu_table)
		#create_table(conn, sql_create_IO_table)
		#create_table(conn, sql_create_memory_table)
	else:
		print("Error! cannot create a database connection")


def create_connection(db_file):
	try:
		if os.path.isdir(databaseDir) is not True:
			os.mkdir(databaseDir)
		conn = sqlite3.connect(db_file)
		return conn
	except sqlite3.Error as e:
		print(e)

	return None

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

#-------------------------------ADD AND RETRIEVE VALUES FROM DATABASE--------------------------------

#ADDING VALUES TO TABLES
def add_jobs_record():
	start_time = (int(time.time()),)

	conn = create_connection(database)
	c = conn.cursor()
	sqlCommand = '''INSERT INTO jobs(start_time) VALUES(?)'''

	try:
		with conn:
			c.execute(sqlCommand, start_time)
	except sqlite3.Error as e:
		print(e)


def update_jobs_record():
	finish_time = (int(time.time()),)

	conn = create_connection(database)
	c = conn.cursor()
	sqlCommand = '''UPDATE jobs SET finish_time = ? WHERE id = (SELECT MAX(id) FROM jobs)'''

	try:
		with conn:
			c.execute(sqlCommand, finish_time)
	except sqlite3.Error as e:
		print(e)


def add_updates_record(cpu_record, IO_record, memory_record):
	update_timeTuple = (int(time.time()),)

	conn = create_connection(database)
	c = conn.cursor()

	sqlCommand = '''SELECT MAX(id) FROM jobs'''

	#lastRowId = -1

	try:
		with conn:
			c.execute(sqlCommand)

			job_idTuple = (c.fetchone()[0],)

			sqlCommand = '''SELECT MAX(id) FROM updates 
								WHERE job_id = ?'''

			c.execute(sqlCommand, job_idTuple)

			highestIdRow = c.fetchone()
			nextIdTuple = None

			if highestIdRow[0] is None:
				nextIdTuple = (1,)
			else:
				#print(len(highestIdRow))
				#print(highestIdRow[0])
				nextIdTuple = (highestIdRow[0] + 1,) 

			sqlCommand = '''INSERT INTO updates(id, job_id, update_time, cpu_usage_percentage, num_cores, threads, cpu_time, 
							read_count, write_count, read_bytes, write_bytes, memory_usage, page_faults) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)'''

			tupleToFill = nextIdTuple + job_idTuple + update_timeTuple + cpu_record + IO_record + memory_record

			c.execute(sqlCommand, tupleToFill)

		#add_cpu_record(lastRowId, cpu_record)
		#add_IO_record(lastRowId, IO_record)
		#add_memory_record(lastRowId, memory_record)
	except sqlite3.Error as e:
		print(e)

#def add_cpu_record(id, record):
#	idTuple = (id,)
#	record = idTuple + record
#
#	conn = create_connection(database)
#	c = conn.cursor()
#	sqlCommand = '''INSERT INTO cpu(id, usage_percentage, num_cores, threads, cpu_time, idle_time) VALUES(?,?,?,?,?,?)'''
#
#	try:
#		with conn:
#			c.execute(sqlCommand, record)
#	except sqlite3.Error as e:
#		print(e)


#def add_IO_record(id, record):
#	idTuple = (id,)
#	record = idTuple + record
#
#	conn = create_connection(database)
#	c = conn.cursor()
#	sqlCommand = '''INSERT INTO IO(id, read_count, write_count, read_bytes, write_bytes) VALUES(?,?,?,?,?)'''
#
#	try:
#		with conn:
#			c.execute(sqlCommand, record)
#	except sqlite3.Error as e:
#		print(e)


#def add_memory_record(id, record):
#	idTuple = (id,)
#	record = idTuple + record
#
#	conn = create_connection(database)
#	c = conn.cursor()
#	sqlCommand = '''INSERT INTO memory(id, memory_usage, page_faults) VALUES(?,?,?)'''
#
#	try:
#		with conn:
#			c.execute(sqlCommand, record)
#	except sqlite3.Error as e:
#		print(e)

#-----------RETRIEVING VALUES FROM TABLES--------------

#All combined CPU, IO and memory updates
def retrieve_updates(): 
	conn = create_connection(database)

	try:
		c = conn.cursor()
		c.execute('''SELECT * FROM updates''')
		rows = c.fetchall()

		return rows
	except sqlite3.Error as e:
		print(e)

#Certain combined CPU, IO and memory updates, with id >= startId
def retrieve_updates_report(startId):
	idTuple = (startId,)
	conn = create_connection(database)

	try:
		c = conn.cursor()
		c.execute('''SELECT MAX(id) FROM jobs''')

		job_idTuple = (c.fetchone()[0],)

		tuppleToFill = idTuple + job_idTuple

		c.execute('''SELECT * FROM updates 
					WHERE id >= ? AND job_id = ?''', tuppleToFill)
		rows = c.fetchall()

		return rows
	except sqlite3.Error as e:
		print(e)

#All CPU updates
def retrieve_cpu_values(): 
	conn = create_connection(database)

	try:
		c = conn.cursor()
		c.execute('''SELECT cpu_usage_percentage, num_cores, threads, cpu_time, id, job_id, update_time FROM updates''')
		rows = c.fetchall()

		return rows
	except sqlite3.Error as e:
		print(e)


#Certain CPU updates, with id >= startId
def retrieve_cpu_values_report(startId):
	idTuple = (startId,)
	conn = create_connection(database)

	try:
		c = conn.cursor()
		c.execute('''SELECT MAX(id) FROM jobs''')

		job_idTuple = (c.fetchone()[0],)

		tuppleToFill = idTuple + job_idTuple
		
		c.execute('''SELECT cpu_usage_percentage, num_cores, threads, cpu_time, id, job_id, update_time
					FROM updates 
					WHERE id >= ? AND job_id = ?''', tuppleToFill)
		rows = c.fetchall()
		return rows
	except sqlite3.Error as e:
		print(e)


def retrieve_cpu_values_notif():
    conn = create_connection(database)

    try:
        c = conn.cursor()
        c.execute('''SELECT MAX(id) FROM jobs''')

        jobId = (c.fetchone()[0],)

        c.execute('''SELECT cpu_usage_percentage, num_cores, threads, cpu_time, id, job_id, update_time
                    FROM updates
                    WHERE job_id = ?
                    ORDER BY id
                    DESC limit 10''', jobId)

        rows = c.fetchall()

        return rows
    except sqlite3.Error as e:
        print(e)

#All memory updates
def retrieve_IO_values():
	conn = create_connection(database)

	try:
		c = conn.cursor()
		c.execute('''SELECT read_count, write_count, read_bytes, write_bytes, id, job_id, update_time
					FROM updates''')
		rows = c.fetchall()

		return rows
	except sqlite3.Error as e:
		print(e)


#Certain memory updates, with id >= startId
def retrieve_IO_values_report(startId):
	idTuple = (startId,)
	conn = create_connection(database)
	
	try:
		c = conn.cursor()
		c.execute('''SELECT MAX(id) FROM jobs''')

		job_idTuple = (c.fetchone()[0],)

		tuppleToFill = idTuple + job_idTuple

		c.execute('''SELECT read_count, write_count, read_bytes, write_bytes, id, job_id, update_time 
					FROM updates 
					WHERE id >= ? AND job_id = ?''', tuppleToFill)
		rows = c.fetchall()

		return rows
	except sqlite3.Error as e:
		print(e)

#All IO updates
def retrieve_memory_values():
	conn = create_connection(database)

	try:
		c = conn.cursor()
		c.execute('''SELECT memory_usage, page_faults, id, job_id, update_time
					FROM updates''')
		rows = c.fetchall()

		return rows
	except sqlite3.Error as e:
		print(e)

#Certain IO updates, with id >= startId
def retrieve_memory_values_report(startId):
	idTuple = (startId,)
	conn = create_connection(database)

	try:
		c = conn.cursor()
		c.execute('''SELECT MAX(id) FROM jobs''')

		job_idTuple = (c.fetchone()[0],)

		tuppleToFill = idTuple + job_idTuple

		c.execute('''SELECT memory_usage, page_faults, id, job_id, update_time
					FROM updates 
					WHERE id >= ? AND job_id = ?''', tuppleToFill)
		rows = c.fetchall()

		return rows
	except sqlite3.Error as e:
		print(e)


def retrieve_memory_values_notif():
    conn = create_connection(database)

    try:
        c = conn.cursor()
        c.execute('''SELECT MAX(id) FROM jobs''')

        jobId = (c.fetchone()[0],)

        c.execute('''SELECT memory_usage, page_faults, id, job_id, update_time
                    FROM updates
                    WHERE job_id = ?
                    ORDER BY id
                    DESC limit 10''', jobId)

        rows = c.fetchall()

        return rows
    except sqlite3.Error as e:
        print(e)
		