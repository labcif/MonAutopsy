import sqlite3, os

dirname = os.path.dirname(__file__)
database = dirname + "\\database\\database.db"

#------------DATABASE/TABLES CREATION (EXECUTION)------------
def main():
	dirname = os.path.dirname(__file__)
	database = dirname + "\\database\\database.db"

	sql_create_jobs_table = '''CREATE TABLE IF NOT EXISTS jobs
							(
								id INTEGER PRIMARY KEY AUTOINCREMENT,
								start_time TEXT NOT NULL,
								finish_time TEXT NOT NULL
							)'''

	sql_create_updates_table = '''CREATE TABLE IF NOT EXISTS updates
							(
								id INTEGER PRIMARY KEY AUTOINCREMENT,
								job_id INTEGER NOT NULL,
								timedate TEXT NOT NULL,
								FOREIGN KEY(job_id) REFERENCES jobs(id)
							)'''

	sql_create_cpu_table = ''' CREATE TABLE IF NOT EXISTS cpu
							(
								id INTEGER PRIMARY KEY,
								usage_percentage REAL NOT NULL,
								affinity INTEGER NOT NULL,
								threads INTEGER NOT NULL,
								cpu_time REAL NOT NULL,
								idle_time REAL NOT NULL,
								FOREIGN KEY(id) REFERENCES updates(id)
							)'''

	sql_create_IO_table = '''CREATE TABLE IF NOT EXISTS IO
							(
								id INTEGER PRIMARY KEY,
								read_count INTEGER NOT NULL,
								write_count INTEGER NOT NULL,
								read_bytes INTEGER NOT NULL,
								write_bytes INTEGER NOT NULL,
								FOREIGN KEY(id) REFERENCES updates(id)
							)'''

	sql_create_memory_table = '''CREATE TABLE IF NOT EXISTS memory
							(
								id INTEGER PRIMARY KEY,
								memory_usage INTEGER NOT NULL,
								page_faults INTEGER NOT NULL,
								FOREIGN KEY(id) REFERENCES updates(id)
							)'''

	conn = create_connection(database)
	if conn is not None:
		create_table(conn, sql_create_jobs_table)
		create_table(conn, sql_create_updates_table)
		create_table(conn, sql_create_cpu_table)
		create_table(conn, sql_create_IO_table)
		create_table(conn, sql_create_memory_table)
	else:
		print("Error! cannot create a database connection")


def create_connection(db_file): 
    try:
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

#EXECUTION
if __name__ == "__main__":
	main()

#-------------------------------MODULE PART--------------------------------

#ADDING VALUES TO TABLES
def add_cpu_values(values):
	conn = create_connection(database)
	sql_update_cpu = '''INSERT INTO cpu(cpu_usage,date_time) VALUES(?,?)'''
	try:
		with conn:
			conn.execute(sql_update_cpu, values)
	except sqlite3.Error as e:
		print(e)


#RETRIEVING VALUES FROM TABLES
def retrieve_cpu_values():
	conn = create_connection(database)
	try:
		c = conn.cursor()
		c.execute('''SELECT * FROM cpu''')
		rows = c.fetchall()
		return rows
	except sqlite3.Error as e:
		print(e)


def retrieve_latest_cpu_values():
	conn = create_connection(database)
	try:
		c = conn.cursor()
		c.execute('''SELECT * FROM (SELECT * FROM cpu ORDER BY id DESC LIMIT 10)  ORDER BY id ASC''')
		rows = c.fetchall()
		return rows
	except sqlite3.Error as e:
		print(e)

def retrieve_memory_values():
	conn = create_connection(database)
	#try:
		#c = conn.cursor()
		#c.execute('''(SELECT ''')