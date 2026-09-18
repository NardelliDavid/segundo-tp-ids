from flask import jsonify
from ..repositories.database import conexion

# endpoint GET/deportes
def deportes_routes():
    conn = conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM deportes")
    consulta = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(consulta)