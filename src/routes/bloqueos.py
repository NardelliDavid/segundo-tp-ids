from flask import jsonify, request
from ..repositories.database import conexion

# endpoint GET/bloqueos

def bloqueos_routes():
    id_cancha = request.args.get("id_cancha")
    fecha = request.args.get("fecha")
    limit = request.args.get("_limit", 10)
    offset = request.args.get("_offset", 0)

    # Validación de los parámetros numéricos
    try:
        if id_cancha is not None:
            id_cancha = int(id_cancha)

        limit = int(limit)
        offset = int(offset)

    except ValueError:
        return jsonify({
            "errors": [
                {
                    "code": "ERROR_VALIDACION",
                    "message": "Parámetros inválidos",
                    "level": "error",
                    "description": "id_cancha, _limit y _offset deben ser números enteros"
                }
            ]
        }), 400

    # Validación de los límites de paginación
    if limit < 1 or limit > 100 or offset < 0:
        return jsonify({
            "errors": [
                {
                    "code": "ERROR_VALIDACION",
                    "message": "Parámetros inválidos",
                    "level": "error",
                    "description": "_limit debe estar entre 1 y 100 y _offset debe ser mayor o igual a 0"
                }
            ]
        }), 400

    conn = conexion()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM bloqueos WHERE 1=1"
    parametros = []

    # Filtro por cancha
    if id_cancha is not None:
        query += " AND id_cancha = %s"
        parametros.append(id_cancha)

    # Filtro por fecha
    if fecha is not None:
        query += " AND fecha = %s"
        parametros.append(fecha)

    # Paginación
    query += " LIMIT %s OFFSET %s"
    parametros.append(limit)
    parametros.append(offset)

    cursor.execute(query, parametros)
    consulta = cursor.fetchall()

    # Si no se encontraron bloqueos
    if not consulta:
        cursor.close()
        conn.close()
        return "", 204

    # Convertimos fecha y horarios para poder devolverlos como JSON
    for bloqueo in consulta:
        bloqueo["hora_inicio"] = str(bloqueo["hora_inicio"])
        bloqueo["hora_fin"] = str(bloqueo["hora_fin"])
        bloqueo["fecha"] = bloqueo["fecha"].isoformat()

    # Cantidad total de bloqueos para calcular la paginación
    cursor.execute("SELECT COUNT(*) AS total FROM bloqueos")
    total = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    # Cálculo de los offsets de las páginas
    ultimo_offset = ((total - 1) // limit) * limit

    anterior_offset = max(offset - limit, 0)
    siguiente_offset = offset + limit

    # Links de paginación
    links = {
        "_first": {
            "href": f"http://localhost:5000/bloqueos?_offset=0&_limit={limit}"
        },
        "_prev": {
            "href": f"http://localhost:5000/bloqueos?_offset={anterior_offset}&_limit={limit}"
        },
        "_next": {
            "href": f"http://localhost:5000/bloqueos?_offset={siguiente_offset}&_limit={limit}"
        },
        "_last": {
            "href": f"http://localhost:5000/bloqueos?_offset={ultimo_offset}&_limit={limit}"
        }
    }

    # Respuesta según BloqueosListResponse del Swagger
    return jsonify({
        "bloqueos": consulta,
        "_links": links
    }), 200