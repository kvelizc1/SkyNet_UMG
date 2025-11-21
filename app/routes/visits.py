from flask import Blueprint, jsonify, request
from app.models.visit import Visit
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime
from app.utils.decorators import role_required
# Para PDF
from app.services.pdf_service import generate_visit_pdf
from app.models.user import User
from app.models.client import Client
# Envio de correos
from app.services.mail_service import send_visit_report_email

visits_bp = Blueprint("visits", __name__)

# 1. Obtener visitas
@visits_bp.route("/", methods=["GET"])
@jwt_required()
def get_visits():
    claims = get_jwt()
    role = claims.get("role")
    user_id = claims.get("sub")  # id del usuario autenticado

    if role == "tecnico":
        visits = Visit.query.filter_by(technician_id=user_id).all()
    elif role == "supervisor":
        visits = Visit.query.filter_by(supervisor_id=user_id).all()
    else:
        visits = Visit.query.all()

    return jsonify([v.to_dict() for v in visits]), 200


# 2. Crear visita (solo supervisor o admin)
@visits_bp.route("/", methods=["POST"])
@jwt_required()
@role_required(["administrador", "supervisor"])
def create_visit():
    data = request.get_json()
    required = ["client_id", "technician_id", "scheduled_date"]
    if not all(k in data for k in required):
        return jsonify({"error": "Información incompleta"}), 400

    scheduled_date = datetime.fromisoformat(data["scheduled_date"])

    new_visit = Visit(
        client_id=data["client_id"],
        technician_id=data["technician_id"],
        supervisor_id=get_jwt().get("sub"),
        scheduled_date=scheduled_date,
    )

    db.session.add(new_visit)
    db.session.commit()
    return jsonify(new_visit.to_dict()), 201


# 3. Check-in (técnico)
@visits_bp.route("/check_in/<int:id>", methods=["PUT"])
@jwt_required()
@role_required(["tecnico", "administrador"])
def visit_check_in(id):
    visit = Visit.query.get_or_404(id)
    data = request.get_json()

    visit.check_in_time = datetime.now()
    visit.check_in_lat = data.get("latitude")
    visit.check_in_lng = data.get("longitude")
    visit.status = "en progreso"

    db.session.commit()
    return jsonify(visit.to_dict()), 200


# 4. Check-out (técnico) - CON GENERACIÓN DE PDF
@visits_bp.route("/check_out/<int:id>", methods=["PUT"])
@jwt_required()
@role_required(["tecnico", "administrador"])
def visit_check_out(id):
    visit = Visit.query.get_or_404(id)
    data = request.get_json()

    visit.check_out_time = datetime.now()
    visit.check_out_lat = data.get("latitude")
    visit.check_out_lng = data.get("longitude")
    visit.status = "finalizada"

    db.session.commit()
    # return jsonify(visit.to_dict()), 200

    # Entidades de la tabla para Generar reporte PDF
    client = Client.query.get(visit.client_id)
    technician = User.query.get(visit.technician_id)
    supervisor = User.query.get(visit.supervisor_id)

    # Generar PDF desde el servicio
    filepath = generate_visit_pdf(visit, client, technician, supervisor)

    # ENVIO DE CORREO CON EL REPORTE ADJUNTO!!
    try:
        send_visit_report_email(client, visit, filepath)
    except Exception as e:
        print(f"[ERROR] No se pudo enviar el correo: {e}")

    return jsonify({
        "visit": visit.to_dict(),
        "pdf_path": filepath
    }), 200


# 5. Actualizar visita (opcional)
@visits_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@role_required(["administrador", "supervisor"])
def update_visit(id):
    visit = Visit.query.get_or_404(id)
    data = request.get_json()

    if "notes" in data:
        visit.notes = data["notes"]
    if "status" in data:
        visit.status = data["status"]

    db.session.commit()
    return jsonify(visit.to_dict()), 200


# 6. Eliminar visita
@visits_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required(["administrador"])
def delete_visit(id):
    visit = Visit.query.get_or_404(id)
    db.session.delete(visit)
    db.session.commit()
    return jsonify({"message": "Visita eliminada"}), 200

