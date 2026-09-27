from src import utils
from src.constants import (
   DEFAULT_LIMIT,
   MAX_LIMIT,
   MIN_LIMIT
)

def validar_limit(limit_ingresado):
    
    if limit_ingresado is None or str(limit_ingresado).strip() == '':
        return DEFAULT_LIMIT

    limit = utils.validar_entero(limit_ingresado, nombre='_limit')

  
    if isinstance(limit, dict):
        return limit

    
    if limit < MIN_LIMIT or limit > MAX_LIMIT:
        return utils.construir_error_api(
            'invalid._limit.value',
            "Valor de '_limit' invalido",
            'error',
            "El campo '_limit' debe ser un numero entero entre 1 y 100"
        )

    return limit


def validar_offset(offset_ingresado):

    if offset_ingresado is None or str(offset_ingresado).strip() == '':
        return 0

    offset = utils.validar_entero(offset_ingresado, nombre='_offset')

    if isinstance(offset, dict):
        return offset

    if offset < 0:
        return utils.construir_error_api(
            'invalid._offset.value',
            "Valor de '_offset' invalido",
            'error',
            "El campo '_offset' debe ser un numero entero mayor o igual a 0"
        )

    return offset

def validar_boolean_opcional(valor, nombre):
    if valor is None or str(valor).strip() == '':
        return None  # No se aplico el filtro
    
    valor_final= str(valor).strip().lower()
    if valor_final == 'true':
        return True
    elif valor_final == 'false':
        return False

    return utils.construir_error_api(
        code=f'invalid.{nombre}.format',
        message=f"Formato de '{nombre}' invalido",
        type_error='error',
        description=f"El campo '{nombre}' debe ser un booleano (true o false)"
    )