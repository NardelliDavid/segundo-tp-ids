from flask import Blueprint, jsonify, request
from src.validators import utils
from src.services.deportes import mostrar_deportes


deportes_bp=Blueprint('deportes', __name__)

@deportes_bp.route('/deportes', methods=['GET'])
def get_deportes():
    deportes = mostrar_deportes(request)

    if isinstance(deportes, dict) and 'errors' in deportes:
        return jsonify(deportes), 400

    if not deportes:
        return '',204
        
    return jsonify({"deportes": deportes}), 200


