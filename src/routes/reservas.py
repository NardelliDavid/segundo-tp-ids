from flask import jsonify, request
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

# endpoint POST /reservas/bloquear
def bloquear_cancha_route():
    datos = request.get_json()
    
# Valido que lleguen los datos para el bloqueo
    if not datos or "id_cancha" not in datos or "fecha_hora_inicio" not in datos or "fecha_hora_fin" not in datos:
        return jsonify({"Error": "Faltan datos obligatorios (id_cancha, fecha_hora_inicio, fecha_hora_fin)"}), 400
        
    id_cancha = datos["id_cancha"]
    fecha_hora_inicio = datos["fecha_hora_inicio"]
    fecha_hora_fin = datos["fecha_hora_fin"]
    
# El precio y el total para un bloqueo de mantenimiento por lógica es 0
    precio_hora = datos.get("precio_hora", 0)
    total = datos.get("total", 0)

    try:
        conn = conexion()
        cursor = conn.cursor()
        
# Inserto en la tabla reservas poniendo estado 'bloqueada'
        query = """
            INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total) 
            VALUES (1, %s, %s, %s, 'bloqueada', %s, %s);
        """
        cursor.execute(query, (id_cancha, fecha_hora_inicio, fecha_hora_fin, precio_hora, total))

        
        conn.commit()
        nuevo_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "Mensaje": "Cancha bloqueada con éxito",
            "Bloqueo": {
                "id_reserva": nuevo_id,
                "id_cancha": id_cancha,
                "fecha_hora_inicio": fecha_hora_inicio,
                "fecha_hora_fin": fecha_hora_fin,
                "estado": "bloqueada"
            }
        }), 201

    except Exception as e:
        return jsonify({"Error": f"No se pudo procesar el bloqueo: {str(e)}"}), 500
# endpoint DELETE /bloqueos/<id>
def eliminar_bloqueo_route(id):
    if id <= 0:
        return jsonify({"Error": "El id debe ser positivo"}), 400

    conn = conexion()
    cursor = conn.cursor()

    try:
        # Solo se puede borrar una fila que realmente sea un bloqueo.
        cursor.execute(
            "DELETE FROM reservas WHERE id = %s AND estado = 'bloqueada'",
            (id,)
        )

        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({"Error": "Bloqueo no encontrado"}), 404

        conn.commit()
        return "", 204

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

