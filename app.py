from flask import Flask, request
from src.routes.deportes import deportes_bp
from src.routes.canchas import canchas_bp
from src.constants import BASE_URL

app = Flask(__name__)

app.register_blueprint(deportes_bp, url_prefix=BASE_URL)
app.register_blueprint(canchas_bp, url_prefix=BASE_URL)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
