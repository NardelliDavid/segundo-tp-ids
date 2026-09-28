from src.repository.canchas import listar_canchas, contar_canchas
from src.utils import generar_links_hateoas
from src.constants import (
    DEFAULT_LIMIT
)

def mostrar_canchas(base_url, id_deporte=None, nombre=None, techada=None, activa=None, limit=DEFAULT_LIMIT, offset=0):
     

    canchas=listar_canchas(id_deporte, nombre, techada, activa, limit, offset)
    total_registros=contar_canchas(id_deporte, nombre, techada, activa)

    if canchas is None or total_registros is None:
        return None

    links=generar_links_hateoas(base_url, limit, offset, total_registros)
  
    return {"canchas": canchas, "_links": links}