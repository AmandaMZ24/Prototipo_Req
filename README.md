# PetLink — Setup & Testing Guide

This repository contains a small pet adoption prototype with a Flask backend and static frontend pages.

This README explains, step-by-step, how to set up the environment, create the database, run the backend, and test the application (frontend + API). It assumes you're on Windows (PowerShell) but the steps are similar on macOS/Linux.

## Repository layout (important files)

- `backend/` — Flask API server
  - `app.py` — application entrypoint
  - `config.py` — configuration helpers
  - `db.py` — database connection helper
  - `requirements.txt` — Python dependencies for the backend
- `models/` — Python model helpers used by routes
- `routes/` — Flask route blueprints for users, pets, adoptions/requests
- `database/petlink.sql` — SQL schema & seed statements (creates the `petlink` database and tables)
- `frontend/` — static HTML pages and JS used for manual testing

## Quick contract (what this README provides)

- Inputs: a running MySQL / MariaDB server, Python 3.8+, access to a web browser
- Outputs: a running backend at `http://127.0.0.1:5000` and frontend pages you can open in your browser
- Success criteria: able to register/login users, list and add pets (admin), send adoption requests

## Prerequisites

1. Python 3.8+ installed and on PATH.
2. MySQL or MariaDB server installed and running locally. You need a MySQL client (e.g., `mysql` command) to run the supplied SQL script.
3. Optional but recommended: create and use a Python virtual environment.

## 1) Prepare Python environment

Open PowerShell in the project root (`E:\IC-TEC\II SEMESTRE 2025\REQUERIMIENTOS DE SOFTWARE\Proyecto\Prototipo`).

Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
pip install -r backend/requirements.txt
```

The `backend/requirements.txt` includes:

- Flask (>=2.2)
- flask-cors
- flask-jwt-extended
- flask-bcrypt
- mysql-connector-python or PyMySQL (both may be present; the code uses the configured connector)

If you hit permission problems, run PowerShell as Administrator, or use `--user` for pip install (not recommended in virtualenv).

## 2) Create the MySQL database

The `database/petlink.sql` file contains SQL to create the `petlink` database, tables and seed data. There are two common ways to apply it.

Option A — use the mysql client (recommended):

```powershell
# Run this in the project root
mysql -u root -p < database\petlink.sql
```

You'll be prompted for the MySQL `root` password. If the file executes successfully, the `petlink` database and tables will exist.

Option B — from within the MySQL interactive console:

```sql
# open mysql client first
mysql -u root -p
# then in the mysql prompt
SOURCE E:/IC-TEC/II SEMESTRE 2025/REQUERIMIENTOS DE SOFTWARE/Proyecto/Prototipo/database/petlink.sql;
```

Notes:
- If you prefer to create a dedicated DB user for the app, run this in the MySQL prompt (adjust the password):

```sql
CREATE USER 'petuser'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON petlink.* TO 'petuser'@'localhost';
FLUSH PRIVILEGES;
```

- If you change the DB user/password/database, update the configuration in `backend/db.py` or use environment variables if you change the code to read them.

## 3) Configure the backend

By default the repository contains `backend/db.py` and `backend/config.py`. The simplest approach is to open `backend/db.py` and set the connection parameters (host, user, password, database) to match your MySQL setup.

Preferred production approach (optional):

- Store secrets in environment variables and update `backend/config.py` / `backend/app.py` to read them. There is already a `config.py` that may help. Search for `JWT_SECRET_KEY` and database configuration in the backend files.

## 4) Start the backend

From the project root (or `backend/`) run:

```powershell
python backend/app.py
```

By default Flask should start on `http://127.0.0.1:5000`. If you changed the host/port, follow the printed startup messages.

If you get errors about missing modules, ensure you installed dependencies in the correct Python environment.

## 5) Run or open the frontend

The `frontend/` folder contains static HTML pages. You can open them directly in the browser (double-click the `.html`) or serve them with a simple HTTP server so fetches use `http://` (recommended for some browsers' CORS behavior):

From the `frontend` folder:

```powershell
python -m http.server 8000
```

Then open `http://127.0.0.1:8000/index.html` in your browser.

Note: If the frontend calls the API at `http://127.0.0.1:5000`, make sure the backend is running on that address and port.

## 6) Test flows (manual via frontend)

1. Open the frontend pages in the browser (index, register, login, pets, add_pet, edit_pet).
2. Register a new user from the register page. The register form should call the backend register endpoint.
3. Login via `frontend/login.html`. The login flow stores a JWT token in `localStorage` which the front-end uses for protected routes.
4. Visit `pets.html` to list pets. If you registered as an admin, you will be able to add or edit pets using the admin pages.

If registration pages don't expose a `role` field, use the API directly to create an admin (see curl examples below) or change the database manually.

## 7) Test flows (API-level, curl examples)

Below are cURL examples to exercise the API. Replace `127.0.0.1:5000` if your backend uses a different host/port.

- Register a normal user:

```powershell
curl -X POST http://127.0.0.1:5000/users/register `
  -H "Content-Type: application/json" `
  -d '{"name":"Alice","email":"alice@example.com","password":"pass123"}'
```

- Register an admin (if the backend supports role in the register payload):

```powershell
curl -X POST http://127.0.0.1:5000/users/register `
  -H "Content-Type: application/json" `
  -d '{"name":"Admin","email":"admin@example.com","password":"adminpass","role":"admin"}'
```

- Login to receive JWT token:

```powershell
curl -X POST http://127.0.0.1:5000/users/login `
  -H "Content-Type: application/json" `
  -d '{"email":"admin@example.com","password":"adminpass"}'
```

The response typically contains a token (look for a `token` or similar field). Use that token for protected endpoints.

- List pets (public):

```powershell
curl http://127.0.0.1:5000/pets/
```

- Add a pet (admin only):

```powershell
curl -X POST http://127.0.0.1:5000/pets/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <TOKEN>" `
  -d '{"name":"Firulais","species":"Perro","breed":"Mixta","age":3,"availability":"disponible"}'
```

- Create an adoption request (authenticated user):

```powershell
curl -X POST http://127.0.0.1:5000/adoptions/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <TOKEN>" `
  -d '{"pet_id":1,"reason":"I love pets"}'
```

## 8) Troubleshooting

- Database connection errors: verify `backend/db.py` credentials, ensure MySQL service is running, ensure the `petlink` database exists.
- Module import errors: ensure you installed the requirements into the Python interpreter you use to run `app.py` (activate your venv first).
- CORS issues: the backend enables CORS in `app.py` (look for `flask_cors.CORS`). If you still see blocked requests, check browser console and verify the backend is reachable from the frontend origin.
- JWT / authentication errors: check `app.py` for `JWT_SECRET_KEY` and ensure the token in requests is the token returned by the login endpoint. For production keep the secret outside source control.
- If the frontend cannot fetch the API and you served the frontend using `file://` (opened directly in browser), try serving it with `python -m http.server 8000` so HTTP origins match and CORS applies correctly.

## 9) Helpful tips and notes

- There are two request/adoption route modules in the repo: `routes/requests.py` and `routes/adoption.py`. The frontend appears to use the `/adoptions` routes; check both files if behavior seems duplicated.
- For development, use a local MySQL user with limited privileges rather than `root`.
- For persistent debugging, add logging to `app.py` or run Flask in debug mode (only for development).

## 10) Next steps / potential improvements (optional)

- Move DB credentials and JWT secret to environment variables and read them in `config.py`.
- Add a small script `scripts/init_db.py` to run `database/petlink.sql` programmatically and optionally create an admin account.
- Add unit tests for API endpoints using `pytest` and a test database.

---

If you want, I can also:

- Add a small `scripts/init_db.ps1` that runs the SQL file and optionally creates a test admin user.
- Add a `README` at `backend/README.md` explaining backend-specific environment variables.

Tell me which of the optional extras you'd like and I'll add them.
