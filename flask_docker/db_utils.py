import time
import mysql.connector
from mysql.connector import Error

def get_db_cursor(db, retries=3, delay=5):
    """
    Function to establish a database cursor with error handling.
    :param db: Database connection instance
    :param retries: Number of retries if connection fails
    :param delay: Delay in seconds between retries
    :return: A database cursor
    """
    for _ in range(retries):
        try:
            return db.cursor(buffered=True)
        except Error as e:
            print(f"Error connecting to database: {e}")
            time.sleep(delay)
            db.reconnect()
    return None

def execute_query(crs, query, data=None, retries=3, delay=5):
    """
    Function to execute a query with error handling.
    :param crs: Cursor instance
    :param query: Query to be executed
    :param data: Data to be inserted in the query, defaults to None
    :param retries: Number of retries if query execution fails
    :param delay: Delay in seconds between retries
    :return: Query execution result
    """
    for _ in range(retries):
        try:
            if data is not None:
                crs.execute(query, data)
            else:
                crs.execute(query)
            return crs
        except Error as e:
            print(f"Error executing query: {e}")
            time.sleep(delay)
    return None