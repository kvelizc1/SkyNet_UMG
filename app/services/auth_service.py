# app/services/auth_service.py - autenticación de usuarios
# Servicio para manejar la lógica de autenticación y generación de tokens JWT (JSON Web Tokens).
# Utiliza la extensión Flask-JWT-Extended para crear tokens seguros.
from flask_jwt_extended import create_access_token
from datetime import timedelta

def generate_token(user):
    token = create_access_token(
        identity=str(user.id),              # debe ser string o int
        additional_claims={                 # puede incluir más datos
            "email": user.email,
            "role": user.role
        },
        expires_delta=timedelta(hours=6)
    )
    return token




'''
from flask_jwt_extended import create_access_token
from datetime import timedelta

def generate_token(user):
    token = create_access_token(
        identity={"id": str(user.id), "email": user.email, "role": user.role},
        #identity=str(user.id), additional_claims={"email": user.email, "role": user.role},
        expires_delta=timedelta(hours=6)
    )

    print(f"[DEBUG] Token generado para usuario {user.email}: {token}")
    print(f"[DEBUG] {token.__hash__()}")
    return token
'''