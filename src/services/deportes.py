from src.validators.deportes import validar_peticion_url
from src.repository.deportes import obtener_todos_los_deportes

def mostrar_deportes(request):

    error_validacion=validar_peticion_url(request)
    if error_validacion:
        return error_validacion

    deportes=obtener_todos_los_deportes()
    return deportes
