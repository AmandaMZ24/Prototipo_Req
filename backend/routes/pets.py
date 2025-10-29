from flask import Blueprint, jsonify, request
from db import get_db
from flask_jwt_extended import jwt_required

bp = Blueprint("pets", __name__, url_prefix="/pets")

#  Listar todas las mascotas
@bp.route("/", methods=["GET"])
def get_pets():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pets ORDER BY id DESC")
    pets = cursor.fetchall()
    return jsonify(pets), 200

#  Obtener una mascota por ID
@bp.route("/<int:id>", methods=["GET"])
def get_pet(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pets WHERE id = %s", (id,))
    pet = cursor.fetchone()
    if pet:
        return jsonify(pet), 200
    else:
        return jsonify({"msg": "Mascota no encontrada"}), 404

#  Agregar una mascota
@bp.route("/", methods=["POST"])
@jwt_required()
def add_pet():
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()

    query = """
        INSERT INTO pets (name, species, breed, age, sex, health_status, availability, photo_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        data.get("name"),
        data.get("species"),
        data.get("breed"),
        data.get("age"),
        data.get("sex"),
        data.get("health_status"),
        data.get("availability"),
        data.get("photo_url")
    ))

    db.commit()
    return jsonify({"msg": "Mascota agregada correctamente"}), 201

#  Editar mascota
@bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_pet(id):
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()

    query = """
        UPDATE pets
        SET name=%s, species=%s, breed=%s, age=%s, sex=%s, health_status=%s, availability=%s, photo_url=%s
        WHERE id=%s
    """
    cursor.execute(query, (
        data.get("name"),
        data.get("species"),
        data.get("breed"),
        data.get("age"),
        data.get("sex"),
        data.get("health_status"),
        data.get("availability"),
        data.get("photo_url"),
        id
    ))

    db.commit()
    return jsonify({"msg": "Mascota actualizada correctamente"}), 200

#  Eliminar mascota
@bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_pet(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM pets WHERE id = %s", (id,))
    db.commit()
    return jsonify({"msg": "Mascota eliminada correctamente"}), 200
