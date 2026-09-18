from flask import Flask
from src.routes.deportes import *
from src.routes.canchas import *
from src.routes.socios import *
from src.routes.reservas import *

app = Flask(__name__)

@app.route("/")
def index():
    texto = """
        <div>
        <h3>
        DEPORTES: <br>
        /deportes/ <br>
        CANCHAS: <br>
        /canchas/ <br>
        /canchas/id <br>
        SOCIOS: <br>
        /socios/ <br>
        RESERVAS: <br>
        /reservas/ <br>
        </h3>
        </div>
        """
    return texto

# ENDPOINTS DE DEPORTES
@app.route("/deportes/")
def deportes():
    return deportes_routes()

# ENDPOINTS DE CANCHAS
@app.route("/canchas/")
def canchas():
    return canchas_routes()

@app.route("/canchas/<int:id>")
def canchas_id(id):
    return canchas_id_routes(id)

# ENDPOINTS DE SOCIOS
@app.route("/socios/")
def socios():
    return socios_routes()

@app.route("/socios/<int:id>")
def socios_id(id):
    return socios_id_routes(id)

# ENDPOINTS DE RESERVAS
@app.route("/reservas/")
def reservas():
    return reservas_routes()

@app.route("/reservas/<int:id>")
def reservas_id(id):
    return reservas_id_routes(id)