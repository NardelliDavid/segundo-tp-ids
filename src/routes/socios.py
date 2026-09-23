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

#endpoint PATCH /socios/<id>
def modificar_socio_route(id):
    #Validamos que el ID de la URL sea un número entero
    try:
        id_socio = int(id)
    except ValueError:
        return jsonify({"Error": "El ID provisto debe ser un número entero"}), 400

    #Atrapamos los datos nuevos que el usuario mandó en el JSON de Postman
    datos = request.get_json()
    if not datos:
        return jsonify({"Error": "No se enviaron datos para modificar"}), 400

    #Abrimos la conexión a tu base de datos de XAMPP
    try:
        conn = conexion()
        cursor = conn.cursor(dictionary=True) #Uso dictionary=True para poder leer los datos comodamente

        #Verifico si el socio realmente existe en la base de datos antes de intentar cambiarlo
        cursor.execute("SELECT * FROM socios WHERE id = %s;", (id_socio,))
        socio_actual = cursor.fetchone()
        
        if not socio_actual:
            cursor.close()
            conn.close()
            return jsonify({"Error": f"No se encontró ningún socio con el ID {id_socio}"}), 404

       
        #Si mandó el nombre, usamos el nuevo; si no lo mandó, dejamos el que ya tenía en la base de datos
        nombre_final = datos.get("nombre", socio_actual["nombre"])
        
        #Si mandó el email, aplicamos el requisito del TP: .strip() y .lower() para guardarlo en minúsculas
        if "email" in datos:
            email_final = datos["email"].strip().lower()
        else:
            email_final = socio_actual["email"]

        #Ejecutamos la orden de actualización (UPDATE) en MySQL
        query = "UPDATE socios SET nombre = %s, email = %s WHERE id = %s;"
        cursor.execute(query, (nombre_final, email_final, id_socio))
        
        conn.commit() #Confirmamos el cambio real en el disco de XAMPP
        
        cursor.close()
        conn.close()
        
        #Devolvemos un mensaje de éxito con los datos como quedaron finalmente
        return jsonify({
            "Mensaje": "Socio modificado con éxito",
            "Socio": {
                "id": id_socio,
                "nombre": nombre_final,
                "email": email_final,
                "activo": socio_actual["activo"]
            }
        }), 200

    except Exception as e:
        return jsonify({"Error": f"No se pudo modificar el socio: {str(e)}"}), 500

    # endpoint DELETE /socios/<id> (Baja Lógica)
def baja_socio_route(id):
    #Valido que el ID de la URL sea un número entero
    try:
        id_socio = int(id)
    except ValueError:
        return jsonify({"Error": "El ID provisto debe ser un número entero"}), 400

    #Abrimos la conexión a tu base de datos de XAMPP
    try:
        conn = conexion()
        cursor = conn.cursor(dictionary=True)
        
        #Verificos si el socio realmente existe en la base de datos antes de desactivarlo
        cursor.execute("SELECT id FROM socios WHERE id = %s;", (id_socio,))
        existe = cursor.fetchone()
        
        if not existe:
            cursor.close()
            conn.close()
            return jsonify({"Error": f"No se encontró ningún socio con el ID {id_socio}"}), 404
            
        #Ejecutamos la BAJA LÓGICA: cambiamos activo a 0
        query = "UPDATE socios SET activo = 0 WHERE id = %s;"
        cursor.execute(query, (id_socio,))
        
        conn.commit() #Confirmamos el cambio real en el disco de XAMPP
        
        cursor.close()
        conn.close()
        
        return jsonify({"Mensaje": f"Socio con ID {id_socio} dado de baja correctamente"}), 200

    except Exception as e:
        return jsonify({"Error": f"Error al procesar la baja: {str(e)}"}), 500
