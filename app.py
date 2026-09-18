from flask import Flask
from src.routes.deportes import deportes_routes

app = Flask(__name__)

@app.route("/")
def index():
    return "hola mundo"

@app.route("/deportes/")
def deportes():
    return deportes_routes()