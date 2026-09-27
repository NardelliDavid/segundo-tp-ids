
CREATE TABLE IF NOT EXISTS deportes (
	id_deporte INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

INSERT IGNORE INTO deportes (id_deporte, nombre)
VALUES
(1, 'futbol'),
(2, 'tenis'),
(3, 'padel');


CREATE TABLE IF NOT EXISTS canchas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    id_deporte INT NOT NULL,
    precio_hora INT NOT NULL, 
    techada BOOLEAN NOT NULL DEFAULT FALSE,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (id_deporte) REFERENCES deportes(id_deporte)
);
