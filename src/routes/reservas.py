import re

from flask import jsonify, request
from ..repositories.database import conexion
from datetime import datetime, timedelta, timezone

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

# endpoint POST /reservas/recurrentes
def reservas_recurrentes_route():
    datos = request.get_json(silent=True)
    campos = {
        "id_socio", "id_cancha", "fecha_hora_inicio",
        "fecha_hora_fin", "cantidad_semanas"
    }

    if not isinstance(datos, dict) or set(datos) != campos:
        return jsonify({"Error": "Se requieren id_socio, id_cancha, "
                        "fecha_hora_inicio, fecha_hora_fin y cantidad_semanas"}), 400

    id_socio = datos["id_socio"]
    id_cancha = datos["id_cancha"]
    semanas = datos["cantidad_semanas"]

    if (type(id_socio) is not int or id_socio <= 0
            or type(id_cancha) is not int or id_cancha <= 0
            or type(semanas) is not int or not 2 <= semanas <= 12):
        return jsonify({"Error": "IDs inválidos o cantidad_semanas fuera de 2 a 12"}), 400

    patron = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}-03:00"

    try:
        texto_inicio = datos["fecha_hora_inicio"]
        texto_fin = datos["fecha_hora_fin"]

        if (not isinstance(texto_inicio, str)
                or not isinstance(texto_fin, str)
                or not re.fullmatch(patron, texto_inicio)
                or not re.fullmatch(patron, texto_fin)):
            raise ValueError()

        inicio = datetime.fromisoformat(texto_inicio)
        fin = datetime.fromisoformat(texto_fin)
    except ValueError:
        return jsonify({"Error": "Las fechas deben tener formato "
                        "YYYY-MM-DDTHH:MM:SS.ffffff-03:00"}), 400

    duracion = fin - inicio
    zona_club = timezone(timedelta(hours=-3))

    if (inicio.date() != fin.date()
            or duracion not in (
                timedelta(hours=1), timedelta(hours=2), timedelta(hours=3)
            )
            or inicio.hour < 8 or fin.hour > 23
            or inicio.minute or inicio.second or inicio.microsecond
            or fin.minute or fin.second or fin.microsecond
            or inicio <= datetime.now(zona_club)):
        return jsonify({"Error": "El intervalo debe ser futuro, durar de 1 a 3 "
                        "horas completas y estar entre las 08:00 y las 23:00"}), 400

    conn = conexion()
    cursor = conn.cursor(dictionary=True)

    try:
        # La transacción permite guardar toda la serie o ninguna reserva.
        conn.start_transaction()

        cursor.execute(
            "SELECT id, activo FROM socios WHERE id = %s FOR UPDATE",
            (id_socio,)
        )
        socio = cursor.fetchone()

        cursor.execute(
            "SELECT id, activa, precio_hora FROM canchas WHERE id = %s FOR UPDATE",
            (id_cancha,)
        )
        cancha = cursor.fetchone()

        if socio is None or cancha is None:
            conn.rollback()
            return jsonify({"Error": "Socio o cancha inexistente"}), 404

        if not socio["activo"] or not cancha["activa"]:
            conn.rollback()
            return jsonify({"Error": "Socio o cancha inactiva"}), 409

        intervalos = []
        conflictos = []

        for numero in range(semanas):
            desde = inicio + timedelta(weeks=numero)
            hasta = fin + timedelta(weeks=numero)

            if desde <= datetime.now(zona_club):
                conn.rollback()
                return jsonify({"Error": "Todas las fechas deben ser futuras"}), 400

            # DATETIME en MySQL guarda la fecha y hora local sin el -03:00.
            desde_sql = desde.replace(tzinfo=None)
            hasta_sql = hasta.replace(tzinfo=None)
            intervalos.append((desde, hasta, desde_sql, hasta_sql))

            cursor.execute(
                """
                SELECT id FROM reservas
                WHERE
                    (
                        (id_cancha = %s AND estado IN ('confirmada', 'bloqueada'))
                        OR (id_socio = %s AND estado = 'confirmada')
                    )
                    AND fecha_hora_inicio < %s
                    AND fecha_hora_fin > %s
                LIMIT 1
                """,
                (id_cancha, id_socio, hasta_sql, desde_sql)
            )

            if cursor.fetchone() is not None:
                conflictos.append(desde.date().isoformat())

        if conflictos:
            conn.rollback()
            return jsonify({
                "Error": "Hay fechas ocupadas; no se creó ninguna reserva",
                "conflictos": conflictos
            }), 409

        precio_hora = cancha["precio_hora"]
        total = precio_hora * (duracion // timedelta(hours=1))
        reservas_creadas = []

        for desde, hasta, desde_sql, hasta_sql in intervalos:
            cursor.execute(
                """
                INSERT INTO reservas
                    (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin,
                     estado, precio_hora, total)
                VALUES (%s, %s, %s, %s, 'confirmada', %s, %s)
                """,
                (id_socio, id_cancha, desde_sql, hasta_sql, precio_hora, total)
            )

            reservas_creadas.append({
                "id": cursor.lastrowid,
                "id_socio": id_socio,
                "id_cancha": id_cancha,
                "fecha_hora_inicio": desde.isoformat(timespec="microseconds"),
                "fecha_hora_fin": hasta.isoformat(timespec="microseconds"),
                "estado": "confirmada",
                "precio_hora": precio_hora,
                "total": total
            })

        conn.commit()
        return jsonify({"reservas": reservas_creadas}), 201

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

