from src.db import ejecutar_consulta

def obtener_todos_los_deportes():
    sql = 'SELECT id_deporte AS id, nombre FROM deportes'
    return ejecutar_consulta(sql)
 