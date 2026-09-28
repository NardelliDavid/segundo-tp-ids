from flask import jsonify,request
from ..repositories.database import conexion
from ..validators.socios import *
from ..services.parametros import *


# endpoint GET/socios
def socios_routes(limit, offset):
    conn = conexion()
    cursor = conn.cursor(dictionary=True)

    # Parametros opcionales de nombre y activo
    nombre = request.args.get("nombre")
    activo = request.args.get("activo")
    resultado1, resultado2 = validar_nombre_activo(nombre, activo)
    if resultado2 == 400:
        return jsonify(resultado1), resultado2
    else:
        nombre = resultado1
        activo = resultado2

    # Lineas extra para la consulta si corresponde
    extra_consulta = ""
    if nombre != None and activo != None:
        extra_consulta = f"WHERE nombre LIKE '%{nombre}%' AND activo = {activo}"
    elif nombre != None:
        extra_consulta = f"WHERE nombre LIKE '%{nombre}%'"
    elif activo != None:
        extra_consulta = f"WHERE activo = {activo}"

    # Obtengo el total de registros filtrados
    cursor.execute(f"SELECT COUNT(*) AS total FROM socios {extra_consulta};")
    total_registros = cursor.fetchone()["total"]

    # Obtengo los socios paginados
    cursor.execute(f"SELECT * FROM socios {extra_consulta} ORDER BY id ASC LIMIT {limit} OFFSET {offset};")
    consulta = cursor.fetchall()

    # HATEOAS
    links = generar_links_socios(request.path, limit, offset, total_registros)

    cursor.close()
    conn.close()

    return jsonify({"Socios":consulta, "_links": links}), 200


# endpoint GET /socios/<id>
def socios_id_routes(id):
    conn = conexion()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, nombre, email, activo FROM socios WHERE id = %s AND activo = 1;", (id,))
    socio = cursor.fetchone()

    cursor.close()
    conn.close()

    if not socio:
        return jsonify({"Error": "Socio no encontrado"}), 404

    return jsonify(socio), 200


# endpoint POST /socios/
def crear_socio_route():
    datos = request.get_json(silent=True)

    # Verificar que el cuerpo sea un objeto JSON
    if datos is None or not isinstance(datos, dict):
        return jsonify({
            "Error": "El cuerpo de la solicitud es inválido"
        }), 400

    # Rechazar campos desconocidos
    campos_permitidos = {"nombre", "email"}

    if any(campo not in campos_permitidos for campo in datos):
        return jsonify({
            "Error": "Se enviaron campos no permitidos"
        }), 400

    # Verificar campos obligatorios
    if "nombre" not in datos or "email" not in datos:
        return jsonify({
            "Error": "Los campos nombre y email son obligatorios"
        }), 400

    nombre = datos["nombre"]
    email = datos["email"]

    # El nombre no puede quedar vacío
    if not isinstance(nombre, str) or not nombre.strip():
        return jsonify({
            "Error": "El nombre no puede estar vacío"
        }), 400

    nombre = nombre.strip()

    # El email no puede quedar vacío
    if not isinstance(email, str) or not email.strip():
        return jsonify({
            "Error": "El email no puede estar vacío"
        }), 400

    email = email.strip().lower()

    try:
        conn = conexion()
        cursor = conn.cursor(dictionary=True)

        # Verificar si el email ya está registrado
        cursor.execute(
            "SELECT id FROM socios WHERE email = %s;",
            (email,)
        )

        if cursor.fetchone():
            cursor.close()
            conn.close()

            return jsonify({
                "Error": "El email ya está registrado"
            }), 409

        # Crear el socio
        cursor.execute(
            "INSERT INTO socios (nombre, email, activo) VALUES (%s, %s, %s);",
            (nombre, email, 1)
        )

        conn.commit()

        nuevo_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({
            "id": nuevo_id,
            "nombre": nombre,
            "email": email,
            "activo": True
        }), 201

    except Exception as e:
        return jsonify({
            "Error": f"No se pudo guardar el socio: {str(e)}"
        }), 500


# endpoint PATCH /socios/<id>
def modificar_socio_route(id):
    datos = request.get_json(silent=True)

    if datos is None or datos == {}:
        return jsonify({"Error": "El cuerpo no puede estar vacío"}), 400

    # Campos que se pueden modificar
    campos_permitidos = {"nombre", "email", "activo"}

    if any(campo not in campos_permitidos for campo in datos):
        return jsonify({"Error": "Hay campos desconocidos"}), 400

    conn = conexion()
    cursor = conn.cursor(dictionary=True)

    # Verificar que el socio exista
    cursor.execute(
        "SELECT * FROM socios WHERE id = %s;",
        (id,)
    )
    socio = cursor.fetchone()

    if not socio:
        cursor.close()
        conn.close()
        return jsonify({"Error": "Socio no encontrado", "code": "SOCIO_NO_ENCONTRADO"}), 404

    # Mantener el nombre actual si no se envió uno nuevo
    nombre_final = socio["nombre"]

    if "nombre" in datos:

        if not isinstance(datos["nombre"], str) or not datos["nombre"].strip():
            cursor.close()
            conn.close()
            return jsonify({"Error": "El nombre no puede estar vacío"}), 400

        nombre_final = datos["nombre"].strip()

    # Mantener el email actual si no se envió uno nuevo
    email_final = socio["email"]

    if "email" in datos:
        email = (
            datos["email"].strip().lower()
            if isinstance(datos["email"], str)
            else ""
        )


        if not email or "@" not in email:
            cursor.close()
            conn.close()
            return jsonify({"Error": "El formato del email es inválido"}), 400

        # Verificar que el email no pertenezca a otro socio
        if email != socio["email"]:
            cursor.execute(
                "SELECT id FROM socios "
                "WHERE email = %s AND id != %s;",
                (email, id)
            )

            if cursor.fetchone():
                cursor.close()
                conn.close()

                return jsonify({"Error": "El email ya está registrado", "code": "EMAIL_DUPLICADO"}), 409

        email_final = email

    # Mantener activo actual si no se envió uno nuevo
    activo_final = socio["activo"]

    if "activo" in datos:
        if not isinstance(datos["activo"], bool):
            cursor.close()
            conn.close()
            return jsonify({"Error": "Activo debe ser true o false"}), 400

        activo_final = 1 if datos["activo"] else 0

    # Actualizar los datos
    cursor.execute(
        "UPDATE socios "
        "SET nombre = %s, email = %s, activo = %s "
        "WHERE id = %s;",
        (
            nombre_final,
            email_final,
            activo_final,
            id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()


    return "", 204
        