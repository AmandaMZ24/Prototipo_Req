# 🐾 PetLink — Guía de instalación y pruebas

Este repositorio contiene un prototipo funcional de adopción de mascotas con un **backend en Flask** y un **frontend estático**.

Este documento explica paso a paso cómo configurar el entorno, crear la base de datos, ejecutar el backend y probar la aplicación (frontend + API).  
Las instrucciones están pensadas para **Windows (PowerShell)**, pero los pasos son similares en macOS o Linux.

---

## 📁 Estructura del repositorio

- **backend/** — Servidor API con Flask  
  - `app.py` — Punto de entrada principal de la aplicación  
  - `config.py` — Configuración general  
  - `db.py` — Conexión con la base de datos  
  - `requirements.txt` — Dependencias de Python para el backend  
- **models/** — Modelos de Python utilizados por las rutas  
- **routes/** — Blueprints de Flask para usuarios, mascotas y adopciones  
- **database/petlink.sql** — Script SQL que crea la base de datos y las tablas  
- **frontend/** — Páginas HTML y JS estáticos para pruebas manuales  

---

## 🎯 Qué ofrece este README

**Entradas necesarias:**  
- Servidor MySQL o MariaDB en ejecución  
- Python 3.8 o superior  
- Acceso a un navegador web  

**Resultados esperados:**  
- Backend funcionando en `http://127.0.0.1:5000`  
- Frontend visible en el navegador  

**Objetivo:**  
- Registrar o iniciar sesión de usuarios  
- Listar y agregar mascotas (admin)  
- Enviar solicitudes de adopción  

---

## ⚙️ Prerrequisitos

1. Tener **Python 3.8 o superior** instalado y agregado al PATH.  
2. Tener **MySQL o MariaDB** instalados y en ejecución.  
3. *(Opcional pero recomendado)* Crear y usar un entorno virtual de Python.  

---

## 🐍 1) Preparar el entorno de Python

Abre PowerShell en el directorio raíz del proyecto.  
Ejemplo:  
```
E:\IC-TEC\II SEMESTRE 2025\REQUERIMIENTOS DE SOFTWARE\Proyecto\Prototipo
```

Crea y activa un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instala las dependencias del backend:

```powershell
pip install -r backend/requirements.txt
```

El archivo `requirements.txt` incluye:  
- Flask (>=2.2)  
- flask-cors  
- flask-jwt-extended  
- flask-bcrypt  
- mysql-connector-python o PyMySQL  

Si aparecen errores de permisos, ejecuta PowerShell como administrador o usa el parámetro `--user` (no recomendado dentro del entorno virtual).

---

## 🐬 2) Crear la base de datos MySQL

El archivo `database/petlink.sql` contiene las sentencias SQL para crear la base de datos **petlink**, las tablas y los datos de ejemplo.

### Opción A — Usando el cliente `mysql` (recomendada):

```powershell
mysql -u root -p < database\petlink.sql
```

Se solicitará la contraseña del usuario **root**.  
Si el script se ejecuta correctamente, la base `petlink` quedará creada.

### Opción B — Desde la consola interactiva de MySQL:

```sql
mysql -u root -p
SOURCE E:/IC-TEC/II SEMESTRE 2025/REQUERIMIENTOS DE SOFTWARE/Proyecto/Prototipo/database/petlink.sql;
```

Si deseas crear un usuario dedicado para la aplicación, ejecuta:

```sql
CREATE USER 'petuser'@'localhost' IDENTIFIED BY 'contraseña_segura';
GRANT ALL PRIVILEGES ON petlink.* TO 'petuser'@'localhost';
FLUSH PRIVILEGES;
```

> 💡 Si cambias el usuario, la contraseña o el nombre de la base, actualiza los valores en `backend/db.py`.

---

## 🧩 3) Configurar el backend

Abre `backend/db.py` y edita los datos de conexión:

```python
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'tu_contraseña',
    'database': 'petlink'
}
```

También puedes usar variables de entorno y modificarlas en `config.py` o `app.py` si deseas una configuración más segura.

---

## 🚀 4) Iniciar el backend

Desde la raíz del proyecto (o dentro de `backend/`):

```powershell
python backend/app.py
```

Flask debería iniciar en `http://127.0.0.1:5000`.  
Si aparecen errores de módulos faltantes, asegúrate de haber activado el entorno virtual y de haber instalado las dependencias correctamente.

---

## 🌐 5) Ejecutar o abrir el frontend

Dentro de la carpeta `frontend/` se encuentran las páginas HTML.  
Puedes abrirlas directamente con doble clic o servirlas mediante un servidor HTTP simple:

```powershell
python -m http.server 8000
```

Luego entra a tu navegador y abre:  
👉 [http://127.0.0.1:8000/index.html](http://127.0.0.1:8000/index.html)

Asegúrate de que el backend esté corriendo en `http://127.0.0.1:5000`, ya que esa es la dirección a la que apunta el frontend.

---

## 🧪 6) Pruebas manuales (frontend)

1. Abre las páginas del frontend (`index.html`, `register.html`, `login.html`, `pets.html`, `add_pet.html`, `edit_pet.html`).  
2. Registra un nuevo usuario desde la página de registro.  
3. Inicia sesión con el usuario creado; el frontend guardará el **token JWT** en `localStorage`.  
4. Ingresa a `pets.html` para ver las mascotas disponibles.  
   - Si iniciaste como **administrador**, podrás agregar o editar mascotas.  

> 🔸 Si la página de registro no tiene opción para crear administradores, puedes hacerlo desde la API o directamente en la base de datos.

---

## 🧰 7) Pruebas por API (cURL)

**Registrar usuario:**

```powershell
curl -X POST http://127.0.0.1:5000/users/register `
  -H "Content-Type: application/json" `
  -d "{\"name\":\"Alice\",\"email\":\"alice@example.com\",\"password\":\"pass123\"}"
```

**Registrar administrador (si el backend lo permite):**

```powershell
curl -X POST http://127.0.0.1:5000/users/register `
  -H "Content-Type: application/json" `
  -d "{\"name\":\"Admin\",\"email\":\"admin@example.com\",\"password\":\"adminpass\",\"role\":\"admin\"}"
```

**Iniciar sesión:**

```powershell
curl -X POST http://127.0.0.1:5000/users/login `
  -H "Content-Type: application/json" `
  -d "{\"email\":\"admin@example.com\",\"password\":\"adminpass\"}"
```

**Listar mascotas:**

```powershell
curl http://127.0.0.1:5000/pets/
```

**Agregar una mascota (requiere token):**

```powershell
curl -X POST http://127.0.0.1:5000/pets/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <TOKEN>" `
  -d "{\"name\":\"Firulais\",\"species\":\"Perro\",\"breed\":\"Mixta\",\"age\":3,\"availability\":\"disponible\"}"
```

**Crear una solicitud de adopción:**

```powershell
curl -X POST http://127.0.0.1:5000/adoptions/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <TOKEN>" `
  -d "{\"pet_id\":1,\"reason\":\"Amo a los animales\"}"
```

