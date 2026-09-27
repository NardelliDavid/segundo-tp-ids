def validar_nombre_activo(nombre, activo):
    try:
        if nombre != None:
            nombre = str(nombre).strip().lower()
            caracteres_validos = "qwertyuiopasdfghjklñzxcvbnm"
            for letra in nombre:
                if letra not in caracteres_validos:
                    return {"Error":"El parametro nombre contiene caracteres invalidos"}, 400
        if activo != None:
            activo = int(activo)

        return nombre, activo
    except:
        return {"Error":"El parametro nombre o activo es erroneo"}, 400

import re

def _email_valido(email):
    patron = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(patron, email))

def _nombre_valido(nombre):
    patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ' ]+$"
    return bool(re.match(patron, nombre))
