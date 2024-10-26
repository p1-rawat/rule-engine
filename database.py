# app/database.py
import mysql.connector
from mysql.connector import Error

def create_connection():
    """Create a database connection and create the rules table if it doesn't exist."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Your actual username
            password='0503'  # Your actual password
        )

        if connection.is_connected():
            print("Connected to MySQL Server")
            create_database_and_table(connection)

    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def create_database_and_table(connection):
    """Create rules database and table if they don't exist."""
    cursor = connection.cursor()
    
    # Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS rule_engine")
    
    cursor.execute("USE rule_engine")

    # Create rules table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rules (
        id INT AUTO_INCREMENT PRIMARY KEY,
        rule TEXT NOT NULL
    )
    """)
    connection.commit()
    print("Database and table checked/created successfully.")

def insert_rule(connection, rule):
    """Insert a new rule into the rules table and delete the old rule if it exists."""
    if connection is None:
        print("Database connection is not established.")
        return

    cursor = connection.cursor()
    cursor.execute("USE rule_engine") 

    cursor.execute("SELECT rule FROM rules ORDER BY id DESC LIMIT 1")
    old_rule = cursor.fetchone()

    if old_rule:
        merged_rule = f"({old_rule[0]}) OR ({rule})"
        cursor.execute("DELETE FROM rules") 
        cursor.execute("INSERT INTO rules (rule) VALUES (%s)", (merged_rule,))
        print(f"Merged rule inserted: {merged_rule}")
    else:
        cursor.execute("INSERT INTO rules (rule) VALUES (%s)", (rule,))
        print("Rule inserted successfully.")

    connection.commit()

def fetch_rules(connection):
    """Fetch all rules from the rules table."""
    cursor = connection.cursor()
    cursor.execute("USE rule_engine")
    cursor.execute("SELECT rule FROM rules")
    return cursor.fetchall()
