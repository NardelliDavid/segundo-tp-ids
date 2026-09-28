import mysql.connector

def conexion():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_flask"
    )
    return conexion