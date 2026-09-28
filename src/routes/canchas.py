from flask import jsonify, request
from ..repositories.database import conexion
from datetime import datetime, time

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
    try:
        id = int(id)
    except:
        return {"Error":"Ingrese un numero entero como id"}

    conn = conexion()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM canchas WHERE id = {id};")
    consulta = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(consulta), 200

# endpoint GET/canchas/disponibles
def canchas_disponibles_routes(fecha, hora_inicio, hora_fin, id_deporte, techada):
    if fecha == None or hora_fin == None or hora_inicio == None:
        return jsonify({"Error":"Uno de los parametros obligatorios esta vacio"}), 400

    # Verifica que id_deporte y techada sean correctos
    if id_deporte != None:
        try:
            id_deporte = int(id_deporte)
        except:
            return jsonify({"Error":"id_deporte debe ser un entero"}), 400

    if techada != None:
        try:
            techada = int(techada)
            if techada != 0 and techada !=1:
                return jsonify({"Error":"techada debe ser 1 o 0"}), 400
        except:
            return jsonify({"Error":"techada debe ser 1 o 0"}), 400

    if fecha.count("-") != 2:
            return jsonify({"Error":"Ingrese una fecha valida"}), 400
    if hora_inicio.count(":") != 1 or hora_fin.count(":") != 1:
        return jsonify({"Error":"Ingrese una hora valida"}), 400

    # Verifica que los parametros contengan caracteres validos
    caracteres_validos = "1234567890-:"
    for caracter in fecha:
        if caracter not in caracteres_validos:
            return jsonify({"Error":"Ingrese una fecha valida"}), 400
    for caracter in hora_inicio:
            if caracter not in caracteres_validos:
                return jsonify({"Error":"Ingrese una hora inicial valida"}), 400
    for caracter in hora_fin:
            if caracter not in caracteres_validos:
                return jsonify({"Error":"Ingrese una hora final valida"}), 400

    try: # Conversión a "YYYY-MM-DD HH:MM:SS"
        
        fecha_hora_inicio = f"{fecha} {hora_inicio}"
        fecha_hora_fin = f"{fecha} {hora_fin}"

        dt_inicio = datetime.strptime(fecha_hora_inicio, "%Y-%m-%d %H:%M")
        dt_fin = datetime.strptime(fecha_hora_fin, "%Y-%m-%d %H:%M")     

        # Verifica que las horas sean correctas
        if dt_inicio >= dt_fin:
            return jsonify({"Error": "La hora de inicio debe ser anterior a la hora de finalizacion"}), 400
        diferencia = dt_fin - dt_inicio
        if diferencia.total_seconds() / 3600 > 3:
            return jsonify({"Error": "La diferencia entre horarios no puede ser mayor a 3 horas"}), 400

        # Verifica que el horario sea correcto (entre las 8am y las 11pm)
        apertura = time(8, 0)
        cierre = time(23, 0)
        if not (apertura <= dt_inicio.time() <= cierre and apertura <= dt_fin.time() <= cierre):
            return jsonify({"Error": "El horario debe estar entre las 08:00 y las 23:00"}), 400

        fecha_hora_inicio = dt_inicio.strftime("%Y-%m-%d %H:%M:%S")
        fecha_hora_fin = dt_fin.strftime("%Y-%m-%d %H:%M:%S")

        # Consultas para obtenes las canchas disponibles
        conn = conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT id_cancha
            FROM reservas
            WHERE estado != 'cancelada'
            AND fecha_hora_inicio < %s
            AND fecha_hora_fin > %s
        """, (fecha_hora_fin, fecha_hora_inicio))
        ocupadas = {fila[0] for fila in cursor.fetchall()}

        # Consulta para obtener el id de las canchas y en que deporte
        consulta = "SELECT id FROM canchas WHERE activa = 1"
        params = []

        if id_deporte is not None:
            consulta += " AND id_deporte = %s"
            params.append(id_deporte)

        if techada is not None:
            consulta += " AND techada = %s"
            params.append(techada)

        cursor.execute(consulta, tuple(params))
        todas = {fila[0] for fila in cursor.fetchall()}

        cursor.close()
        conn.close()

        # Devuelve el id de las canchas disponibles
        disponibles = sorted(todas - ocupadas)
        return jsonify({"canchas_disponibles": disponibles}), 200
    except Exception as a:
        return jsonify({"Error":f"Ingrese fecha y horas validos {a}"}), 400

    
# endpoint PATCH/canchas/
def patch_canchas_route(id, nombre, precio_hora, techada, activa):
    # Para ir agregando datos extra a la consulta SQL
    sets_consulta = ""

    # Verifica que el nombre este bien escrito y que no exista otro igual en la tabla de canchas
    caracteres_validos_nombre = "qwertyuiopasdfghjklñzxcvbnmQWERTYUIOPASDFGHJKLÑZXCVBNM1234567890- "
    if nombre != None:
        for caracter in nombre:
            if caracter not in caracteres_validos_nombre:
                return {"Error":"Ingrese un nombre valido"}, 400
        nombre = nombre.strip()
        if nombre == "":
            return {"Error":"Ingrese un nombre valido"}, 400

        conn = conexion()
        cursor = conn.cursor()

        cursor.execute(f"SELECT id FROM canchas WHERE nombre='{nombre}'")
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"Error":"Ya hay una cancha con este nombre"}, 409

        cursor.close()
        conn.close()

        sets_consulta += f"nombre='{nombre}', "
            
    if precio_hora != None:
        try:
            precio_hora = int(precio_hora)
            if precio_hora < 0:
                return {"Error":"El precio_hora es invalido"}, 400
            sets_consulta += f"precio_hora={precio_hora}, "
        except:
            return {"Error":"El precio_hora es invalido"}, 400
        
    if techada != None:
        try:
            techada = int(techada)
        except (ValueError, TypeError):
            return {"Error": "techada debe ser 0 o 1"}, 400
        if techada != 0 and techada != 1:
            return {"Error": "techada debe ser 0 o 1"}, 400
        sets_consulta += f"techada={techada}, "

    if activa != None:
        try:
            activa = int(activa)
        except (ValueError, TypeError):
            return {"Error": "activa debe ser 0 o 1"}, 400
        if activa != 0 and activa != 1:
            return {"Error":"activa debe ser 0 o 1"}, 400
        sets_consulta += f"activa={activa}"

    if sets_consulta == "":
        return {"Error":"No hay ningun parametro"}, 400

    conn = conexion()
    cursor = conn.cursor()

    sets_consulta = sets_consulta.rstrip(", ")
    consulta = f"UPDATE canchas SET {sets_consulta} WHERE id={id}"
    try:
        cursor.execute(consulta)
        conn.commit()
        if cursor.rowcount == 0:
            return {"Error": "La cancha a actualizar no existe o no hay ningun campo a actualizar"}, 404
        return {"TODO BIEN": "Se actualizo correctamente la cancha"}, 200
    finally:
        cursor.close()
        conn.close()


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


