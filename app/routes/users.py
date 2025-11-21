from flask import Blueprint, jsonify, request
from app.models.user import User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import generate_token
from app.utils.decorators import role_required

# Objeto blueprint. 
# "users" es el nombre del blueprint y __name__ es el nombre del módulo actual.
# __name__ ayuda a Flask a localizar recursos relacionados con el blueprint.
# __name__ indica en qué módulo se definió el blueprint.
users_bp = Blueprint("users", __name__)


# Registro de ruta (GET) en el blueprint (users_bp).
# '@' Decorador (envuelve a otra función) agregando funcionalidad adicional.
# El decorador indica que cuando llegue un GET a la ruta "/", se ejecute la función get_users.
@users_bp.route("/", methods=["GET"])
def get_users():
    # User hereda de db.Model (app/models/user.py), db es una instancia de SQLAlchemy.
    # SQLAlchemy proporciona una forma de interactuar con la base de datos usando objetos Python.
    # SQLAlchemy agrega metodos de consulta a través de "BaseQuery" (Objeto de ayuda).
    # Esto permite hacer .query.all()
    users = User.query.all()
    # Además de devolver un json con la lista de usuarios,
    # se devuelve un código HTTP 200 (OK).
    # Es porque get_users es una función asociada a una ruta HTTP.
    return jsonify([u.to_dict() for u in users]), 200


@users_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or not all(k in data for k in ("name", "email", "password", "role")):
        return jsonify({"error": "Datos incompletos"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "El correo ya está registrado"}), 400

    new_user = User(
        name=data["name"],
        email=data["email"],
        role=data["role"]
    )
    new_user.set_password(data["password"])

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.to_dict()), 201


# Nuevo endpoint para login (domingo 9 nov)
@users_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ("email", "password")):
        return jsonify({"error": "Datos incompletos"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = generate_token(user)
    return jsonify({
        "access_token": token,
        "user": user.to_dict()
    }), 200


# Endpoint para administradores
@users_bp.route("/admin", methods=["GET"])
@jwt_required()
@role_required(["administrador"])
def admin_area():
    return jsonify({"mensaje": "Área restringida a administradores - OK!"}), 200
