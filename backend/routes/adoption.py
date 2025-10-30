from flask import Blueprint, jsonify, request
from db import get_db
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint("adoption", __name__, url_prefix="/adoptions")


# Crear una solicitud de adopción
@bp.route("/", methods=["POST"])
@jwt_required()
def create_request():
    db = get_db()
    data = request.get_json()
    email = get_jwt_identity()

    # Obtener ID del usuario a partir del correo
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    query = """
        INSERT INTO adoption_requests (user_id, pet_id, reason, status)
        VALUES (%s, %s, %s, 'En revisión')
    """
    cursor.execute(query, (user["id"], data["pet_id"], data.get("reason", "")))
    db.commit()

    return jsonify({"msg": "Solicitud enviada con éxito ✅"}), 201

# 🔹 Ruta solo para ADMIN: ver todas las solicitudes
@bp.route("/admin", methods=["GET"])
@jwt_required()
def get_all_requests():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    identity = get_jwt_identity()
    # identity debe contener el rol (viene del token)
    role = identity.get("role") if isinstance(identity, dict) else None
    if role != "admin":
        return jsonify({"msg": "Acceso denegado"}), 403

    cursor.execute("""
        SELECT ar.id, ar.user_id, ar.pet_id, ar.status, ar.created_at AS request_date,
               u.name AS user_name, p.name AS pet_name
        FROM adoption_requests ar
        JOIN users u ON ar.user_id = u.id
        JOIN pets p ON ar.pet_id = p.id
        ORDER BY ar.created_at DESC
    """)
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data), 200
