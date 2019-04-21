import sqlite3, os

dirname = os.path.dirname(__file__)
database = dirname + "\\database\\database.db"

#------------DATABASE/TABLES CREATION (EXECUTION)------------
def main():
	dirname = os.path.dirname(__file__)
	database = dirname + "\\database\\database.db"
	sql_create_cpu_table = ''' CREATE TABLE IF NOT EXISTS cpu (id INTEGER PRIMARY KEY, cpu_usage REAL NOT NULL, date_time TEXT)'''
	conn = create_connection(database)
	if conn is not None:
		create_table(conn, sql_create_cpu_table)
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

#-------------------------------

#ADDING VALUES TO TABLES (MODULE PART)
def add_cpu_values(values):
	conn = create_connection(database)
	sql_update_cpu = '''INSERT INTO cpu(cpu_usage,date_time) VALUES(?,?)'''
	try:
		with conn:
			conn.execute(sql_update_cpu, values)
	except sqlite3.Error as e:
		print(e)

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