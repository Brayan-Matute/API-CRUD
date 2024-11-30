#coonexion.py
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='empleados',
            user='root',
            password=''
        )
        return connection
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None
