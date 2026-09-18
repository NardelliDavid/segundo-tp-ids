USE db_flask;

CREATE TABLE IF NOT EXISTS deportes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS canchas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    id_deporte INT NOT NULL,
    precio_hora INT NOT NULL, 
    techada BOOLEAN NOT NULL DEFAULT FALSE,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (id_deporte) REFERENCES deportes(id)
);

CREATE TABLE IF NOT EXISTS socios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS reservas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_socio INT NOT NULL,
    id_cancha INT NOT NULL,
    fecha_hora_inicio DATETIME(6) NOT NULL,
    fecha_hora_fin DATETIME(6) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'confirmada', 
    precio_hora INT NOT NULL,
    total INT NOT NULL,       
    FOREIGN KEY (id_socio) REFERENCES socios(id),
    FOREIGN KEY (id_cancha) REFERENCES canchas(id)
);

INSERT INTO deportes (id, nombre) VALUES 
(1, 'Fútbol'),
(2, 'Tenis'),
(3, 'Pádel');

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa) VALUES
('Cancha Fútbol 1', 1, 1500000, TRUE, TRUE),
('Cancha Fútbol 2', 1, 1200000, FALSE, TRUE),
('Cancha Tenis 1', 2, 1000000, TRUE, TRUE),
('Cancha Tenis 2', 2, 900000, FALSE, TRUE),
('Cancha Pádel 1', 3, 1800000, TRUE, TRUE);

INSERT INTO socios (nombre, email, activo) VALUES
('Juan Perez', 'juan.perez@gmail.com', TRUE),
('Maria Gomez', 'maria.gomez@gmail.com', TRUE),
('Carlos Lopez', 'carlos.lopez@gmail.com', TRUE),
('Ana Martinez', 'ana.martinez@gmail.com', TRUE),
('Pedro Rodriguez', 'pedro.rodriguez@gmail.com', TRUE);

INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total) VALUES
(1, 1, '2026-10-15 18:00:00.000000', '2026-10-15 20:00:00.000000', 'confirmada', 1500000, 3000000),
(2, 2, '2026-10-15 19:00:00.000000', '2026-10-15 20:00:00.000000', 'confirmada', 1200000, 1200000),
(3, 3, '2026-10-16 10:00:00.000000', '2026-10-16 12:00:00.000000', 'confirmada', 1000000, 2000000),
(4, 5, '2026-10-16 16:00:00.000000', '2026-10-16 17:00:00.000000', 'confirmada', 1800000, 1800000),
(5, 1, '2026-10-17 20:00:00.000000', '2026-10-17 21:00:00.000000', 'cancelada', 1500000, 1500000);

-- DROP DATABASE db_flask;
