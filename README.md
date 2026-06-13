# ObligatorioBD

Fecha de entrega: 14/6/2026

Sistema de gestión de deportes universitarios. Permite administrar estudiantes, disciplinas, espacios deportivos, actividades e inscripciones mediante una aplicación de consola en Python conectada a una base de datos MySQL.

---

## Requisitos previos

Antes de comenzar, asegurate de tener instalado:

- **MySQL Server** (versión 8.0 o superior recomendada)
- **Python** (versión 3.10 o superior)
- **pip** (incluido con Python)

---

## 1. Configurar la base de datos (main.sql)

El archivo `BD/main.sql` crea la base de datos, todas las tablas, el trigger de validación, los datos de ejemplo y los usuarios MySQL con sus permisos.

### Paso 1 — Abrir una terminal y conectarse a MySQL como root

```bash
mysql -u root -p
```

Ingresá tu contraseña de root cuando se solicite.

### Paso 2 — Ejecutar el script SQL

Desde dentro de la sesión MySQL:

```sql
source /ruta/completa/al/proyecto/BD/main.sql
```

> Reemplazá `/ruta/completa/al/proyecto/` con la ruta real donde clonaste el repositorio.
> Ejemplo en Mac: `source /Users/tuUsuario/Documents/ObligatorioBD/BD/main.sql`

**Alternativamente**, podés ejecutarlo directamente desde la terminal sin entrar a MySQL:

```bash
mysql -u root -p < BD/main.sql
```

### Paso 3 — Verificar que todo se creó correctamente

Dentro de MySQL ejecutá:

```sql
USE gestion_deportes_universidad;
SHOW TABLES;
```

Deberías ver las siguientes tablas:

```
+-----------------------------------+
| Tables_in_gestion_deportes_univer |
+-----------------------------------+
| ACTIVIDAD                         |
| ASISTENCIA                        |
| DISCIPLINA                        |
| ESPACIO_DEPORTIVO                 |
| ESTUDIANTE                        |
| INSCRIPCION                       |
+-----------------------------------+
```

Para verificar que el trigger se creó:

```sql
SHOW TRIGGERS;
```

Debería aparecer `validar_cupo_inscripcion`.

> **Importante:** si ya habías ejecutado el script antes y querés reiniciar la base de datos desde cero, primero eliminala y volvé a correr el script:
> ```sql
> DROP DATABASE IF EXISTS gestion_deportes_universidad;
> ```
> Luego ejecutá `main.sql` nuevamente.

---

## 2. Configurar el entorno Python

### Paso 1 — Crear un entorno virtual

Desde la carpeta raíz del proyecto:

```bash
python3 -m venv .venv
```

### Paso 2 — Activar el entorno virtual

**En Mac/Linux:**
```bash
source .venv/bin/activate
```

**En Windows:**
```bash
.venv\Scripts\activate
```

Cuando el entorno está activo, verás `(.venv)` al inicio de tu terminal.

### Paso 3 — Instalar las dependencias

```bash
pip install -r python/requirements.txt
```

---

## 3. Ejecutar la aplicación (app.py)

Desde la carpeta raíz del proyecto, con el entorno virtual activado:

```bash
python python/app.py
```

---

## 4. Uso de la aplicación

Al iniciar, el programa pedirá un **rol** y una **contraseña**.

### Roles disponibles y sus contraseñas

| Rol | Contraseña |
|---|---|
| `administrador` | `Admin2025.` |
| `profesor` | `Profesor2025.` |
| `estudiante` | `Estudiante2025.` |

### Menú según rol

**Administrador** — acceso completo:
- ABM Estudiantes (insertar, editar, eliminar)
- ABM Disciplinas
- ABM Espacios Deportivos
- ABM Actividades
- Inscribir estudiantes en actividades
- Registrar asistencia
- Consultas del sistema

**Profesor** — acceso parcial:
- Registrar asistencia
- Consultas del sistema (10 consultas disponibles)

**Estudiante** — acceso limitado:
- Ver actividades con cupos disponibles
- Inscribirse en una actividad (ingresando su número de documento)

### Navegación

Después de cada acción, el programa pregunta:
- `¿Desea realizar otra acción? (s/n)` — para continuar o salir
- `¿Desea cambiar de usuario? (s/n)` — para iniciar sesión con otro rol sin reiniciar

---

---

## 5. Correr con Docker (alternativa)

Si tenés Docker instalado, podés levantar todo sin instalar MySQL ni Python manualmente.

### Requisito

- **Docker Desktop** instalado y corriendo

### Paso 1 — Construir y levantar los contenedores

Desde la carpeta raíz del proyecto:

```bash
docker compose up --build
```

Esto levanta dos contenedores:
- `db` — MySQL 8.0 con la base de datos ya inicializada (ejecuta `main.sql` automáticamente)
- `app` — la aplicación Python

> La primera vez tarda un poco más porque descarga la imagen de MySQL y construye la imagen de Python.

### Paso 2 — Conectarse a la aplicación interactiva

Como `app.py` usa `input()`, necesitás correrlo con una terminal interactiva:

```bash
docker compose run --rm app
```

Esto inicia la aplicación en tu terminal y podés usarla normalmente.

> `docker compose up` sola no es suficiente para apps interactivas — siempre usá `docker compose run --rm app`.

### Detener los contenedores

```bash
docker compose down
```

Para también eliminar los datos de MySQL (volumen):

```bash
docker compose down -v
```

---

## Estructura del repositorio

```
ObligatorioBD/
├── BD/
│   ├── main.sql             # Script SQL: tablas, trigger, datos, usuarios
│   └── docker_grants.sql    # Permisos extra para Docker (host '%')
├── python/
│   ├── app.py               # Aplicación de consola
│   └── requirements.txt     # Dependencias Python
├── Dockerfile               # Imagen Docker para app.py
├── docker-compose.yml       # Orquestación MySQL + Python
├── .dockerignore
└── README.md
```

---

## Solución de problemas frecuentes

**Error al conectar a MySQL:**
Verificá que el servidor MySQL esté corriendo:
```bash
# Mac (Homebrew)
brew services start mysql

# Linux
sudo systemctl start mysql
```

**Error "Access denied" al conectar:**
Asegurate de haber ejecutado `main.sql` completo como root. Los usuarios `administrador`, `profesor` y `estudiante` se crean automáticamente con el script.

**Error "No module named 'mysql'":**
El entorno virtual no está activado o las dependencias no están instaladas. Ejecutá:
```bash
source .venv/bin/activate
pip install -r python/requirements.txt
```
