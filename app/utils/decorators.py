# Decorador para verificar roles de usuario en rutas protegidas.
# Sólo permite el acceso si el rol del usuario está en la lista de roles permitidos.
# Regresa un 403 (Denegado) si el rol no es adecuado.
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from functools import wraps
from flask import jsonify

def role_required(roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in roles:
                return jsonify({"error": "Acceso denegado"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper



'''
def role_required(roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            if current_user["role"] not in roles:
                return jsonify({"error": "Acceso denegado"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
'''