from flask import jsonify, request
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

# endpoint POST /canchas/
def crear_cancha_route():
    datos = request.get_json()
    
    
    if not datos or "nombre" not in datos or "precio_hora" not in datos or "id_deporte" not in datos:
        return jsonify({"Error": "Faltan datos obligatorios (nombre, precio_hora, id_deporte)"}), 400
        
    nombre = datos["nombre"]
    precio_hora = datos["precio_hora"]
    id_deporte = datos["id_deporte"]
    # Si nos mandan si es techada (1 o 0) lo usamos; si no, por defecto ponemos 0 (No techada)
    techada = datos.get("techada", 0) 

    try:
        conn = conexion()
        cursor = conn.cursor()
        
        query = "INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa) VALUES (%s, %s, %s, %s, 1);"
        cursor.execute(query, (nombre, id_deporte, precio_hora, techada))
        
        conn.commit()
        nuevo_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "Mensaje": "Cancha creada con éxito",
            "Cancha": {
                "id": nuevo_id,
                "nombre": nombre,
                "precio_hora": precio_hora,
                "id_deporte": id_deporte,
                "techada": techada,
                "activa": 1
            }
        }), 201

    except Exception as e:
        return jsonify({"Error": f"No se pudo guardar la cancha: {str(e)}"}), 500

# endpoint DELETE /canchas/<id> (Baja Lógica)
def baja_cancha_route(id):
# valido que el ID de la URL sea un número entero
    try:
        id_cancha = int(id)
    except ValueError:
        return jsonify({"Error": "El ID provisto debe ser un número entero"}), 400

# abro la conexión a tu base de datos de XAMPP
    try:
        conn = conexion()
        cursor = conn.cursor(dictionary=True)
        
# verifico que la cancha realmente existe en la base de datos antes de desactivarla
        cursor.execute("SELECT id FROM canchas WHERE id = %s;", (id_cancha,))
        existe = cursor.fetchone()
        
        if not existe:
            cursor.close()
            conn.close()
            return jsonify({"Error": f"No se encontró ninguna cancha con el ID {id_cancha}"}), 404
            
#ejecuta baja logica: cambiamos activa a 0
        query = "UPDATE canchas SET activa = 0 WHERE id = %s;"
        cursor.execute(query, (id_cancha,))
        
        conn.commit() # Confirmamos el cambio real en el disco de XAMPP
        
        cursor.close()
        conn.close()
        
        return jsonify({"Mensaje": f"Cancha con ID {id_cancha} dada de baja correctamente"}), 200

    except Exception as e:
        return jsonify({"Error": f"Error al procesar la baja de la cancha: {str(e)}"}), 500


