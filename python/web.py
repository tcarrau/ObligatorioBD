from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

cnx = mysql.connector.connect(
    user='root',
    password='Locostib2005.',
    host='127.0.0.1',
    database='gestion_deportes_universidad'
)

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
        id_estudiante = int(request.form["id_estudiante"])
        id_actividad = int(request.form["id_actividad"])
        mensaje = inscirpcion_estudiante(cnx, id_estudiante, id_actividad)
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
        <button class="tab-btn" onclick="showTab('disciplinas')">Disciplinas</button>
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
            <input type="number" id="edtDocumento" placeholder="Nuevo Documento" required>
            <input type="text" id="edtNombre" placeholder="Nuevo Nombre" required>
            <input type="text" id="edtApellido" placeholder="Nuevo Apellido" required>
            <input type="email" id="edtEmail" placeholder="Nuevo Email" required>
            <input type="text" id="edtCarrera" placeholder="Nueva Carrera" required>
            <input type="text" id="edtFacultad" placeholder="Nueva Facultad" required>
            <button type="button" onclick="editarEstudiante()">Guardar cambios</button>
        </form>
        <div id="msgEditEst"></div>
    </div>

    <!-- PESTAÑA ACTIVIDADES -->
    <div id="actividades" class="tab-content">
        <h2>Actividades</h2>

        <h3>Crear Actividad</h3>
        <form id="formNuevaActividad">
            <input type="text" id="actNombre" placeholder="Nombre actividad" required>
            <input type="number" id="actCupo" placeholder="Cupo máximo" required>
            <select id="actEspacio">
                <option value="">-- Seleccionar espacio --</option>
            </select>
            <select id="actDisc">
                <option value="">-- Seleccionar disciplina --</option>
            </select>
            <select id="actDia">
                <option value="">-- Seleccionar día --</option>
                <option value="Lunes">Lunes</option>
                <option value="Martes">Martes</option>
                <option value="Miércoles">Miércoles</option>
                <option value="Jueves">Jueves</option>
                <option value="Viernes">Viernes</option>
                <option value="Sábado">Sábado</option>
                <option value="Domingo">Domingo</option>
            </select>
            <input type="time" id="actHorarioIni" placeholder="Hora inicio" required>
            <input type="time" id="actHorarioFin" placeholder="Hora fin" required>
            <select id="actEstado">
                <option value="abierta">abierta</option>
                <option value="cerrada">cerrada</option>
                <option value="finalizada">finalizada</option>
                <option value="cancelada">cancelada</option>
            </select>
            <button type="button" onclick="crearActividad()">Crear</button>
        </form>
        <div id="msgNuevaAct"></div>

        <h3>Lista de Actividades</h3>
        <button onclick="cargarActividades()">Recargar</button>
        <table id="tabActividades">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Disciplina</th>
                    <th>Espacio</th>
                    <th>Día</th>
                    <th>Hora Inicio</th>
                    <th>Hora Fin</th>
                    <th>Cupo</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>

        <h3 style="margin-top: 20px;">Editar Actividad</h3>
        <form id="formEditarActividad">
            <input type="number" id="edtActId" placeholder="ID a editar" required>
            <input type="text" id="edtActNombre" placeholder="Nuevo nombre" required>
            <input type="number" id="edtActCupo" placeholder="Nuevo cupo" required>
            <select id="edtActEspacio">
                <option value="">-- Seleccionar espacio --</option>
            </select>
            <select id="edtActDisc">
                <option value="">-- Seleccionar disciplina --</option>
            </select>
            <select id="edtActDia">
                <option value="">-- Seleccionar día --</option>
                <option value="Lunes">Lunes</option>
                <option value="Martes">Martes</option>
                <option value="Miércoles">Miércoles</option>
                <option value="Jueves">Jueves</option>
                <option value="Viernes">Viernes</option>
                <option value="Sábado">Sábado</option>
                <option value="Domingo">Domingo</option>
            </select>
            <input type="time" id="edtActHorarioIni" placeholder="Hora inicio" required>
            <input type="time" id="edtActHorarioFin" placeholder="Hora fin" required>
            <select id="edtActEstado">
                <option value="abierta">abierta</option>
                <option value="cerrada">cerrada</option>
                <option value="finalizada">finalizada</option>
                <option value="cancelada">cancelada</option>
            </select>
            <button type="button" onclick="editarActividad()">Guardar cambios</button>
        </form>
        <div id="msgEditAct"></div>
    </div>

    <!-- PESTAÑA DISCIPLINAS -->
    <div id="disciplinas" class="tab-content">
        <h2>Disciplinas Deportivas</h2>

        <h3>Crear Disciplina</h3>
        <form id="formNuevaDisciplina">
            <input type="text" id="discNombre" placeholder="Nombre disciplina" required>
            <button type="button" onclick="crearDisciplina()">Crear</button>
        </form>
        <div id="msgNuevaDisc"></div>

        <h3>Lista de Disciplinas</h3>
        <button onclick="cargarDisciplinas()">Recargar</button>
        <table id="tabDisciplinas">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>

        <h3 style="margin-top: 20px;">Editar Disciplina</h3>
        <form id="formEditarDisciplina">
            <input type="number" id="edtDiscId" placeholder="ID a editar" required>
            <input type="text" id="edtDiscNombre" placeholder="Nuevo nombre" required>
            <button type="button" onclick="editarDisciplina()">Guardar cambios</button>
        </form>
        <div id="msgEditDisc"></div>
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
            if (tabName === 'actividades') {
                Promise.all([obtenerDisciplinas(), obtenerEspacios()])
                    .then(([listaDisc, listaEsp]) => {
                        poblarSelectDisciplinas(listaDisc);
                        poblarSelectEspacios(listaEsp);
                        cargarActividades();
                    });
            }
            if (tabName === 'disciplinas') cargarDisciplinas();
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

        async function obtenerDisciplinas() {
            try {
                const res = await fetch('/api/disciplinas');
                if (!res.ok) return [];
                return await res.json();
            } catch (e) {
                return [];
            }
        }

        function poblarSelectDisciplinas(lista) {
            const actSel = document.getElementById('actDisc');
            const edtSel = document.getElementById('edtActDisc');
            if (!actSel || !edtSel) return;
            actSel.innerHTML = '<option value="">-- Seleccionar disciplina --</option>';
            edtSel.innerHTML = '<option value="">-- Seleccionar disciplina --</option>';
            lista.forEach(d => {
                actSel.innerHTML += `<option value="${d.id}">${d.nombre}</option>`;
                edtSel.innerHTML += `<option value="${d.id}">${d.nombre}</option>`;
            });
        }

        async function obtenerEspacios() {
            try {
                const res = await fetch('/api/espacios');
                if (!res.ok) return [];
                return await res.json();
            } catch (e) {
                return [];
            }
        }

        function poblarSelectEspacios(lista) {
            const actSel = document.getElementById('actEspacio');
            const edtSel = document.getElementById('edtActEspacio');
            if (!actSel || !edtSel) return;
            actSel.innerHTML = '<option value="">-- Seleccionar espacio --</option>';
            edtSel.innerHTML = '<option value="">-- Seleccionar espacio --</option>';
            lista.forEach(e => {
                actSel.innerHTML += `<option value="${e.id}">${e.nombre}</option>`;
                edtSel.innerHTML += `<option value="${e.id}">${e.nombre}</option>`;
            });
        }

        async function cargarActividades() {
            try {
                const res = await fetch('/api/actividades');
                if (!res.ok) {
                    const txt = await res.text();
                    document.getElementById('msgNuevaAct').innerHTML = '<span class="error">Error cargando actividades: ' + txt + '</span>';
                    return;
                }
                const actividades = await res.json();
                const tbody = document.querySelector('#tabActividades tbody');
                tbody.innerHTML = '';
                actividades.forEach(a => {
                    const discName = a.disciplina_nombre || '';
                    const espName = a.espacio_nombre || '';
                    tbody.innerHTML += `
                    <tr>
                        <td>${a.id}</td>
                        <td>${a.nombre}</td>
                        <td>${discName}</td>
                        <td>${espName}</td>
                        <td>${a.dia_semana || ''}</td>
                        <td>${a.horario_inicio || ''}</td>
                        <td>${a.horario_fin || ''}</td>
                        <td>${a.cupo}</td>
                        <td>${a.estado}</td>
                        <td>
                            <button onclick="cargarEditAct(${a.id}, '${(a.nombre||'').replace(/'/g, "\\'")}', ${a.cupo}, '${a.estado}', ${a.disciplina_id || 'null'}, ${a.espacio_id || 'null'}, '${(a.dia_semana||'').replace(/'/g, "\\'")}', '${(a.horario_inicio||'').replace(/'/g, "\\'")}', '${(a.horario_fin||'').replace(/'/g, "\\'")}')">Editar</button>
                            <button class="danger" onclick="borrarActividad(${a.id})">Borrar</button>
                        </td>
                    </tr>`;
                });
            } catch (err) {
                document.getElementById('msgNuevaAct').innerHTML = '<span class="error">' + err.message + '</span>';
            }
        }

        function cargarEditAct(id, nombre, cupo, estado, discId, espId, dia, horIni, horFin) {
            document.getElementById('edtActId').value = id;
            document.getElementById('edtActNombre').value = nombre;
            document.getElementById('edtActCupo').value = cupo;
            document.getElementById('edtActEstado').value = estado;
            if (discId !== null && discId !== undefined) document.getElementById('edtActDisc').value = discId;
            if (espId !== null && espId !== undefined) document.getElementById('edtActEspacio').value = espId;
            if (dia) document.getElementById('edtActDia').value = dia;
            if (horIni) document.getElementById('edtActHorarioIni').value = horIni;
            if (horFin) document.getElementById('edtActHorarioFin').value = horFin;
            document.querySelector('html').scrollTop = document.querySelector('#formEditarActividad').offsetTop;
        }

        function mostrarDisciplina(id, nombre) {
            if (!id) {
                alert('Sin disciplina asociada');
            } else {
                alert('Disciplina: ' + nombre + ' (ID ' + id + ')');
            }
        }

        async function crearActividad() {
            const data = {
                nombre: document.getElementById('actNombre').value,
                cupo: parseInt(document.getElementById('actCupo').value),
                estado: document.getElementById('actEstado').value,
                id_disciplina: document.getElementById('actDisc').value || null,
                id_espacio: document.getElementById('actEspacio').value || null,
                dia_semana: document.getElementById('actDia').value,
                horario_inicio: document.getElementById('actHorarioIni').value,
                horario_fin: document.getElementById('actHorarioFin').value
            };
            const res = await fetch('/api/actividades', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
            const result = await res.json();
            const msg = document.getElementById('msgNuevaAct');
            if (result.ok) {
                msg.innerHTML = '<span class="success">' + result.msg + '</span>';
                document.getElementById('formNuevaActividad').reset();
                cargarActividades();
            } else {
                msg.innerHTML = '<span class="error">' + result.msg + '</span>';
            }
        }

        async function editarActividad() {
            const id = parseInt(document.getElementById('edtActId').value);
            const data = {
                nombre: document.getElementById('edtActNombre').value,
                cupo: parseInt(document.getElementById('edtActCupo').value),
                estado: document.getElementById('edtActEstado').value,
                id_disciplina: document.getElementById('edtActDisc').value || null,
                id_espacio: document.getElementById('edtActEspacio').value || null,
                dia_semana: document.getElementById('edtActDia').value,
                horario_inicio: document.getElementById('edtActHorarioIni').value,
                horario_fin: document.getElementById('edtActHorarioFin').value
            };
            const res = await fetch(`/api/actividades/${id}`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
            const result = await res.json();
            const msg = document.getElementById('msgEditAct');
            if (result.ok) {
                msg.innerHTML = '<span class="success">' + result.msg + '</span>';
                cargarActividades();
            } else {
                msg.innerHTML = '<span class="error">' + result.msg + '</span>';
            }
        }

        async function borrarActividad(id) {
            if (!confirm('¿Seguro que deseas borrar esta actividad?')) return;
            const res = await fetch(`/api/actividades/${id}`, { method: 'DELETE' });
            const result = await res.json();
            if (result.ok) {
                alert('Actividad eliminada');
                cargarActividades();
            } else {
                alert('Error: ' + result.msg);
            }
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

        // --- Disciplinas functions ---
        async function cargarDisciplinas() {
            try {
                const res = await fetch('/api/disciplinas');
                if (!res.ok) {
                    const txt = await res.text();
                    document.getElementById('msgNuevaDisc').innerHTML = '<span class="error">Error cargando disciplinas: ' + txt + '</span>';
                    return;
                }
                const disciplinas = await res.json();
                const tbody = document.querySelector('#tabDisciplinas tbody');
                tbody.innerHTML = '';
                disciplinas.forEach(d => {
                    const safeName = (d.nombre || '').replace(/'/g, "\\\\'");
                    tbody.innerHTML += `
                    <tr>
                        <td>${d.id}</td>
                        <td>${d.nombre}</td>
                        <td>
                            <button onclick="cargarEditDisc(${d.id}, '${safeName}')">Editar</button>
                            <button class="danger" onclick="borrarDisciplina(${d.id})">Borrar</button>
                        </td>
                    </tr>`;
                });
            } catch (err) {
                document.getElementById('msgNuevaDisc').innerHTML = '<span class="error">' + err.message + '</span>';
            }
        }

        function cargarEditDisc(id, nombre) {
            document.getElementById('edtDiscId').value = id;
            document.getElementById('edtDiscNombre').value = nombre;
            document.querySelector('html').scrollTop = document.querySelector('#formEditarDisciplina').offsetTop;
        }

        async function crearDisciplina() {
            const data = { nombre: document.getElementById('discNombre').value };
            const res = await fetch('/api/disciplinas', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
            const result = await res.json();
            const msg = document.getElementById('msgNuevaDisc');
            if (result.ok) {
                msg.innerHTML = '<span class="success">' + result.msg + '</span>';
                document.getElementById('formNuevaDisciplina').reset();
                cargarDisciplinas();
            } else {
                msg.innerHTML = '<span class="error">' + result.msg + '</span>';
            }
        }

        async function editarDisciplina() {
            const id = parseInt(document.getElementById('edtDiscId').value);
            const data = { nombre: document.getElementById('edtDiscNombre').value };
            const res = await fetch(`/api/disciplinas/${id}`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
            const result = await res.json();
            const msg = document.getElementById('msgEditDisc');
            if (result.ok) {
                msg.innerHTML = '<span class="success">' + result.msg + '</span>';
                cargarDisciplinas();
            } else {
                msg.innerHTML = '<span class="error">' + result.msg + '</span>';
            }
        }

        async function borrarDisciplina(id) {
            if (!confirm('¿Seguro que deseas borrar esta disciplina?')) return;
            const res = await fetch(`/api/disciplinas/${id}`, { method: 'DELETE' });
            const result = await res.json();
            if (result.ok) {
                alert('Disciplina eliminada');
                cargarDisciplinas();
            } else {
                alert('Error: ' + result.msg);
            }
        }
    </script>
</body>
</html>'''


@app.route("/api/actividades")
def api_get_actividades():
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT a.id_actividad,
               a.nombre_actividad,
               a.cupo_maximo,
               a.estado,
               a.id_disciplina,
               d.nombre_disciplina,
               a.id_espacio,
               e.nombre_espacio,
               a.dia_semana,
               a.horario_inicio,
               a.horario_fin
        FROM ACTIVIDAD a
        LEFT JOIN DISCIPLINA d ON a.id_disciplina = d.id_disciplina
        LEFT JOIN ESPACIO_DEPORTIVO e ON a.id_espacio = e.id_espacio
    """)
    rows = cursor.fetchall()
    data = [{
        'id': r[0],
        'nombre': r[1],
        'cupo': r[2],
        'estado': r[3],
        'disciplina_id': r[4],
        'disciplina_nombre': r[5],
        'espacio_id': r[6],
        'espacio_nombre': r[7],
        'dia_semana': r[8],
        'horario_inicio': str(r[9]) if r[9] else '',
        'horario_fin': str(r[10]) if r[10] else ''
    } for r in rows]
    return jsonify(data)


@app.route('/api/actividades', methods=['POST'])
def api_create_actividad():
    data = request.json
    id_disc = data.get('id_disciplina')
    id_esp = data.get('id_espacio')
    
    # validar disciplina si se envía
    if id_disc is not None and id_disc != '':
        cur = cnx.cursor()
        cur.execute("SELECT 1 FROM DISCIPLINA WHERE id_disciplina=%s", (id_disc,))
        if cur.fetchone() is None:
            return jsonify({'ok': False, 'msg': 'Disciplina no existe'}), 400
    
    # validar espacio si se envía
    if id_esp is not None and id_esp != '':
        cur = cnx.cursor()
        cur.execute("SELECT 1 FROM ESPACIO_DEPORTIVO WHERE id_espacio=%s", (id_esp,))
        if cur.fetchone() is None:
            return jsonify({'ok': False, 'msg': 'Espacio no existe'}), 400
    
    try:
        cursor = cnx.cursor()
        cursor.execute(
            "INSERT INTO ACTIVIDAD (nombre_actividad, cupo_maximo, estado, id_disciplina, id_espacio, dia_semana, horario_inicio, horario_fin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (data.get('nombre'), data.get('cupo'), data.get('estado'), 
             id_disc if id_disc and id_disc != '' else None,
             id_esp if id_esp and id_esp != '' else None,
             data.get('dia_semana'),
             data.get('horario_inicio'),
             data.get('horario_fin'))
        )
        cnx.commit()
        return jsonify({'ok': True, 'msg': 'Actividad creada'}), 201
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 400


@app.route('/api/actividades/<int:aid>', methods=['PUT'])
def api_update_actividad(aid):
    data = request.json
    id_disc = data.get('id_disciplina')
    id_esp = data.get('id_espacio')
    
    if id_disc is not None and id_disc != '':
        cur = cnx.cursor()
        cur.execute("SELECT 1 FROM DISCIPLINA WHERE id_disciplina=%s", (id_disc,))
        if cur.fetchone() is None:
            return jsonify({'ok': False, 'msg': 'Disciplina no existe'}), 400
    
    if id_esp is not None and id_esp != '':
        cur = cnx.cursor()
        cur.execute("SELECT 1 FROM ESPACIO_DEPORTIVO WHERE id_espacio=%s", (id_esp,))
        if cur.fetchone() is None:
            return jsonify({'ok': False, 'msg': 'Espacio no existe'}), 400
    
    try:
        cursor = cnx.cursor()
        cursor.execute(
            "UPDATE ACTIVIDAD SET nombre_actividad=%s, cupo_maximo=%s, estado=%s, id_disciplina=%s, id_espacio=%s, dia_semana=%s, horario_inicio=%s, horario_fin=%s WHERE id_actividad=%s",
            (data.get('nombre'), data.get('cupo'), data.get('estado'), 
             id_disc if id_disc and id_disc != '' else None,
             id_esp if id_esp and id_esp != '' else None,
             data.get('dia_semana'),
             data.get('horario_inicio'),
             data.get('horario_fin'),
             aid)
        )
        cnx.commit()
        return jsonify({'ok': True, 'msg': 'Actividad actualizada'})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 400


@app.route('/api/actividades/<int:aid>', methods=['DELETE'])
def api_delete_actividad(aid):
    try:
        cursor = cnx.cursor()
        cursor.execute("DELETE FROM ACTIVIDAD WHERE id_actividad=%s", (aid,))
        cnx.commit()
        return jsonify({'ok': True, 'msg': 'Actividad eliminada'})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 400


@app.route("/api/disciplinas", methods=["GET"])
def api_get_disciplinas():
    cursor = cnx.cursor()
    cursor.execute("SELECT id_disciplina, nombre_disciplina FROM DISCIPLINA")
    rows = cursor.fetchall()
    data = [{'id': r[0], 'nombre': r[1]} for r in rows]
    return jsonify(data)

@app.route("/api/espacios", methods=["GET"])
def api_get_espacios():
    cursor = cnx.cursor()
    cursor.execute("SELECT id_espacio, nombre_espacio FROM ESPACIO_DEPORTIVO")
    rows = cursor.fetchall()
    data = [{'id': r[0], 'nombre': r[1]} for r in rows]
    return jsonify(data)

@app.route("/api/disciplinas", methods=["POST"])
def api_create_disciplina():
    data = request.json
    try:
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO DISCIPLINA (nombre_disciplina) VALUES (%s)", (data.get('nombre'),))
        cnx.commit()
        return jsonify({'ok': True, 'msg': 'Disciplina creada'}), 201
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 400


@app.route("/api/disciplinas/<int:did>", methods=["PUT"])
def api_update_disciplina(did):
    data = request.json
    try:
        cursor = cnx.cursor()
        cursor.execute("UPDATE DISCIPLINA SET nombre_disciplina=%s WHERE id_disciplina=%s", (data.get('nombre'), did))
        cnx.commit()
        return jsonify({'ok': True, 'msg': 'Disciplina actualizada'})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 400


@app.route("/api/disciplinas/<int:did>", methods=["DELETE"])
def api_delete_disciplina(did):
    try:
        cursor = cnx.cursor()
        cursor.execute("DELETE FROM DISCIPLINA WHERE id_disciplina=%s", (did,))
        cnx.commit()
        return jsonify({'ok': True, 'msg': 'Disciplina eliminada'})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 400


if __name__ == "__main__":
    app.run(debug=False, port=5000)
