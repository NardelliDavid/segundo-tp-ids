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
    
    datos = request.get_json() #Obtener los datos enviados desde Postman en formato JSON 
    
    if not datos or "nombre" not in datos or "email" not in datos:
        return jsonify({"Error": "Faltan datos obligatorios (nombre y email)"}), 400
        
    nombre = datos["nombre"]
    email = datos["email"].strip().lower() # .lower() asegura que se guarde en minúsculas

    #Conectarse a la base de datos e insertar el nuevo socio
    try:
        conn = conexion()
        cursor = conn.cursor()
        
        
        query = "INSERT INTO socios (nombre, email, activo) VALUES (%s, %s, 1);"
        cursor.execute(query, (nombre, email))
        
        conn.commit() # Confirma los cambios en MySQL
        
        #Obtiene el ID asignado automáticamente
        nuevo_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "Mensaje": "Socio creado con éxito",
            "Socio": {
                "id": nuevo_id,
                "nombre": nombre,
                "email": email,
                "activo": 1
            }
        }), 201

    except Exception as e:
        return jsonify({"Error": f"No se pudo guardar el socio: {str(e)}"}), 500


# endpoint PATCH /socios/<id>
def modificar_socio_route(id):
    datos = request.get_json(silent=True)

    # El cuerpo no puede estar vacío
    if datos is None or datos == {}:
        return jsonify({
            "Error": "El cuerpo no puede estar vacío"
        }), 400

    # Solo se permiten estos campos
    campos_permitidos = {"nombre", "email", "activo"}

    if any(campo not in campos_permitidos for campo in datos):
        return jsonify({
            "Error": "Hay campos desconocidos"
        }), 400

    try:
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

            return jsonify({
                "Error": "Socio no encontrado"
            }), 404

        # Mantener los valores actuales si no fueron enviados
        nombre_final = socio["nombre"]
        email_final = socio["email"]
        activo_final = socio["activo"]

        # Validar nombre
        if "nombre" in datos:
            nombre = datos["nombre"]

            if not isinstance(nombre, str) or not nombre.strip() or not _nombre_valido(nombre.strip()):
                cursor.close()
                conn.close()

                return jsonify({
                    "Error": "El nombre no puede estar vacío o contiene caracteres inválidos"
                }), 400

            nombre_final = nombre.strip()

        # Validar email
        if "email" in datos:
            email = datos["email"]

            if not isinstance(email, str) or not email.strip() or not _email_valido(email.strip()):
                cursor.close()
                conn.close()

                return jsonify({
                    "Error": "El email no puede estar vacío o tiene un formato inválido"
                }), 400

            email_final = email.strip().lower()

            # Verificar que el email no pertenezca a otro socio
            cursor.execute(
                "SELECT id FROM socios WHERE email = %s AND id != %s;",
                (email_final, id)
            )

            if cursor.fetchone():
                cursor.close()
                conn.close()

                return jsonify({
                    "Error": "El email ya está registrado"
                }), 409

        # Validar activo
        if "activo" in datos:
            if not isinstance(datos["activo"], bool):
                cursor.close()
                conn.close()

                return jsonify({
                    "Error": "Activo debe ser true o false"
                }), 400

            activo_final = datos["activo"]

        # Actualizar el socio
        cursor.execute(
            """
            UPDATE socios
            SET nombre = %s, email = %s, activo = %s
            WHERE id = %s;
            """,
            (nombre_final, email_final, activo_final, id)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return "", 204

    except Exception as e:
        return jsonify({
            "Error": f"No se pudo modificar el socio: {str(e)}"
        }), 500
