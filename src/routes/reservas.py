from flask import jsonify, request
from ..repositories.database import conexion
from datetime import datetime, timezone, timedelta
import re

def respuesta_error(codigo, mensaje, descripcion, estado_http):
    return jsonify({
        "errors": [
            {
                "code": codigo,
                "message": mensaje,
                "level": "error",
                "description": descripcion
            }
        ]
    }), estado_http

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

 # endpoint POST/reservas
def crear_reserva_route():   
    datos = request.get_json()

    if not isinstance(datos, dict):
        return respuesta_error(
            "ERROR_VALIDACION",
            "Cuerpo inválido",
            "El cuerpo debe ser un objeto JSON",
            400
        )
    if not datos:
        return respuesta_error(
            "ERROR_VALIDACION",
            "Faltan datos",
            "Faltan datos para crear la reserva",
            400  
        )

    if "id_socio" not in datos or "id_cancha" not in datos or "fecha_hora_inicio" not in datos or "fecha_hora_fin" not in datos:
        return respuesta_error(
            "ERROR_VALIDACION",
            "Faltan datos obligatorios",
            "Se deben enviar id_socio, id_cancha, fecha_hora_inicio y fecha_hora_fin",
            400
        )

    campos_permitidos = {"id_socio", "id_cancha", "fecha_hora_inicio", "fecha_hora_fin"}

    if not set(datos.keys()).issubset(campos_permitidos):
        return respuesta_error(
            "ERROR_VALIDACION",
            "Campos no permitidos",
            "Se enviaron campos que no están permitidos para crear una reserva",
            400
        )

    id_socio = datos["id_socio"]
    id_cancha = datos["id_cancha"]
    fecha_hora_inicio = datos["fecha_hora_inicio"]
    fecha_hora_fin = datos["fecha_hora_fin"]

    if not isinstance(fecha_hora_inicio, str) or not isinstance(fecha_hora_fin, str):
        return respuesta_error(
            "ERROR_VALIDACION",
            "Fechas inválidas",
            "Las fechas deben ser cadenas de texto",
            400
        )

    if type(id_socio) is not int or id_socio <= 0:
        return respuesta_error(
            "ERROR_VALIDACION",
            "ID de socio inválido",
            "El id_socio debe ser un entero positivo",
            400
        )

    if type(id_cancha) is not int or id_cancha <= 0:
        return respuesta_error(
            "ERROR_VALIDACION",
            "ID de cancha inválido",
            "El id_cancha debe ser un entero positivo",
            400
        )

    conn = conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT id, activo FROM socios WHERE id = %s;", (id_socio,))
    socio = cursor.fetchone()

    if socio is None:
        cursor.close()
        conn.close()
        return respuesta_error(
            "SOCIO_NO_ENCONTRADO",
            "Socio no encontrado",
            "No existe un socio con el id indicado",
            404
        )

    if not socio[1]:
        cursor.close()
        conn.close()
        return respuesta_error(
            "SOCIO_INACTIVO",
            "Socio inactivo",
            "El socio indicado está inactivo y no puede realizar nuevas reservas",
            409
        )

    cursor.execute("SELECT id, activa, precio_hora FROM canchas WHERE id = %s;", (id_cancha,))
    cancha = cursor.fetchone()

    if cancha is None:
        cursor.close()
        conn.close()
        return respuesta_error(
            "CANCHA_NO_ENCONTRADA",
            "Cancha no encontrada",
            "No existe una cancha con el id indicado",
            404
        )

    if not cancha[1]:
        cursor.close()
        conn.close()
        return respuesta_error(
            "CANCHA_INACTIVA",
            "Cancha inactiva",
            "La cancha indicada está inactiva y no puede recibir nuevas reservas",
            409
        )

    patron_fecha = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}-03:00$" 


    if not re.fullmatch(patron_fecha, fecha_hora_inicio) or not re.fullmatch(patron_fecha, fecha_hora_fin):
        cursor.close()
        conn.close()
        return respuesta_error(
            "ERROR_VALIDACION",
            "Formato de fecha inválido",
            "La fecha y hora no tienen el formato requerido",
            400
        )

    try:
        inicio = datetime.fromisoformat(fecha_hora_inicio)
        fin = datetime.fromisoformat(fecha_hora_fin)
    except ValueError:
        cursor.close()
        conn.close()
        return respuesta_error(
            "ERROR_VALIDACION",
            "Formato de fecha inválido",
            "La fecha y hora ingresadas no son válidas",
            400
        )

    if inicio >= fin:
        cursor.close()
        conn.close()
        return respuesta_error(
            "ERROR_VALIDACION",
            "Horario inválido",
            "La fecha de inicio debe ser anterior a la fecha de fin",
            400
        )

    if inicio.date() != fin.date():
        cursor.close()
        conn.close()
        return respuesta_error(
            "ERROR_VALIDACION",
            "Fechas inválidas",
            "La reserva no puede cruzar la medianoche",
            400
        )

    if inicio.minute != 0 or inicio.second != 0 or inicio.microsecond != 0 or fin.minute != 0 or fin.second != 0 or fin.microsecond != 0:
        cursor.close()
        conn.close()
        return respuesta_error(
            "ERROR_VALIDACION",
            "Horario inválido",
            "La reserva debe comenzar y finalizar en una hora exacta",
            400
        )
    
    if inicio.hour < 8 or fin.hour > 23:
        cursor.close()
        conn.close()
        return respuesta_error(
            "ERROR_VALIDACION",
            "Horario fuera de rango",
            "La reserva debe estar dentro del horario del club de 08:00 a 23:00",
            400
        )

    duracion = (fin - inicio).total_seconds() / 3600
    
    if duracion < 1 or duracion > 3:
        cursor.close()
        conn.close()
        return respuesta_error(
            "ERROR_VALIDACION",
            "Duración inválida",
            "La reserva debe durar entre 1 y 3 horas",
            400
        )

    ahora = datetime.now(timezone(timedelta(hours=-3)))

    if inicio <= ahora:
        cursor.close()
        conn.close()
        return respuesta_error(
            "ERROR_VALIDACION",
            "Fecha inválida",
            "La reserva debe comenzar en una fecha futura",
            400
        )

    cursor.execute("""
    SELECT id FROM reservas
    WHERE id_cancha = %s
    AND estado = 'confirmada'
    AND fecha_hora_inicio < %s
    AND fecha_hora_fin > %s;
""", (id_cancha, fin, inicio))

    reserva_cancha = cursor.fetchone()

    if reserva_cancha is not None:
        cursor.close()
        conn.close()
        return respuesta_error(
            "CONFLICTO_RESERVA",
            "Cancha no disponible",
            "La cancha ya tiene una reserva confirmada en ese horario",
            409
        )

    cursor.execute("""
    SELECT id FROM reservas
    WHERE id_socio = %s
    AND estado = 'confirmada'
    AND fecha_hora_inicio < %s
    AND fecha_hora_fin > %s;
""", (id_socio, fin, inicio))

    reserva_socio = cursor.fetchone()
    

    if reserva_socio is not None:
        cursor.close()
        conn.close()
        return respuesta_error(
            "CONFLICTO_RESERVA",
            "Socio no disponible",
            "El socio ya tiene una reserva confirmada en ese horario",
            409
        )
        
    precio_hora = cancha[2]
    precio_total = int(precio_hora * duracion)

    query = """
    INSERT INTO reservas
    (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

    cursor.execute(query, (
        id_socio,
        id_cancha,
        inicio,
        fin,
        "confirmada",
        precio_hora,
        precio_total
    
    ))

    conn.commit()
    nuevo_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "id": nuevo_id,
        "id_socio": id_socio,
        "id_cancha": id_cancha,
        "fecha_hora_inicio": fecha_hora_inicio,
        "fecha_hora_fin": fecha_hora_fin,
        "estado": "confirmada",
        "precio_hora": precio_hora,
        "precio_total": precio_total
    }), 201

