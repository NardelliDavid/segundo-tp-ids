from src import utils

def validar_peticion_url(request):
    if request.args:
        return utils.construir_error_api(
            code="INVALID_QUERY_PARAMS",
            message="El cuerpo de la solicitud es inválido",
            level="error",
            description="No se aceptan parámetros de consulta"
        )

    if request.get_data():
        return utils.construir_error_api(
            code="invalid_body",
            message="cuerpo no permitido",
            level="error",
            description="GET /deportes no debe incluir cuerpo en la solicitud"
        )     
    return None