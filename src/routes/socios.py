from flask import jsonify,request
from ..repositories.database import conexion
from ..validators.socios import *
from ..services.parametros import generar_links


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
    links = generar_links(request.path, limit, offset, total_registros)

    cursor.close()
    conn.close()

    return jsonify({"Socios":consulta, "_links": links}), 200

# endpoint GET/socios/<id>
def socios_id_routes(id):
    try:
        id = int(id)
    except:
        return jsonify({"Error":"el id no es un numero entero"}), 400

    conn = conexion()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM socios WHERE id = {id};")
    consulta = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(consulta), 200

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
        return jsonify(
            _error("El cuerpo no puede estar vacío")
        ), 400

    # Campos que se pueden modificar
    campos_permitidos = {"nombre", "email", "activo"}

    # Verificar que no lleguen campos desconocidos
    if any(campo not in campos_permitidos for campo in datos):
        return jsonify(
            _error("Hay campos desconocidos")
        ), 400

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

        return jsonify(
            _error(
                "Socio no encontrado",
                code="SOCIO_NO_ENCONTRADO"
            )
        ), 404

    # Mantener el nombre actual si no se envió uno nuevo
    nombre_final = socio["nombre"]

    if "nombre" in datos:
        if not _nombre_valido(datos["nombre"]):
            cursor.close()
            conn.close()

            return jsonify(
                _error("El nombre no puede estar vacío")
            ), 400

        nombre_final = datos["nombre"].strip()

    # Mantener el email actual si no se envió uno nuevo
    email_final = socio["email"]

    if "email" in datos:
        email = (
            datos["email"].strip().lower()
            if isinstance(datos["email"], str)
            else ""
        )

        if not _email_valido(email):
            cursor.close()
            conn.close()

            return jsonify(
                _error("El formato del email es inválido")
            ), 400

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

                return jsonify(
                    _error(
                        "El email ya está registrado",
                        code="EMAIL_DUPLICADO"
                    )
                ), 409

        email_final = email

    # Mantener activo actual si no se envió uno nuevo
    activo_final = socio["activo"]

    if "activo" in datos:
        if not isinstance(datos["activo"], bool):
            cursor.close()
            conn.close()

            return jsonify(
                _error("Activo debe ser true o false")
            ), 400

        activo_final = datos["activo"]

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

    # PATCH exitoso: no devuelve contenido
    return "", 204
