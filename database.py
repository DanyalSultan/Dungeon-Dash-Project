# database.py
global cursor
import psycopg2
from psycopg2 import Error

try:
    # Connect to an existing database
    connection = psycopg2.connect(user="**************",
                                  password="************************************************************",
                                  host="*******************************************************",
                                  port="****",
                                  database="***************")

    cursor = connection.cursor()
    # SQL query to create a new table
    create_table_query = '''CREATE TABLE IF NOT EXISTS Player 
          (ID SERIAL PRIMARY KEY     NOT NULL,
          email     TEXT NOT NULL,
          username           TEXT NOT NULL,
          hashed_password         TEXT NOT NULL,
          high_score         INTEGER NOT NULL); '''
    # Execute a command: this creates a new table
    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL ")

    # Create a cursor to perform database operations
    cursor = connection.cursor()
    # Print PostgreSQL details
    print("PostgreSQL server information")
    print(connection.get_dsn_parameters(), "\n")
    # Executing a SQL query
    cursor.execute("SELECT version();")
    # Fetch result
    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
