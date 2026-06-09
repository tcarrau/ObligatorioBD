CREATE DATABASE IF NOT EXISTS gestion_deportes_universidad;
USE gestion_deportes_universidad;

CREATE TABLE ESTUDIANTE(
    id_estudiante int AUTO_INCREMENT,
    documento int,
    nombre varchar(50),
    apellido varchar(50),
    email varchar(50),
    carrera varchar(50),
    facultad varchar(50),
    PRIMARY KEY(id_estudiante)
);

CREATE TABLE DISCIPLINA(
    id_disciplina int AUTO_INCREMENT,
    nombre_disciplina varchar(50),
    PRIMARY KEY(id_disciplina)
);

CREATE TABLE ESPACIO_DEPORTIVO(
    id_espacio int AUTO_INCREMENT,
    nombre_espacio varchar(50),
    ubicacion varchar(50),
    capacidad int,
    PRIMARY KEY(id_espacio)
);




CREATE TABLE ACTIVIDAD(
    id_actividad int AUTO_INCREMENT,
    nombre_actividad varchar(50),
    id_espacio int,
    id_disciplina int,
    cupo_maximo int,
    dia_semana varchar(50),
    horario_inicio TIME,
    horario_fin TIME,
    estado ENUM('abierta', 'cerrada', 'finalizada', 'cancelada') NOT NULL DEFAULT 'abierta',
    PRIMARY KEY(id_actividad),
    FOREIGN KEY(id_espacio) REFERENCES ESPACIO_DEPORTIVO(id_espacio),
    FOREIGN KEY(id_disciplina) REFERENCES DISCIPLINA(id_disciplina)
);

CREATE TABLE INSCRIPCION(
    id_inscripcion int AUTO_INCREMENT,
    id_estudiante int,
    id_actividad int,
    fecha_inscripcion DATE,
    estado_inscripcion ENUM('inscripto', 'lista_espera', 'cancelada'),
    PRIMARY KEY(id_inscripcion),
    FOREIGN KEY(id_estudiante) REFERENCES ESTUDIANTE(id_estudiante),
    FOREIGN KEY(id_actividad) REFERENCES ACTIVIDAD(id_actividad)

);

CREATE TABLE ASISTENCIA(
    id_asistencia int AUTO_INCREMENT,
    id_actividad int,
    fecha DATE,
    asistio bool,
    id_estudiante int,

    PRIMARY KEY(id_asistencia),
    FOREIGN KEY(id_actividad) REFERENCES ACTIVIDAD(id_actividad),
    FOREIGN KEY(id_estudiante) REFERENCES ESTUDIANTE(id_estudiante)
);
-- =========================
-- INSERTS ESTUDIANTE
-- =========================

INSERT INTO ESTUDIANTE (documento, nombre, apellido, email, carrera, facultad) VALUES
(52345678, 'Juan', 'Pérez', 'juan.perez@fing.edu.uy', 'Ingeniería en Computación', 'FING'),
(51234567, 'María', 'Gómez', 'maria.gomez@fcea.edu.uy', 'Contador Público', 'FCEA'),
(49876543, 'Lucía', 'Fernández', 'lucia.fernandez@fmed.edu.uy', 'Medicina', 'FMED'),
(48765432, 'Santiago', 'Rodríguez', 'santiago.rodriguez@fing.edu.uy', 'Ingeniería Eléctrica', 'FING'),
(47654321, 'Valentina', 'Suárez', 'valentina.suarez@fder.edu.uy', 'Abogacía', 'FDER'),
(46543210, 'Mateo', 'López', 'mateo.lopez@fing.edu.uy', 'Ingeniería Civil', 'FING'),
(45432109, 'Camila', 'Martínez', 'camila.martinez@fcea.edu.uy', 'Administración', 'FCEA'),
(44321098, 'Agustín', 'Silva', 'agustin.silva@fing.edu.uy', 'Ingeniería Mecánica', 'FING'),
(43210987, 'Florencia', 'Ruiz', 'florencia.ruiz@fagro.edu.uy', 'Agronomía', 'FAGRO'),
(42109876, 'Nicolás', 'Torres', 'nicolas.torres@fing.edu.uy', 'Ingeniería en Computación', 'FING'),
(41098765, 'Sofía', 'Morales', 'sofia.morales@fpsi.edu.uy', 'Psicología', 'FPSI'),
(40987654, 'Martín', 'Castro', 'martin.castro@fing.edu.uy', 'Ingeniería Química', 'FING'),
(39876543, 'Paula', 'Vega', 'paula.vega@fcea.edu.uy', 'Economía', 'FCEA'),
(38765432, 'Diego', 'Acosta', 'diego.acosta@fing.edu.uy', 'Ingeniería Industrial', 'FING'),
(37654321, 'Micaela', 'Pintos', 'micaela.pintos@fder.edu.uy', 'Relaciones Internacionales', 'FDER');

-- =========================
-- INSERTS DISCIPLINA
-- =========================

INSERT INTO DISCIPLINA (nombre_disciplina) VALUES
('Fútbol'),
('Basketball'),
('Voley'),
('Handball'),
('Natación'),
('Tenis'),
('Running'),
('Yoga'),
('Crossfit'),
('Ajedrez');

-- =========================
-- INSERTS ESPACIO_DEPORTIVO
-- =========================

INSERT INTO ESPACIO_DEPORTIVO (nombre_espacio, ubicacion, capacidad) VALUES
('Cancha Central', 'Campus Principal', 200),
('Gimnasio Norte', 'Edificio Norte', 80),
('Piscina Olímpica', 'Complejo Deportivo', 120),
('Cancha Techada', 'Campus Principal', 150),
('Sala Fitness', 'Edificio Sur', 60),
('Pista Atlética', 'Complejo Deportivo', 300),
('Cancha Auxiliar', 'Campus Oeste', 100),
('Sala de Yoga', 'Edificio Bienestar', 40);

-- =========================
-- INSERTS ACTIVIDAD
-- =========================

INSERT INTO ACTIVIDAD 
(nombre_actividad, id_espacio, id_disciplina, cupo_maximo, dia_semana, horario_inicio, horario_fin, estado)
VALUES
('Fútbol Recreativo', 1, 1, 22, 'Lunes', '18:00:00', '20:00:00', 'abierta'),
('Basketball Intermedio', 2, 2, 15, 'Martes', '19:00:00', '21:00:00', 'abierta'),
('Voley Mixto', 4, 3, 18, 'Miércoles', '17:00:00', '19:00:00', 'abierta'),
('Handball Avanzado', 4, 4, 16, 'Jueves', '20:00:00', '22:00:00', 'cerrada'),
('Natación Libre', 3, 5, 30, 'Viernes', '08:00:00', '10:00:00', 'abierta'),
('Tenis Principiantes', 7, 6, 10, 'Sábado', '10:00:00', '12:00:00', 'abierta'),
('Running Club', 6, 7, 40, 'Domingo', '09:00:00', '11:00:00', 'abierta'),
('Yoga Relax', 8, 8, 20, 'Martes', '18:30:00', '19:30:00', 'abierta'),
('Crossfit Funcional', 5, 9, 25, 'Lunes', '07:00:00', '08:30:00', 'cerrada'),
('Torneo de Ajedrez', 2, 10, 32, 'Viernes', '16:00:00', '20:00:00', 'finalizada');

-- =========================
-- INSERTS INSCRIPCION
-- =========================

INSERT INTO INSCRIPCION (id_estudiante, id_actividad, fecha_inscripcion, estado_inscripcion) VALUES
(1, 1, '2026-03-01', 'inscripto'),
(2, 1, '2026-03-02', 'inscripto'),
(3, 5, '2026-03-02', 'inscripto'),
(4, 2, '2026-03-03', 'inscripto'),
(5, 8, '2026-03-03', 'inscripto'),
(6, 9, '2026-03-04', 'cancelada'),
(7, 10, '2026-03-04', 'cancelada'),
(8, 4, '2026-03-05', 'cancelada'),
(9, 7, '2026-03-05', 'inscripto'),
(10, 1, '2026-03-06', 'inscripto'),
(11, 8, '2026-03-06', 'inscripto'),
(12, 9, '2026-03-07', 'cancelada'),
(13, 2, '2026-03-07', 'inscripto'),
(14, 6, '2026-03-08', 'inscripto'),
(15, 3, '2026-03-08', 'inscripto'),
(1, 7, '2026-03-09', 'inscripto'),
(2, 8, '2026-03-09', 'inscripto'),
(3, 10, '2026-03-10', 'cancelada'),
(4, 5, '2026-03-10', 'inscripto'),
(5, 3, '2026-03-11', 'inscripto');

-- Reinsertar asistencias igual que antes
INSERT INTO ASISTENCIA (id_actividad, fecha, asistio, id_estudiante) VALUES
-- Fútbol Recreativo (actividad 1)
(1, '2026-04-06', TRUE, 1),
(1, '2026-04-06', TRUE, 2),
(1, '2026-04-06', FALSE, 10),

-- Basketball Intermedio (actividad 2)
(2, '2026-04-07', TRUE, 4),
(2, '2026-04-07', TRUE, 13),

-- Voley Mixto (actividad 3)
(3, '2026-04-08', TRUE, 15),
(3, '2026-04-08', FALSE, 5),

-- Natación Libre (actividad 5)
(5, '2026-04-10', TRUE, 3),
(5, '2026-04-10', TRUE, 4),

-- Running Club (actividad 7)
(7, '2026-04-12', TRUE, 9),
(7, '2026-04-12', FALSE, 1),

-- Yoga Relax (actividad 8)
(8, '2026-04-07', TRUE, 5),
(8, '2026-04-07', TRUE, 11),
(8, '2026-04-07', FALSE, 2)
