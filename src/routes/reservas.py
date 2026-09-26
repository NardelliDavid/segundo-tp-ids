import re

from flask import jsonify, request
from ..repositories.database import conexion
from datetime import datetime, timedelta, timezone
from ..services.parametros import *

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

# endpoint PUT /reservas/<id>/estado
def modificar_estado_reserva_route(id):
    datos = request.get_json()

    if not datos or "estado" not in datos:
        return jsonify({"Error": "Debe indicar el estado"}), 400

    nuevo_estado = datos["estado"]

    if nuevo_estado not in ["confirmada", "cancelada", "finalizada"]:
        return jsonify({"Error": "Estado desconocido"}), 400

    try:
        conn = conexion()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM reservas WHERE id = %s;",
            (id,)
        )

        reserva = cursor.fetchone()

        if not reserva:
            cursor.close()
            conn.close()
            return jsonify({
                "Error": "No existe una reserva con ese ID"
            }), 404

        estado_actual = reserva["estado"]

        if nuevo_estado == estado_actual:
            cursor.close()
            conn.close()
            return jsonify(reserva), 200

        ahora = datetime.now()

        # confirmada -> cancelada
        if estado_actual == "confirmada" and nuevo_estado == "cancelada":
            if ahora >= reserva["fecha_hora_inicio"]:
                cursor.close()
                conn.close()
                return jsonify({
                    "Error": "No se puede cancelar una reserva cuyo horario ya comenzó"
                }), 409

        # confirmada -> finalizada
        elif estado_actual == "confirmada" and nuevo_estado == "finalizada":
            if ahora < reserva["fecha_hora_fin"]:
                cursor.close()
                conn.close()
                return jsonify({
                    "Error": "La reserva todavía no finalizó"
                }), 409

        # cualquier otra transición
        else:
            cursor.close()
            conn.close()
            return jsonify({
                "Error": "La transición de estado no está permitida"
            }), 409

        cursor.execute(
            "UPDATE reservas SET estado = %s WHERE id = %s;",
            (nuevo_estado, id)
        )

        conn.commit()

        cursor.execute(
            "SELECT * FROM reservas WHERE id = %s;",
            (id,)
        )

        reserva_actualizada = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify(reserva_actualizada), 200

    except Exception as e:
        return jsonify({
            "Error": f"No se pudo modificar el estado: {str(e)}"
        }), 500

# endpoint GET/reservas
def reservas_routes(id_cancha,id_socio,estado,fecha_desde,fecha_hasta,limit,offset):
    condiciones = []
    params = []
 
    # Validación de limit y offset
    try:
        limit = int(limit)
        offset = int(offset)
    except (ValueError, TypeError):
        return jsonify({"error": "_limit y _offset deben ser enteros"}), 400
    if limit < 1 or limit > 100:
        return jsonify({"error": "_limit debe estar entre 1 y 100"}), 400
    if offset < 0:
        return jsonify({"error": "_offset debe ser mayor o igual a 0"}), 400
 
    # Validaciones de los filtros opcionales
    # Si el filtro es valido lo va agregando a condiciones y params
    if id_cancha is not None:
        try:
            params.append(int(id_cancha))
            condiciones.append("id_cancha = %s")
        except (ValueError, TypeError):
            return jsonify({"error": "id_cancha debe ser un entero"}), 400
 
    if id_socio is not None:
        try:
            params.append(int(id_socio))
            condiciones.append("id_socio = %s")
        except (ValueError, TypeError):
            return jsonify({"error": "id_socio debe ser un entero"}), 400
 
    if estado is not None:
        estado = estado.lower().strip()
        if estado not in ("confirmada", "cancelada", "pendiente"):
            return jsonify({"error": "estado debe ser confirmada, cancelada o pendiente"}), 400
        condiciones.append("estado = %s")
        params.append(estado)
 
    if fecha_desde is not None:
        try:
            params.append(datetime.strptime(fecha_desde, "%Y-%m-%d %H:%M:%S"))
            condiciones.append("fecha_hora_inicio >= %s")
        except (ValueError, TypeError):
            return jsonify({"error": "fecha_desde debe tener formato YYYY-MM-DD HH:MM:SS"}), 400
 
    if fecha_hasta is not None:
        try:
            params.append(datetime.strptime(fecha_hasta, "%Y-%m-%d %H:%M:%S"))
            condiciones.append("fecha_hora_fin <= %s")
        except (ValueError, TypeError):
            return jsonify({"error": "fecha_hasta debe tener formato YYYY-MM-DD HH:MM:SS"}), 400
 
    where = " WHERE " + " AND ".join(condiciones) if condiciones else ""
 
    conn = conexion()
    try:
        cursor = conn.cursor()
 
        # Total de registros que cumplen los filtros (para los links)
        cursor.execute(f"SELECT COUNT(*) FROM reservas{where}", params)
        total = cursor.fetchone()[0]
 
        # Página pedida
        cursor.execute(
            f"SELECT * FROM reservas{where} ORDER BY id LIMIT %s OFFSET %s",
            params + [limit, offset],
        )
        items = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()
 
    # Se usan los valores originales de la request (strings), no los datetime parseados
    filtros = {
        "id_cancha": id_cancha,
        "id_socio": id_socio,
        "estado": estado,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
    }
    links = generar_links_reservas(request.base_url, limit, offset, total, filtros)
 
    return jsonify({"_items": items, "_links": links, "_total": total}), 200

# endpoint GET/reservas/<id>
def reservas_id_routes(id):
    try:
        id = int(id)
    except:
        return {"Error":"El id debe ser un numero entero"}, 400
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

# endpoint POST /reservas
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

    campos_permitidos = {
        "id_socio",
        "id_cancha",
        "fecha_hora_inicio",
        "fecha_hora_fin"
    }

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

    cursor.execute(
        "SELECT id, activo FROM socios WHERE id = %s;",
        (id_socio,)
    )
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

    cursor.execute(
        "SELECT id, activa, precio_hora FROM canchas WHERE id = %s;",
        (id_cancha,)
    )
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
