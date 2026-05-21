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
    estado ENUM('abierta', 'cerrada', 'finalizada', 'cancelada') NOT NULL DEFAULT 'Pendiente',
    PRIMARY KEY(id_actividad),
    FOREIGN KEY(id_espacio) REFERENCES ESPACIO_DEPORTIVO(id_espacio),
    FOREIGN KEY(id_disciplina) REFERENCES DISCIPLINA(id_disciplina)
);

CREATE TABLE INSCRIPCION(
    id_inscripcion int AUTO_INCREMENT,
    id_estudiante int,
    id_actividad int,
    fecha_inscripcion DATE,
    estado ENUM('abierta', 'cerrada', 'finalizada', 'cancelada') NOT NULL DEFAULT 'Pendiente',
    PRIMARY KEY(id_inscripcion),
    FOREIGN KEY(id_estudiante) REFERENCES ESTUDIANTE(id_estudiante),
    FOREIGN KEY(id_actividad) REFERENCES ACTIVIDAD(id_actividad)

);
