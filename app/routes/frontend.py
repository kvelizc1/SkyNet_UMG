from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify, send_from_directory, current_app, abort
import requests
from app.config import Config
from app.utils.api_client import api_request
# Para PDF
from flask import send_from_directory
import os

frontend_bp = Blueprint("frontend", __name__)

API_URL = "http://127.0.0.1:5000/api/users"

@frontend_bp.route("/")
def index():
    if "user" in session:
        return redirect(url_for("frontend.dashboard"))
    return redirect(url_for("frontend.login"))


@frontend_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        response = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
        if response.status_code == 200:
            data = response.json()
            session["token"] = data["access_token"]
            session["user"] = data["user"]
            return redirect(url_for("frontend.dashboard"))
        else:
            return render_template("login.html", error="Credenciales inválidas")

    return render_template("login.html")


@frontend_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        response = requests.post(f"{API_URL}/", json={
            "name": name,
            "email": email,
            "password": password,
            "role": role
        })
        if response.status_code == 201:
            return redirect(url_for("frontend.login"))
        else:
            return render_template("register.html", error="Error al registrar usuario")

    return render_template("register.html")

'''
@frontend_bp.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("frontend.login"))
    return render_template("dashboard.html", user=session["user"])
'''
@frontend_bp.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("frontend.login"))
    # Validar que tenga rol permitido
    if user["role"] not in ["administrador", "supervisor", "tecnico"]:
        session.clear()
        return redirect(url_for("frontend.login"))
    return render_template("dashboard.html", user=user)


@frontend_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("frontend.login"))

# Registrando la nueva ruta /clientes
from app.utils.api_client import api_request

@frontend_bp.route("/clientes", methods=["GET", "POST"])
def clientes():
    user = session.get("user")
    if not user:
        return redirect(url_for("frontend.login"))

    token = session.get("token")

    # POST: Crear cliente
    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "address": request.form.get("address"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "latitude": request.form.get("latitude"),
            "longitude": request.form.get("longitude"),
        }

        resp = api_request(
            "POST",
            "/api/clients/",
            token,
            json=data
        )

        # Si resp es una redirección por token expirado:
        if isinstance(resp, str):
            return resp  # en realidad es un redirect

    # GET: Listar clientes
    resp = api_request("GET", "/api/clients/", token)
    if isinstance(resp, str):  # redirigido por expiración
        return resp

    clients = resp.json() if resp.status_code == 200 else []

    print("[DEBUG] Renderizando clients.html con clientes: ...")
    api_key = Config.GOOGLE_MAPS_KEY
    return render_template("clients.html", clients=clients, api_key=api_key)
    #return render_template("clients.html", clients=clients)


#               --- VISITAS ---
# Verifica que el usuario sea supervisor 
# Obtiene clientes y técnicos desde la API 
# Permite crear visitas enviando un POST 
# Muestra las visitas del supervisor
@frontend_bp.route("/visitas", methods=["GET", "POST"])
def visitas():
    user = session.get("user")
    if not user:
        return redirect(url_for("frontend.login"))

    if user["role"] not in ["supervisor", "administrador"]:
        return redirect(url_for("frontend.dashboard"))

    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # --- OBTENER CLIENTES ---
    clients_resp = requests.get("http://127.0.0.1:5000/api/clients/", headers=headers)
    clients = clients_resp.json() if clients_resp.status_code == 200 else []

    # --- OBTENER TÉCNICOS ---
    users_resp = requests.get("http://127.0.0.1:5000/api/users/", headers=headers)
    all_users = users_resp.json() if users_resp.status_code == 200 else []
    technicians = [u for u in all_users if u["role"] == "tecnico"]

    # --- CREAR VISITA ---
    success = None
    error = None

    if request.method == "POST":
        data = {
            "client_id": request.form.get("client_id"),
            "technician_id": request.form.get("technician_id"),
            "scheduled_date": request.form.get("scheduled_date")
        }

        print("[DEBUG] Intentando crear visita:", data)

        resp = requests.post(
            "http://127.0.0.1:5000/api/visits/",
            json=data,
            headers=headers
        )

        if resp.status_code == 201:
            success = "Visita creada exitosamente."
        else:
            error = f"Error al crear visita: {resp.text}"

    # --- OBTENER VISITAS ---
    visits_resp = requests.get("http://127.0.0.1:5000/api/visits/", headers=headers)
    visits = visits_resp.json() if visits_resp.status_code == 200 else []

    return render_template(
        "visitas.html",
        clients=clients,
        technicians=technicians,
        visits=visits,
        success=success,
        error=error
    )


#           --- VISITAS (user: TÉCNICO) ---
@frontend_bp.route("/mis-visitas", methods=["GET"])
def mis_visitas():
    user = session.get("user")
    if not user or user["role"] != "tecnico":
        return redirect(url_for("frontend.login"))

    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # Obtener visitas del técnico
    resp = requests.get("http://127.0.0.1:5000/api/visits/", headers=headers)

    visits = resp.json() if resp.status_code == 200 else []

    return render_template("mis_visitas.html", visits=visits)

#  --- Check-In y Check-Out de visitas (técnico) ---
# Recibe latitud y longitud desde el frontend
# Hace post a la API para actualizar la visita
# Finalmente redirige recarga la página de mis-visitas
@frontend_bp.route("/checkin/<int:visit_id>")
def checkin_page(visit_id):
    user = session.get("user")
    if not user or user["role"] != "tecnico":
        return redirect(url_for("frontend.login"))

    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # Obtener datos de la visita
    resp = requests.get(f"http://127.0.0.1:5000/api/visits/", headers=headers)
    visits = resp.json()

    visit = next((v for v in visits if v["id"] == visit_id), None)
    if not visit:
        return "Visita no encontrada", 404

    # Obtener cliente
    client_resp = requests.get(f"http://127.0.0.1:5000/api/clients/", headers=headers)
    all_clients = client_resp.json()
    client = next((c for c in all_clients if c["id"] == visit["client_id"]), None)

    api_key = Config.GOOGLE_MAPS_KEY

    return render_template(
        "check_in.html",
        visit_id=visit_id,
        client=client,
        api_key=api_key
    )


@frontend_bp.route("/checkout/<int:visit_id>")
def checkout_page(visit_id):
    user = session.get("user")
    if not user or user["role"] != "tecnico":
        return redirect(url_for("frontend.login"))

    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get("http://127.0.0.1:5000/api/visits/", headers=headers)
    visits = resp.json()
    visit = next((v for v in visits if v["id"] == visit_id), None)

    client_resp = requests.get("http://127.0.0.1:5000/api/clients/", headers=headers)
    clients = client_resp.json()
    client = next((c for c in clients if c["id"] == visit["client_id"]), None)

    api_key = Config.GOOGLE_MAPS_KEY

    return render_template(
        "check_out.html",
        visit_id=visit_id,
        client=client,
        api_key=api_key
    )


# Deprecated - no funcionó bien en local... ''' yo no funciono bien en local .-.

@frontend_bp.route("/registrar-checkin/<int:id>", methods=["POST"])
def registrar_checkin(id):
    user = session.get("user")
    if not user or user["role"] != "tecnico":
        return redirect(url_for("frontend.login"))

    data = request.get_json()
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.put(
        f"http://127.0.0.1:5000/api/visits/check_in/{id}",
        json=data,
        headers=headers
    )

    return ("", resp.status_code)


@frontend_bp.route("/registrar-checkout/<int:id>", methods=["POST"])
def registrar_checkout(id):
    user = session.get("user")
    if not user or user["role"] != "tecnico":
        return redirect(url_for("frontend.login"))

    data = request.get_json()
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.put(
        f"http://127.0.0.1:5000/api/visits/check_out/{id}",
        json=data,
        headers=headers
    )

    return ("", resp.status_code)


#     --- GENERAR Y DESCARGAR PDF Por VISITA FINALIZADA ---
@frontend_bp.route("/reporte/<int:visit_id>")
def reporte(visit_id):
    filename = f"visit_{visit_id}.pdf"
    project_root = os.path.dirname(os.path.dirname(current_app.root_path))
    reports_dir = os.path.join(project_root, "FaseIII_SkyNetvII/generated_reports")
    full_path = os.path.join(project_root, "FaseIII_SkyNetvII/generated_reports", filename)
    print(f"[DEBUG] Generando y enviando archivo PDF: {full_path}")
    if not os.path.exists(full_path):
        abort(404, description=f"Reporte {filename} no encontrado.")

    #return send_from_directory("generated_reports", filename)
    return send_from_directory(reports_dir, filename, as_attachment=True)


#  --- DASHBOARD DE VISITAS PARA SUPERVISORES ---
@frontend_bp.route("/dashboard-supervisor")
def dashboard_supervisor():
    user = session.get("user")
    if not user or user["role"] == "tecnico":
        return redirect(url_for("frontend.login"))

    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # Obtener visitas del supervisor
    resp = requests.get("http://127.0.0.1:5000/api/visits/", headers=headers)

    visits = resp.json() if resp.status_code == 200 else []

    # Estadísticas
    total = len(visits)
    pendientes = len([v for v in visits if v["status"] == "pendiente"])
    progreso = len([v for v in visits if v["status"] == "en progreso"])
    finalizadas = len([v for v in visits if v["status"] == "finalizada"])

    # Visitas por técnico
    visitas_por_tecnico = {}
    for v in visits:
        t = v["technician_id"]
        visitas_por_tecnico[t] = visitas_por_tecnico.get(t, 0) + 1

    return render_template(
        "dashboard_supervisor.html",
        total=total,
        pendientes=pendientes,
        progreso=progreso,
        finalizadas=finalizadas,
        visitas_por_tecnico=visitas_por_tecnico,
        visits=visits
    )