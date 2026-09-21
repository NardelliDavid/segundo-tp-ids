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