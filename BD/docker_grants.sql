-- Permisos para conexiones desde otros contenedores Docker (host '%')


CREATE USER IF NOT EXISTS 'administrador'@'%' IDENTIFIED BY 'Admin2025.';
GRANT ALL PRIVILEGES ON gestion_deportes_universidad.* TO 'administrador'@'%';

CREATE USER IF NOT EXISTS 'profesor'@'%' IDENTIFIED BY 'Profesor2025.';
GRANT SELECT ON gestion_deportes_universidad.ESTUDIANTE TO 'profesor'@'%';
GRANT SELECT ON gestion_deportes_universidad.DISCIPLINA TO 'profesor'@'%';
GRANT SELECT ON gestion_deportes_universidad.ESPACIO_DEPORTIVO TO 'profesor'@'%';
GRANT SELECT ON gestion_deportes_universidad.ACTIVIDAD TO 'profesor'@'%';
GRANT SELECT ON gestion_deportes_universidad.INSCRIPCION TO 'profesor'@'%';
GRANT SELECT, INSERT ON gestion_deportes_universidad.ASISTENCIA TO 'profesor'@'%';

CREATE USER IF NOT EXISTS 'estudiante'@'%' IDENTIFIED BY 'Estudiante2025.';
GRANT SELECT ON gestion_deportes_universidad.ACTIVIDAD TO 'estudiante'@'%';
GRANT SELECT, INSERT ON gestion_deportes_universidad.INSCRIPCION TO 'estudiante'@'%';
GRANT SELECT ON gestion_deportes_universidad.ESTUDIANTE TO 'estudiante'@'%';

FLUSH PRIVILEGES;
