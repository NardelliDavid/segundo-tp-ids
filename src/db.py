#Conexión a la base de datos

import mysql.connector
from .constants import DB_CONFIG


def obtener_conexion():
    return mysql.connector.connect(**DB_CONFIG)

def ejecutar_consulta(sql, parametros=None):
    conexion=obtener_conexion()
    cursor=conexion.cursor(dictionary=True)
   
    cursor.execute(sql, parametros or {})
    resultado=cursor.fetchall()

    cursor.close()
    conexion.close()

    return resultado
