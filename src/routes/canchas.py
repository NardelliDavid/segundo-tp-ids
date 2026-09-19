from flask import jsonify
from ..repositories.database import conexion

# endpoint GET/canchas
def canchas_routes():
    conn = conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM canchas;")
    consulta = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(consulta), 200

# endpoint GET/canchas/<id>
def canchas_id_routes(id):
    conn = conexion()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM canchas WHERE id = {id};")
    consulta = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(consulta), 200
