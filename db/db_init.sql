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

-- =========================================
-- DEPORTES (5)
-- =========================================

INSERT INTO deportes (nombre) VALUES ('Futbol');
INSERT INTO deportes (nombre) VALUES ('Tenis');
INSERT INTO deportes (nombre) VALUES ('Padel');
INSERT INTO deportes (nombre) VALUES ('Basquet');
INSERT INTO deportes (nombre) VALUES ('Voley');


-- =========================================
-- CANCHAS (10)
-- 2 POR CADA DEPORTE
-- =========================================

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
VALUES ('Futbol - Cancha 1', 1, 15000, FALSE, TRUE);

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
VALUES ('Futbol - Cancha 2', 1, 17000, TRUE, TRUE);

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
VALUES ('Tenis - Cancha 1', 2, 10000, FALSE, TRUE);

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
VALUES ('Tenis - Cancha 2', 2, 12000, TRUE, TRUE);

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
VALUES ('Padel - Cancha 1', 3, 14000, TRUE, TRUE);

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
VALUES ('Padel - Cancha 2', 3, 16000, FALSE, TRUE);

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
VALUES ('Basquet - Cancha 1', 4, 15000, TRUE, TRUE);

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
VALUES ('Basquet - Cancha 2', 4, 18000, FALSE, TRUE);

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
VALUES ('Voley - Cancha 1', 5, 12000, TRUE, TRUE);

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
VALUES ('Voley - Cancha 2', 5, 14000, FALSE, FALSE);


-- =========================================
-- SOCIOS (20)
-- =========================================

INSERT INTO socios (nombre, email, activo)
VALUES ('Juan Perez', 'juan.perez@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Maria Gonzalez', 'maria.gonzalez@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Pedro Rodriguez', 'pedro.rodriguez@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Lucia Fernandez', 'lucia.fernandez@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Carlos Martinez', 'carlos.martinez@gmail.com', FALSE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Sofia Lopez', 'sofia.lopez@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Martin Sanchez', 'martin.sanchez@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Valentina Romero', 'valentina.romero@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Nicolas Torres', 'nicolas.torres@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Camila Alvarez', 'camila.alvarez@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Federico Diaz', 'federico.diaz@gmail.com', FALSE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Agustina Ruiz', 'agustina.ruiz@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Matias Castro', 'matias.castro@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Julieta Silva', 'julieta.silva@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Diego Molina', 'diego.molina@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Florencia Vega', 'florencia.vega@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Tomas Herrera', 'tomas.herrera@gmail.com', FALSE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Carolina Acosta', 'carolina.acosta@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Gonzalo Medina', 'gonzalo.medina@gmail.com', TRUE);

INSERT INTO socios (nombre, email, activo)
VALUES ('Paula Navarro', 'paula.navarro@gmail.com', TRUE);


-- =========================================
-- RESERVAS (20)
-- =========================================

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (1, 1, '2026-09-21 18:00:00', '2026-09-21 19:00:00',
'confirmada', 15000, 15000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (2, 2, '2026-09-21 20:00:00', '2026-09-21 22:00:00',
'confirmada', 17000, 34000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (3, 3, '2026-09-22 17:00:00', '2026-09-22 18:00:00',
'confirmada', 10000, 10000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (4, 4, '2026-09-22 19:00:00', '2026-09-22 20:00:00',
'cancelada', 12000, 12000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (5, 5, '2026-09-23 18:00:00', '2026-09-23 19:00:00',
'confirmada', 14000, 14000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (6, 6, '2026-09-23 20:00:00', '2026-09-23 21:00:00',
'pendiente', 16000, 16000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (7, 7, '2026-09-24 16:00:00', '2026-09-24 17:00:00',
'confirmada', 15000, 15000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (8, 8, '2026-09-24 18:00:00', '2026-09-24 20:00:00',
'confirmada', 18000, 36000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (9, 9, '2026-09-25 19:00:00', '2026-09-25 20:00:00',
'confirmada', 12000, 12000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (10, 10, '2026-09-25 20:00:00', '2026-09-25 21:00:00',
'cancelada', 14000, 14000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (11, 1, '2026-09-26 17:00:00', '2026-09-26 18:00:00',
'confirmada', 15000, 15000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (12, 2, '2026-09-26 19:00:00', '2026-09-26 20:00:00',
'pendiente', 17000, 17000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (13, 3, '2026-09-27 10:00:00', '2026-09-27 11:00:00',
'confirmada', 10000, 10000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (14, 4, '2026-09-27 15:00:00', '2026-09-27 16:00:00',
'confirmada', 12000, 12000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (15, 5, '2026-09-28 16:00:00', '2026-09-28 18:00:00',
'confirmada', 14000, 28000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (16, 6, '2026-09-28 18:00:00', '2026-09-28 19:00:00',
'confirmada', 16000, 16000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (17, 7, '2026-09-29 19:00:00', '2026-09-29 20:00:00',
'cancelada', 15000, 15000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (18, 8, '2026-09-30 17:00:00', '2026-09-30 19:00:00',
'confirmada', 18000, 36000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (19, 9, '2026-10-01 18:00:00', '2026-10-01 19:00:00',
'pendiente', 12000, 12000);

INSERT INTO reservas
(id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, total)
VALUES (20, 10, '2026-10-02 20:00:00', '2026-10-02 21:00:00',
'confirmada', 14000, 14000);