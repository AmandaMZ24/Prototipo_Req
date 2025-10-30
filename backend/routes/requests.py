# backend/routes/requests.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from db import get_db as get_connection
from mysql.connector import Error

bp = Blueprint("requests", __name__, url_prefix="/requests")

@bp.route("", methods=["POST"])  # allow POST to /requests (no trailing slash) to avoid redirect which can drop the body
@jwt_required()
def create_request():
    # cualquier usuario autenticado puede solicitar
    claims = get_jwt()
    user_id = claims.get("id")
    data = request.get_json()
    pet_id = data.get("pet_id")
    reason = data.get("reason", "")
    if not pet_id:
        return jsonify({"msg":"pet_id es obligatorio"}), 400
    try:
        conn = get_connection()
        cur = conn.cursor()
        # opcional: verificar que la mascota esté disponible
        cur.execute("SELECT availability FROM pets WHERE id=%s", (pet_id,))
        pet = cur.fetchone()
        if not pet:
            return jsonify({"msg":"Mascota no encontrada"}), 404
        # si está reservada/adoptada, se rechaza
        if pet[0] != "disponible":
            return jsonify({"msg":"Mascota no disponible"}), 400
        # Insertar la solicitud y marcar la mascota como 'reservado'
        cur.execute("INSERT INTO adoption_requests (user_id, pet_id, reason) VALUES (%s,%s,%s)",
                    (user_id, pet_id, reason))
        request_id = cur.lastrowid
        # Marcar mascota como 'reservado' hasta que un admin revise
        cur.execute("UPDATE pets SET availability=%s WHERE id=%s", ("reservado", pet_id))
        conn.commit()
        return jsonify({"msg":"Solicitud registrada","id": request_id}), 201
    except Error as e:
        return jsonify({"msg":"Error en DB","error": str(e)}), 500
    finally:
        try: cur.close(); conn.close()
        except: pass


@bp.route("/admin", methods=["GET"])
@jwt_required()
def list_requests_admin():
    # solo admin
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"msg":"Acceso no autorizado"}), 403
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        status = request.args.get("status")
        if status:
            cur.execute("""
                SELECT r.id, r.user_id, u.name AS user_name, r.pet_id, p.name AS pet_name, r.reason, r.status, r.created_at AS request_date
                FROM adoption_requests r
                JOIN users u ON r.user_id = u.id
                JOIN pets p ON r.pet_id = p.id
                WHERE r.status = %s
                ORDER BY r.created_at DESC
            """, (status,))
        else:
            cur.execute("""
                SELECT r.id, r.user_id, u.name AS user_name, r.pet_id, p.name AS pet_name, r.reason, r.status, r.created_at AS request_date
                FROM adoption_requests r
                JOIN users u ON r.user_id = u.id
                JOIN pets p ON r.pet_id = p.id
                ORDER BY r.created_at DESC
            """)
        reqs = cur.fetchall()
        return jsonify(reqs), 200
    except Error as e:
        return jsonify({"msg":"Error en DB","error": str(e)}), 500
    finally:
        try: cur.close(); conn.close()
        except: pass


@bp.route("/<int:request_id>", methods=["PUT"])
@jwt_required()
def update_request_status(request_id):
    # admin aprueba/rechaza (ruta compatible con frontend)
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"msg":"Acceso no autorizado"}), 403
    data = request.get_json()
    new_status = data.get("status")
    if new_status not in ["En revisión", "Aprobada", "Rechazada"]:
        return jsonify({"msg":"Estado no válido"}), 400
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM adoption_requests WHERE id=%s", (request_id,))
        r = cur.fetchone()
        if not r:
            return jsonify({"msg":"Solicitud no encontrada"}), 404
        if r["status"] != "En revisión":
            return jsonify({"msg":"La solicitud ya fue procesada"}), 400
        cur2 = conn.cursor()
        cur2.execute("UPDATE adoption_requests SET status=%s WHERE id=%s", (new_status, request_id))
        if new_status == "Aprobada":
            # Pet is adopted when a request is approved
            cur2.execute("UPDATE pets SET availability=%s WHERE id=%s", ("adoptado", r["pet_id"]))
        conn.commit()
        return jsonify({"msg":"Estado actualizado correctamente"}), 200
    except Error as e:
        return jsonify({"msg":"Error en DB","error": str(e)}), 500
    finally:
        try: cur.close(); conn.close()
        except: pass



@bp.route("/<int:request_id>/decision", methods=["POST"])
@jwt_required()
def decide_request(request_id):
    # admin aprueba/rechaza
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"msg":"Acceso no autorizado"}), 403
    data = request.get_json()
    decision = data.get("decision")  # "Aprobada" o "Rechazada"
    if decision not in ("Aprobada", "Rechazada"):
        return jsonify({"msg":"Decision inválida"}), 400
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        # buscar solicitud
        cur.execute("SELECT * FROM adoption_requests WHERE id=%s", (request_id,))
        r = cur.fetchone()
        if not r:
            return jsonify({"msg":"Solicitud no encontrada"}), 404
        if r["status"] != "En revisión":
            return jsonify({"msg":"La solicitud ya fue procesada"}), 400
        # actualizar solicitud
        cur2 = conn.cursor()
        cur2.execute("UPDATE adoption_requests SET status=%s WHERE id=%s", (decision, request_id))
        # si aprobada, actualizar mascota a 'adoptado'
        if decision == "Aprobada":
            cur2.execute("UPDATE pets SET availability=%s WHERE id=%s", ("adoptado", r["pet_id"]))
        elif decision == "Rechazada":
            # Si la solicitud fue rechazada, volver a poner la mascota disponible
            cur2.execute("UPDATE pets SET availability=%s WHERE id=%s", ("disponible", r["pet_id"]))
        conn.commit()
        return jsonify({"msg":"Decision guardada"}), 200
    except Error as e:
        return jsonify({"msg":"Error en DB","error": str(e)}), 500
    finally:
        try: cur.close(); conn.close()
        except: pass
