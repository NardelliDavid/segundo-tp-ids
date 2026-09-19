from flask import jsonify
from ..repositories.database import conexion

# endpoint GET/socios
def socios_routes():
    conn = conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM socios;")
    consulta = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(consulta), 200

# endpoint GET/socios/<id>
def socios_id_routes(id):
    conn = conexion()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM socios WHERE id = {id};")
    consulta = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(consulta), 200