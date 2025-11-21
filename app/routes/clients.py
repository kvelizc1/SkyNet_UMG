from flask import Blueprint, jsonify, request
from app.models.client import Client
from app.extensions import db
from flask_jwt_extended import jwt_required
from app.utils.decorators import role_required

clients_bp = Blueprint("clients", __name__)

@clients_bp.route("/", methods=["GET"])
@jwt_required()
def get_clients():
    clients = Client.query.all()
    return jsonify([c.to_dict() for c in clients]), 200


@clients_bp.route("/", methods=["POST"])
@jwt_required()
@role_required(["administrador", "supervisor"])
def create_client():
    data = request.get_json()
    if not data or not all(k in data for k in ("name", "address")):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    new_client = Client(
        name=data["name"],
        address=data["address"],
        email=data.get("email"),
        phone=data.get("phone"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude")
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify(new_client.to_dict()), 201


@clients_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@role_required(["administrador", "supervisor"])
def update_client(id):
    client = Client.query.get_or_404(id)
    data = request.get_json()
    for field in ["name", "address", "email", "phone", "latitude", "longitude"]:
        if field in data:
            setattr(client, field, data[field])
    db.session.commit()
    return jsonify(client.to_dict()), 200


@clients_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required(["administrador"])
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Cliente eliminado"}), 200
