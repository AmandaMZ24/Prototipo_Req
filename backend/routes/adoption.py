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

# Listar solicitudes de un usuario (por si luego querés mostrarle su historial)
@bp.route("/", methods=["GET"])
@jwt_required()
def list_requests():
    db = get_db()
    email = get_jwt_identity()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id, p.name AS pet_name, a.reason, a.status, a.created_at
        FROM adoption_requests a
        JOIN users u ON u.id = a.user_id
        JOIN pets p ON p.id = a.pet_id
        WHERE u.email = %s
        ORDER BY a.created_at DESC
    """, (email,))
    requests = cursor.fetchall()
    return jsonify(requests), 200
