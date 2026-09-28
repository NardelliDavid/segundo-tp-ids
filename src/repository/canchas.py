from src.db import ejecutar_consulta
from src.constants import (
    DEFAULT_LIMIT
)

def listar_canchas(id_deporte=None, nombre=None, techada=None, activa=None, limit=DEFAULT_LIMIT, offset=0):
   

    sql = """
        SELECT
            canchas.id,
            canchas.nombre,
            canchas.id_deporte,
            deportes.nombre AS nombre_deporte,
            canchas.precio_hora,
            (canchas.techada=1) AS techada,
            (canchas.activa=1) AS activa
        FROM canchas
        LEFT JOIN deportes ON canchas.id_deporte=deportes.id_deporte
        WHERE 1=1
    """
    parametros=[]
 
    if id_deporte is not None:
        sql+= ' AND canchas.id_deporte=%s'
        parametros.append(id_deporte)

    if nombre is not None and str(nombre).strip() !='':
        sql+= ' AND LOWER(canchas.nombre) LIKE LOWER(%s)'
        parametros.append(f"%{str(nombre).strip()}%")

    if techada is not None:
        sql+= ' AND canchas.techada=%s'
        parametros.append(techada)

    if activa is not None:
        sql+= ' AND canchas.activa=%s'
        parametros.append(activa)
    
    sql+= ' ORDER BY canchas.id ASC LIMIT %s OFFSET %s;'
    parametros.extend([limit, offset])

    resultados=ejecutar_consulta(sql, parametros)
    if resultados:
        for fila in resultados:
            fila['techada']=bool(fila['techada'])
            fila['activa']=bool(fila['activa'])
    return resultados


def contar_canchas(id_deporte=None, nombre=None, techada=None, activa=None):
    sql = """
        SELECT COUNT(*) AS total
        FROM canchas
        LEFT JOIN deportes ON canchas.id_deporte=deportes.id_deporte
        WHERE 1=1
    """
    parametros = []

    if id_deporte is not None:
        sql += ' AND canchas.id_deporte=%s'
        parametros.append(id_deporte)

    if nombre is not None and nombre.strip() !='':
        sql += ' AND LOWER(canchas.nombre) LIKE LOWER(%s)'
        parametros.append(f"%{nombre.strip()}%")

    if techada is not None:
        sql += ' AND canchas.techada=%s'
        parametros.append(techada)

    if activa is not None:
        sql += ' AND canchas.activa=%s'
        parametros.append(activa)

    resultado = ejecutar_consulta(sql, parametros)
        
    if resultado is None:
        return None
    
    return resultado[0]['total']
    