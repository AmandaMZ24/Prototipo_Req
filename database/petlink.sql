-- petlink/database/petlink.sql
CREATE DATABASE IF NOT EXISTS petlink CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE petlink;

-- Usuarios
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('adoptante','admin') NOT NULL DEFAULT 'adoptante',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mascotas
CREATE TABLE IF NOT EXISTS pets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  species VARCHAR(50),
  breed VARCHAR(100),
  age INT,
  sex ENUM('Macho','Hembra') DEFAULT NULL,
  health_status VARCHAR(255),
  availability ENUM('disponible','reservado','adoptado') DEFAULT 'disponible',
  photo_url VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Solicitudes de adopción
CREATE TABLE IF NOT EXISTS adoption_requests (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  pet_id INT NOT NULL,
  reason VARCHAR(200),
  status ENUM('En revisión','Aprobada','Rechazada') DEFAULT 'En revisión',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
);
