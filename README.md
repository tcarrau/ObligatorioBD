# ObligatorioBD

Fecha de entrega: 14/6/2026

## Descripción

Proyecto de gestión de deportes universitarios con base de datos MySQL y acceso desde Python.

## Estructura del repositorio

- `BD/main.sql`: script SQL para crear la base de datos, tablas y datos de ejemplo.
- `python/app.py`: aplicación Python que se conecta a MySQL y ejecuta consultas/operaciones.
- `python/requirements.txt`: dependencias de Python.

## Configuración inicial

1. Instala MySQL y asegúrate de que el servidor esté funcionando.
2. Carga la base de datos:

```bash
mysql -u root -p < BD/main.sql
```

3. Crea y activa un entorno virtual de Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Instala dependencias:

```bash
pip install -r python/requirements.txt
```

5. Ajusta las credenciales MySQL en `python/app.py` si es necesario.

## Uso

Ejecuta la aplicación desde la carpeta raíz:

```bash
python python/app.py
```

> Nota: `python/app.py` usa credenciales hardcodeadas. Cámbialas si tu contraseña o usuario es distinto.

