from flask import jsonify
from ..repositories.database import conexion

# endpoint GET/reservas
def reservas_routes():
    conn = conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reservas;")
    consulta = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(consulta), 200

# endpoint GET/reservas/<id>
def reservas_id_routes(id):
    conn = conexion()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM reservas WHERE id = {id};")
    consulta = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(consulta), 200