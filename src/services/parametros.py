def verificar_limit_offset(limit,offset):
    if limit < 1 or limit > 100 or offset < 0:
        return {"Error:":"Parametro offset o limit invalidos"}, 400
    else:
        return {"Sin errores"}, 200

# Funcion para generar links HATEOAS
def generar_links(base_url, limit, offset, total):
    last_offset = ((total - 1) // limit) * limit if total > 0 else 0

    links = {
        "_first": f"{base_url}?_limit={limit}&_offset=0",
        "_last": f"{base_url}?_limit={limit}&_offset={last_offset}",
    }
    if offset > 0:
        links["_prev"] = f"{base_url}?_limit={limit}&_offset={max(offset - limit, 0)}"
    if offset + limit < total:
        links["_next"] = f"{base_url}?_limit={limit}&_offset={offset + limit}"

    return links