from flask import Blueprint, jsonify, request
from src.services.canchas import mostrar_canchas
from src.utils import construir_error_api
from src.validators.canchas import (
    validar_boolean_opcional,
    validar_limit,
    validar_offset                                
)


canchas_bp=Blueprint('canchas', __name__)

@canchas_bp.route('/canchas', methods=['GET'])
def get_canchas():
    
    id_deporte = request.args.get('id_deporte', type=int)
    nombre = request.args.get('nombre', type=str)

    techada = validar_boolean_opcional(request.args.get('techada'), 'techada')
    if isinstance(techada, dict):
        return jsonify(techada), 400
    

    activa = validar_boolean_opcional(request.args.get('activa'), 'activa')
    if isinstance(activa, dict):
        return jsonify(activa), 400

    limit=validar_limit(request.args.get('_limit'))
    if isinstance(limit, dict):
        return jsonify(limit), 400
    
    offset=validar_offset(request.args.get('_offset'))
    if isinstance(offset, dict):
        return jsonify(offset), 400

    canchas=mostrar_canchas(base_url=request.base_url, id_deporte=id_deporte, nombre=nombre, techada=techada, activa=activa, limit=limit, offset=offset)

    if canchas is None:
        return jsonify(construir_error_api(
            code='internal.server.error',
            message='Error interno del servidor',
            description='Ocurrió un error inesperado al procesar la solicitud. Intente nuevamente más tarde.',
            level='error'
        )), 500


    if not canchas["canchas"]:
        return '',204


    return jsonify(canchas), 200