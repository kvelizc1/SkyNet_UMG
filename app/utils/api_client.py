# "helper" para requests con manejo de expiración 
# Debe usarse en rutas que hacen requests al API
# Failicita el manejo de tokens expirados o inválidos
# Limpia la sesión y redirige al login si el token ya no es válido

import requests
from flask import session, redirect, url_for

API_BASE = "http://127.0.0.1:5000"

def api_request(method, endpoint, token, **kwargs):
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {token}"

    resp = requests.request(
        method,
        f"{API_BASE}{endpoint}",
        headers=headers,
        **kwargs
    )

    # Manejo centralizado de errores
    if resp.status_code in [401, 422]:
        # Limpia la sesión y pide al usuario que inicie nuevamente
        session.clear()
        return redirect(url_for("frontend.login"))

    return resp
