from flask import Flask, request
from src.routes.deportes import *
from src.routes.canchas import *
from src.routes.socios import *
from src.routes.reservas import *
from src.services.parametros import *
from src.routes.bloqueos import *

app = Flask(__name__)

@app.route("/")
def index():
    texto = """
        <div>
        <h3>
        DEPORTES: <br>
        GET/deportes/ <br>
        CANCHAS: <br>
        GET/canchas/ <br>
        GET/canchas/id <br>
        GET/canchas/disponibles <br>
        POST/canchas/ <br>
        PATCH/canchas/id <br>
        DELETE/canchas/id <br>
        SOCIOS: <br>
        GET/socios/ <br>
        GET/socios/id <br>
        POST/socios/ <br>
        PATCH/socios/ <br>
        RESERVAS: <br>
        GET/reservas/ <br>
        POST/reservas <br>
        GET/reservas/id <br>
        PUT/reservas/id/estado <br>
        POST/reservas/recurrentes <br>
        BLOQUEOS: <br>
        POST/bloqueos <br>
        GET/bloqueos <br>
        DELETE/bloqueos/id <br>
        </h3>
        </div>
        """
    return texto

# ENDPOINTS DE DEPORTES
@app.route("/deportes/", methods=["GET"])
def deportes():
    return deportes_routes()

# ENDPOINTS DE CANCHAS
@app.route("/canchas/", methods=["GET"])
def canchas():
    return canchas_routes()

@app.route("/canchas/<int:id>", methods=["GET"])
def canchas_id(id):
    return canchas_id_routes(id)

@app.route("/canchas/", methods=["POST"])
def crear_cancha():
    return crear_cancha_route()

# ENDPOINTS DE SOCIOS
@app.route("/socios/", methods=["GET"])
def socios():
    try:
        limit = int(request.args.get("_limit", 10))
        offset = int(request.args.get("_offset", 0))
    except:
        return jsonify({"Error":"Parametros limit y offset deben ser enteros"}, 400)

    mensaje, codigo = verificar_limit_offset(limit, offset)
    if codigo != 200:
        return jsonify(mensaje), codigo

    return socios_routes(limit, offset)

@app.route("/socios/", methods=["POST"])
def crear_socio():
    return crear_socio_route()

@app.route("/socios/<int:id>", methods=["GET"])
def socios_id(id):
    return socios_id_routes(id)

# ENDPOINTS DE RESERVAS
@app.route("/reservas", methods=["GET"])
def reservas():
    return reservas_routes()

@app.route("/reservas", methods=["POST"])
def crear_reserva():
    try:
        return crear_reserva_route()
    except Exception:
        return respuesta_error(
            "ERROR_INTERNO",
            "Error interno",
            "Ocurrió un error interno al procesar la reserva",
            500
        ) 

@app.route("/reservas/<int:id>", methods=["GET"])
def reservas_id(id):
    return reservas_id_routes(id)

@app.route("/socios/<int:id>", methods=["PATCH"])
def modificar_socio(id):
    return modificar_socio_route(id)

@app.route("/socios/<int:id>", methods=["DELETE"])
def de_baja_socio(id):
    return baja_socio_route(id)

# ENDPOINTS DE BLOQUEOS
@app.route("/bloqueos", methods=["GET"])
def bloqueos():
    return bloqueos_routes()

