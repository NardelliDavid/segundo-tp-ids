

def construir_error_api(code, message, level, description):
    """Construye la estructura de error con el servidor"""
    return {
        'errors': [{
            'code': code,
            'message': message,
            'level': level,
            'description': description
        }]
    }

def generar_links_hateoas(base_url, limit, offset, total_registros):
    # Usamos la división entera de tu compañero para un _last preciso
    last_offset = ((total_registros - 1) // limit) * limit if total_registros > 0 else 0

    # Usamos la estructura {"href": ...} exigida por la cátedra
    links = {
        "_first": {"href": f"{base_url}?_limit={limit}&_offset=0"},
        "_prev": {"href": f"{base_url}?_limit={limit}&_offset={max(0, offset - limit)}"} if offset > 0 else None,
        "_next": {"href": f"{base_url}?_limit={limit}&_offset={offset + limit}"} if (offset + limit) < total_registros else None,
        "_last": {"href": f"{base_url}?_limit={limit}&_offset={last_offset}"},
    }

    return links



def validar_string_no_vacio(valor, nombre: str):

    if valor is None or str(valor).strip() == '':
        return construir_error_api(
            code=f'required.{nombre}',
            message=f"Campo requerido: '{nombre}'",
            level='error',
            description=f"El campo '{nombre}' es obligatorio y no puede estar vacio"
        )

    return str(valor).strip()    


def validar_entero(numero, nombre='numero'):
    valor_texto = str(numero).strip()

    if not valor_texto.isnumeric():
        return construir_error_api(
            'invalid.' + nombre + '.format',
            "Formato de '" + nombre + "' invalido",
            'error',
            "El valor '" + str(numero) + "' no puede convertirse a un numero entero"
        )

    return int(valor_texto)