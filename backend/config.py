# backend/config.py
import os

# Cambia estas variables según tu entorno o usa variables de entorno reales
JWT_SECRET = os.getenv("PETLINK_JWT_SECRET", "cambiar_esto_por_una_clave_segura")
DB_HOST = os.getenv("PETLINK_DB_HOST", "localhost")
DB_USER = os.getenv("PETLINK_DB_USER", "root")
DB_PASSWORD = os.getenv("PETLINK_DB_PASSWORD", "rfmmsoeu2412##")
DB_NAME = os.getenv("PETLINK_DB_NAME", "petlink")
