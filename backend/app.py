from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from db import get_db
from routes import users, pets, adoption, requests  
app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = "clave-secreta-supersegura"
jwt = JWTManager(app)

# 🔹 Registrar blueprints
app.register_blueprint(users.bp)
app.register_blueprint(pets.bp)
app.register_blueprint(adoption.bp)  
app.register_blueprint(requests.bp)

@app.route("/")
def index():
    return "Servidor PetLink activo 🚀"

if __name__ == "__main__":
    app.run(debug=True)