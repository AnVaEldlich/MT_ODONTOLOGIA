-- 1) En Workbench: conéctate como root (la misma contraseña del instalador de MySQL).
-- 2) File → Open SQL Script → este archivo → Execute (rayo).
-- 3) En .env pon DB_USER=root y DB_PASSWORD=esa misma contraseña.
--    (Opcional: si prefieres el usuario de la app, descomenta el bloque de abajo
--     y deja DB_USER=odontologia_app / DB_PASSWORD=clave-inventada-ejemplo.)

CREATE DATABASE IF NOT EXISTS odontologia_ejemplo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- CREATE USER IF NOT EXISTS 'odontologia_app'@'localhost' IDENTIFIED BY 'clave-inventada-ejemplo';
-- CREATE USER IF NOT EXISTS 'odontologia_app'@'127.0.0.1' IDENTIFIED BY 'clave-inventada-ejemplo';
-- GRANT ALL PRIVILEGES ON odontologia_ejemplo.* TO 'odontologia_app'@'localhost';
-- GRANT ALL PRIVILEGES ON odontologia_ejemplo.* TO 'odontologia_app'@'127.0.0.1';
-- FLUSH PRIVILEGES;
