from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from db import get_db

bcrypt = Bcrypt()
bp = Blueprint("users", __name__, url_prefix="/users")

@bp.route("/register", methods=["POST"])
def register():
    db = get_db()
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "adoptante")

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
        (name, email, hashed_pw, role)
    )
    db.commit()
    return jsonify({"msg": "Usuario registrado correctamente ✅"}), 201

@bp.route("/login", methods=["POST"])
def login():
    db = get_db()
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and bcrypt.check_password_hash(user["password_hash"], password):
        # Crear token JWT: usar email (string) como identity para evitar error "Subject must be a string"
        # y poner id/role en additional_claims para que estén disponibles en las rutas.
        identity = user["email"]
        access_token = create_access_token(identity=identity,
                                           additional_claims={"id": user["id"], "role": user["role"]})
        return jsonify({
            "msg": "Inicio de sesión exitoso ✅",
            "token": access_token,
            "user": {
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }), 200
    else:
        return jsonify({"msg": "Credenciales inválidas"}), 401