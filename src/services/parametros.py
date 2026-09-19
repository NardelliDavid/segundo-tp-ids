

def verificar_limit_offset(limit,offset):
    if limit < 1 or limit > 100 or offset < 0:
        return {"Error:":"Parametro offset o limit invalidos"}, 400
    else:
        return {"Sin errores"}, 200