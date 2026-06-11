from flask import Flask, request, jsonify
import mysql.connector


app = Flask(__name__)

cnx = mysql.connector.connect(
    user='root',
    password='Locostib2005.',
    host='127.0.0.1',
    database='gestion_deportes_universidad'
)


# =====================
# ENDPOINTS API (JSON)
# =====================

@app.route("/api/estudiantes", methods=["GET"])
def api_get_estudiantes():
    cursor = cnx.cursor()
    cursor.execute("SELECT id_estudiante, documento, nombre, apellido, email, carrera, facultad FROM ESTUDIANTE")
    rows = cursor.fetchall()
    data = [{'id': r[0], 'documento': r[1], 'nombre': r[2], 'apellido': r[3], 'email': r[4], 'carrera': r[5], 'facultad': r[6]} for r in rows]
    return jsonify(data)


@app.route("/api/estudiantes", methods=["POST"])
def api_create_estudiante():
    data = request.json
    try:
        cursor = cnx.cursor()
        cursor.execute(
            "INSERT INTO ESTUDIANTE (documento, nombre, apellido, email, carrera, facultad) VALUES (%s, %s, %s, %s, %s, %s)",
            (data.get('documento'), data.get('nombre'), data.get('apellido'), data.get('email'), data.get('carrera'), data.get('facultad'))
        )
        cnx.commit()
        return jsonify({'ok': True, 'msg': 'Estudiante creado'}), 201
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 400


@app.route("/api/estudiantes/<int:sid>", methods=["PUT"])
def api_update_estudiante(sid):
    data = request.json
    try:
        cursor = cnx.cursor()
        cursor.execute(
            "UPDATE ESTUDIANTE SET documento=%s, nombre=%s, apellido=%s, email=%s, carrera=%s, facultad=%s WHERE id_estudiante=%s",
            (data.get('documento'), data.get('nombre'), data.get('apellido'), data.get('email'), data.get('carrera'), data.get('facultad'), sid)
        )
        cnx.commit()
        return jsonify({'ok': True, 'msg': 'Estudiante actualizado'})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 400


@app.route("/api/estudiantes/<int:sid>", methods=["DELETE"])
def api_delete_estudiante(sid):
    try:
        cursor = cnx.cursor()
        cursor.execute("DELETE FROM ESTUDIANTE WHERE id_estudiante=%s", (sid,))
        cnx.commit()
        return jsonify({'ok': True, 'msg': 'Estudiante eliminado'})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 400


@app.route("/estudiantes")
def estudiantes():

    cursor = cnx.cursor()

    cursor.execute("""
        SELECT id_estudiante,
               nombre,
               apellido,
               documento
        FROM ESTUDIANTE
    """)

    estudiantes = cursor.fetchall()

    html = """
    <h1>Estudiantes</h1>

    <table border='1'>
        <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Apellido</th>
            <th>Documento</th>
        </tr>
    """

    for e in estudiantes:
        html += f"""
        <tr>
            <td>{e[0]}</td>
            <td>{e[1]}</td>
            <td>{e[2]}</td>
            <td>{e[3]}</td>
        </tr>
        """

    html += "</table>"
    
    return html

@app.route("/actividades")
def actividades():

    cursor = cnx.cursor()

    cursor.execute("""
        SELECT id_actividad,
               nombre_actividad,
               cupo_maximo,
               estado
        FROM ACTIVIDAD
    """)

    actividades = cursor.fetchall()

    html = """
    <h1>Actividades</h1>

    <table border='1'>
        <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Cupo</th>
            <th>Estado</th>
        </tr>
    """

    for a in actividades:
        html += f"""
        <tr>
            <td>{a[0]}</td>
            <td>{a[1]}</td>
            <td>{a[2]}</td>
            <td>{a[3]}</td>
        </tr>
        """

    html += "</table>"

    return html

def inscirpcion_estudiante(cnx, id_estudiante, id_actividad):

    cursor = cnx.cursor(dictionary=True)

    cursor.execute("""

        SELECT cupo_maximo, estado

        FROM ACTIVIDAD

        WHERE id_actividad = %s

    """, (id_actividad,))

    actividad = cursor.fetchone()

    if actividad is None:

        return "La actividad no existe"

    if actividad['estado'] != 'abierta':

        return "La actividad no está abierta"

    cursor.execute("""

        SELECT *

        FROM INSCRIPCION

        WHERE id_estudiante = %s

        AND id_actividad = %s

        AND estado_inscripcion != 'cancelada'

    """, (id_estudiante, id_actividad))

    duplicado = cursor.fetchone()

    if duplicado:

        return "El estudiante ya está inscripto"

    cursor.execute("""

        SELECT COUNT(*) as cupo_actual

        FROM INSCRIPCION

        WHERE id_actividad = %s

        AND estado_inscripcion = 'inscripto'

    """, (id_actividad,))

    resultado = cursor.fetchone()

    if resultado['cupo_actual'] < actividad['cupo_maximo']:

        estado = "inscripto"

    else:

        estado = "lista_espera"

    cursor.execute("""

        INSERT INTO INSCRIPCION

        (id_estudiante,id_actividad,fecha_inscripcion,estado_inscripcion)

        VALUES (%s,%s,CURDATE(),%s)

    """, (id_estudiante, id_actividad, estado))

    cnx.commit()

    return f"Inscripción realizada. Estado: {estado}"


@app.route("/inscribir", methods=["GET", "POST"])
def inscribir():

    if request.method == "POST":

        id_estudiante = int(
            request.form["id_estudiante"]
        )

        id_actividad = int(
            request.form["id_actividad"]
        )

        mensaje = inscirpcion_estudiante(
            cnx,
            id_estudiante,
            id_actividad
        )

        return f"""
        <h2>{mensaje}</h2>
        <a href='/'>Volver</a>
        """

    return """
    <h1>Nueva inscripción</h1>

    <form method='POST'>

        ID estudiante:
        <input type='number' name='id_estudiante'>

        <br><br>

        ID actividad:
        <input type='number' name='id_actividad'>

        <br><br>

        <button type='submit'>
            Inscribir
        </button>

    </form>
    """

@app.route("/")
def index():
    return '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Gestión Deportes</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #333; }
        .tabs button { padding: 10px 20px; cursor: pointer; background: #ddd; border: none; font-size: 14px; }
        .tabs button.active { background: #0066cc; color: white; }
        .tab-content { display: none; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .tab-content.active { display: block; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        table, th, td { border: 1px solid #ddd; }
        th { background: #0066cc; color: white; padding: 10px; text-align: left; }
        td { padding: 10px; }
        button { padding: 8px 15px; cursor: pointer; background: #0066cc; color: white; border: none; border-radius: 3px; }
        button:hover { background: #004999; }
        button.danger { background: #cc0000; }
        button.danger:hover { background: #990000; }
        input, select { padding: 8px; margin: 5px 0; width: 100%; max-width: 300px; }
        form { margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 3px; }
        .success { color: green; font-weight: bold; }
        .error { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Gestión Deportes Universitarios</h1>
    
    <div class="tabs">
        <button class="tab-btn active" onclick="showTab('estudiantes')">Estudiantes</button>
        <button class="tab-btn" onclick="showTab('actividades')">Actividades</button>
        <button class="tab-btn" onclick="showTab('inscripciones')">Inscripciones</button>
    </div>

    <!-- PESTAÑA ESTUDIANTES -->
    <div id="estudiantes" class="tab-content active">
        <h2>Gestión de Estudiantes</h2>
        
        <h3>Crear Estudiante</h3>
        <form id="formNuevoEstudiante">
            <input type="number" id="estDocumento" placeholder="Documento" required>
            <input type="text" id="estNombre" placeholder="Nombre" required>
            <input type="text" id="estApellido" placeholder="Apellido" required>
            <input type="email" id="estEmail" placeholder="Email" required>
            <input type="text" id="estCarrera" placeholder="Carrera" required>
            <input type="text" id="estFacultad" placeholder="Facultad" required>
            <button type="button" onclick="crearEstudiante()">Crear</button>
        </form>
        <div id="msgNuevoEst"></div>

        <h3>Lista de Estudiantes</h3>
        <button onclick="cargarEstudiantes()">Recargar</button>
        <table id="tabEstudiantes">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Documento</th>
                    <th>Nombre</th>
                    <th>Apellido</th>
                    <th>Email</th>
                    <th>Carrera</th>
                    <th>Facultad</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>

        <h3 style="margin-top: 30px;">Editar Estudiante</h3>
        <form id="formEditarEstudiante">
            <input type="number" id="edtId" placeholder="ID a editar" required>
            <input type="number" id="edtDocumento" placeholder="Documento" required>
            <input type="text" id="edtNombre" placeholder="Nombre" required>
            <input type="text" id="edtApellido" placeholder="Apellido" required>
            <input type="email" id="edtEmail" placeholder="Email" required>
            <input type="text" id="edtCarrera" placeholder="Carrera" required>
            <input type="text" id="edtFacultad" placeholder="Facultad" required>
            <button type="button" onclick="editarEstudiante()">Guardar cambios</button>
        </form>
        <div id="msgEditEst"></div>
    </div>

    <!-- PESTAÑA ACTIVIDADES -->
    <div id="actividades" class="tab-content">
        <h2>Actividades</h2>
        <button onclick="cargarActividades()">Cargar actividades</button>
        <table id="tabActividades">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Cupo Máximo</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>

    <!-- PESTAÑA INSCRIPCIONES -->
    <div id="inscripciones" class="tab-content">
        <h2>Inscribir Estudiante</h2>
        <form id="formInscripcion">
            <label>ID Estudiante: <input type="number" id="insEstudiante" required></label><br>
            <label>ID Actividad: <input type="number" id="insActividad" required></label><br>
            <button type="button" onclick="inscribir()">Inscribir</button>
        </form>
        <div id="msgInscripcion"></div>
    </div>

    <script>
        function showTab(tabName) {
            const contents = document.querySelectorAll('.tab-content');
            const btns = document.querySelectorAll('.tab-btn');
            contents.forEach(c => c.classList.remove('active'));
            btns.forEach(b => b.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            if (tabName === 'estudiantes') cargarEstudiantes();
            if (tabName === 'actividades') cargarActividades();
        }

        async function cargarEstudiantes() {
            const res = await fetch('/api/estudiantes');
            const estudiantes = await res.json();
            const tbody = document.querySelector('#tabEstudiantes tbody');
            tbody.innerHTML = '';
            estudiantes.forEach(e => {
                tbody.innerHTML += `
                <tr>
                    <td>${e.id}</td>
                    <td>${e.documento}</td>
                    <td>${e.nombre}</td>
                    <td>${e.apellido}</td>
                    <td>${e.email}</td>
                    <td>${e.carrera}</td>
                    <td>${e.facultad}</td>
                    <td>
                        <button onclick="cargarEditForm(${e.id}, ${e.documento}, '${e.nombre}', '${e.apellido}', '${e.email}', '${e.carrera}', '${e.facultad}')">Editar</button>
                        <button class="danger" onclick="borrarEstudiante(${e.id})">Borrar</button>
                    </td>
                </tr>`;
            });
        }

        function cargarEditForm(id, doc, nom, ape, email, carr, fac) {
            document.getElementById('edtId').value = id;
            document.getElementById('edtDocumento').value = doc;
            document.getElementById('edtNombre').value = nom;
            document.getElementById('edtApellido').value = ape;
            document.getElementById('edtEmail').value = email;
            document.getElementById('edtCarrera').value = carr;
            document.getElementById('edtFacultad').value = fac;
            document.querySelector('html').scrollTop = document.querySelector('#formEditarEstudiante').offsetTop;
        }

        async function crearEstudiante() {
            const data = {
                documento: parseInt(document.getElementById('estDocumento').value),
                nombre: document.getElementById('estNombre').value,
                apellido: document.getElementById('estApellido').value,
                email: document.getElementById('estEmail').value,
                carrera: document.getElementById('estCarrera').value,
                facultad: document.getElementById('estFacultad').value
            };
            const res = await fetch('/api/estudiantes', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await res.json();
            const msg = document.getElementById('msgNuevoEst');
            if (result.ok) {
                msg.innerHTML = '<span class="success">' + result.msg + '</span>';
                document.getElementById('formNuevoEstudiante').reset();
                cargarEstudiantes();
            } else {
                msg.innerHTML = '<span class="error">' + result.msg + '</span>';
            }
        }

        async function editarEstudiante() {
            const id = parseInt(document.getElementById('edtId').value);
            const data = {
                documento: parseInt(document.getElementById('edtDocumento').value),
                nombre: document.getElementById('edtNombre').value,
                apellido: document.getElementById('edtApellido').value,
                email: document.getElementById('edtEmail').value,
                carrera: document.getElementById('edtCarrera').value,
                facultad: document.getElementById('edtFacultad').value
            };
            const res = await fetch(`/api/estudiantes/${id}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await res.json();
            const msg = document.getElementById('msgEditEst');
            if (result.ok) {
                msg.innerHTML = '<span class="success">' + result.msg + '</span>';
                cargarEstudiantes();
            } else {
                msg.innerHTML = '<span class="error">' + result.msg + '</span>';
            }
        }

        async function borrarEstudiante(id) {
            if (confirm('¿Seguro que deseas borrar este estudiante?')) {
                const res = await fetch(`/api/estudiantes/${id}`, {method: 'DELETE'});
                const result = await res.json();
                if (result.ok) {
                    alert('Estudiante eliminado');
                    cargarEstudiantes();
                } else {
                    alert('Error: ' + result.msg);
                }
            }
        }

        async function cargarActividades() {
            const res = await fetch('/api/actividades');
            const actividades = await res.json();
            const tbody = document.querySelector('#tabActividades tbody');
            tbody.innerHTML = '';
            actividades.forEach(a => {
                tbody.innerHTML += `
                <tr>
                    <td>${a.id}</td>
                    <td>${a.nombre}</td>
                    <td>${a.cupo}</td>
                    <td>${a.estado}</td>
                </tr>`;
            });
        }

        async function inscribir() {
            const id_est = parseInt(document.getElementById('insEstudiante').value);
            const id_act = parseInt(document.getElementById('insActividad').value);
            const res = await fetch('/inscribir', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `id_estudiante=${id_est}&id_actividad=${id_act}`
            });
            const text = await res.text();
            document.getElementById('msgInscripcion').innerHTML = text;
        }
    </script>
</body>
</html>'''


@app.route("/api/actividades")
def api_get_actividades():
    cursor = cnx.cursor()
    cursor.execute("SELECT id_actividad, nombre_actividad, cupo_maximo, estado FROM ACTIVIDAD")
    rows = cursor.fetchall()
    data = [{'id': r[0], 'nombre': r[1], 'cupo': r[2], 'estado': r[3]} for r in rows]
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)