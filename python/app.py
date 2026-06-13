import datetime
import os
from datetime import datetime
import mysql.connector
from werkzeug.security import check_password_hash

DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')

HASHED_PASSWORDS = {
    'administrador': 'scrypt:32768:8:1$FejuFIN6rwgvuGgb$53d0ce1163b317887fbe7ba7f4e3947494128a85862719f8aa61120e9dd8627fbd4ccf2c785f576a2f5ef5c8188fae1541988f22ad295dab29c24bca6a2a25a1',
    'profesor':      'scrypt:32768:8:1$ybaTnl9FBcZRpdf6$afd6fda270f7f4773acdef0240a5e4fcaa73ab0197db2fb7b8bf6b964e990d223e7bae24ee55a0ad0968411f501ba506d3713348b1fcde0c3676f2c548484aad',
    'estudiante':    'scrypt:32768:8:1$nqY3bTGyBZmf6Ve9$407b2d6e284168d3041777a22f1c9cdf777591d34643eff66b2728b8ebea8d2b2785e6c2456d92dea7c6d3baec5b02b10e12e6dc8545abaa6ebf8b218a97b280',
}

def input_no_vacio(prompt):
    while True:
        valor = input(prompt).strip()
        if valor:
            return valor
        print('El campo no puede estar vacío.')

def ElegirUsuario():
    while True:
        try:
            rol = input('Ingrese su rol (administrador, estudiante, profesor): ').strip().lower()
        except EOFError:
            print('\nError: no se detectó una terminal interactiva.')
            print('Ejecutá el programa con: docker compose run --rm app')
            raise
        if rol not in HASHED_PASSWORDS:
            print('Rol no válido. Debe ser administrador, estudiante o profesor.')
            continue
        try:
            password = input('Ingrese su contraseña: ')
        except EOFError:
            raise
        if not check_password_hash(HASHED_PASSWORDS[rol], password):
            print('Contraseña incorrecta.')
            continue
        try:
            cnx = mysql.connector.connect(
                user=rol,
                password=password,
                host=DB_HOST,
                charset='utf8mb4',
                database='gestion_deportes_universidad'
            )
            cursor = cnx.cursor()
            print(f'Conectado como {rol}.\n')
            return cnx, cursor, rol
        except mysql.connector.Error as e:
            print(f'Error de conexión: {e}')
            return None, None, None


def inscirpcion_estudiante(cnx, id_estudiante, id_actividad):
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(("""SELECT cupo_maximo, estado FROM ACTIVIDAD
                   WHERE id_actividad = %s"""), (id_actividad,))
    actividad = cursor.fetchone()

    if actividad is None or actividad['estado'] != 'abierta':
        print('Error: la actividad no existe o no está abierta.')
        return
    else:
        cursor.execute(("""SELECT * FROM INSCRIPCION
                       WHERE id_estudiante = %s AND id_actividad = %s AND estado_inscripcion NOT IN ('cancelada')"""), (id_estudiante, id_actividad))
        duplicado = cursor.fetchone()
        if duplicado is None:
            cursor.execute("""SELECT COUNT(*) as cupo_actual FROM INSCRIPCION
            WHERE id_actividad = %s AND estado_inscripcion = 'inscripto'
            """, (id_actividad,))
            resultado = cursor.fetchone()
            cupo_actual = resultado['cupo_actual']
            if cupo_actual < actividad['cupo_maximo']:
                estado_inscripcion = 'inscripto'
                print('INSCRIPCION POSIBLE')
            else:
                estado_inscripcion = 'lista_espera'
                print('LISTA DE ESPERA')

            sql = """INSERT INTO INSCRIPCION (id_estudiante, id_actividad, fecha_inscripcion, estado_inscripcion)
                        VALUES (%s, %s, CURDATE(), %s)"""
            valores = (id_estudiante, id_actividad, estado_inscripcion)
            cursor.execute(sql, valores)
            cnx.commit()
            print('Inscripcion realizada correctamente')
        else:
            print('Ya existe una inscripción activa para ese estudiante en esa actividad.')
            return


def actividadMaxInscriptos(cnx):
    cursor = cnx.cursor()
    cursor.execute("""SELECT a.id_actividad, a.nombre_actividad, COUNT(*) as cantidadInscriptos FROM ACTIVIDAD a
                   JOIN INSCRIPCION i on i.id_actividad = a.id_actividad
                   GROUP BY a.id_actividad, a.nombre_actividad
                   ORDER BY cantidadInscriptos desc
                   LIMIT 1;""")
    actividad = cursor.fetchone()
    print('La actividad con mayor inscripciones es: %s\n con %s inscriptos' % (actividad[1], actividad[2]))


def actividadesCuposDisponibles(cnx):
    cursor = cnx.cursor()
    cursor.execute("""SELECT a.id_actividad, a.nombre_actividad, COUNT(*) as cantidadInscriptos
                   FROM ACTIVIDAD a
                   LEFT JOIN INSCRIPCION i on i.id_actividad = a.id_actividad
                   GROUP BY a.id_actividad, a.nombre_actividad, a.cupo_maximo
                   HAVING a.cupo_maximo > COUNT(*);""")
    actividades = cursor.fetchall()
    print('Actividades disponibles:\n')
    for actividad in actividades:
        print(f'Actividad: {actividad[1]}.  ID: {actividad[0]}\n')


def cantInscriptosDisciplina(cnx):
    cursor = cnx.cursor()
    cursor.execute("""SELECT d.nombre_disciplina, COUNT(*) FROM DISCIPLINA d
                   LEFT JOIN ACTIVIDAD a on d.id_disciplina = a.id_disciplina
                   LEFT JOIN INSCRIPCION i on a.id_actividad = i.id_actividad
                   GROUP BY d.nombre_disciplina""")
    disciplinas = cursor.fetchall()
    for disciplina in disciplinas:
        print(f'Disciplina: {disciplina[0]}, Cantidad inscriptos: {disciplina[1]}')


def cantInscriptosFacultad(cnx):
    cursor = cnx.cursor()
    cursor.execute("""SELECT e.facultad, COUNT(*) as cantInscriptos FROM ESTUDIANTE e
                   JOIN INSCRIPCION i on e.id_estudiante = i.id_estudiante
                   GROUP BY e.facultad;""")
    facultades = cursor.fetchall()
    for facultad in facultades:
        print(f'Facultad: {facultad[0]}, cantidad inscriptos: {facultad[1]}')


def porcentajeOcupacionActividad(cnx):
    cursor = cnx.cursor()
    id_actividad = int(input('ID de la actividad: '))
    cursor.execute("""SELECT a.id_actividad, a.cupo_maximo, COUNT(*) FROM ACTIVIDAD a
                   JOIN INSCRIPCION i on a.id_actividad = i.id_actividad
                   WHERE a.id_actividad = %s AND i.estado_inscripcion = 'inscripto'
                   GROUP BY a.id_actividad, a.cupo_maximo""", (id_actividad,))
    actividad = cursor.fetchone()
    if actividad is None:
        print('Ocupada al 0%')
        return None
    porcentaje = (actividad[2] / actividad[1]) * 100
    return porcentaje


def porcentajeAsistenciaActividad(cnx):
    cursor = cnx.cursor()
    id_actividad = int(input('ID actividad: '))
    cursor.execute("""SELECT id_actividad, COUNT(*) FROM ASISTENCIA
                   WHERE id_actividad = %s AND asistio = True""", (id_actividad,))
    asistio = cursor.fetchone()
    asistencias = asistio[1]

    cursor.execute("""SELECT id_actividad, COUNT(*) FROM ASISTENCIA
                   WHERE id_actividad = %s""", (id_actividad,))
    total = cursor.fetchone()
    clasesTotales = total[1]
    if clasesTotales == 0:
        print('No hubo clases de esa actividad')
        return
    if total is None or asistio is None:
        print('Nadie asistio a esa actividad')
        return
    porcentaje = (asistencias / clasesTotales) * 100
    print(f'Porcentaje de asistencias es: {porcentaje}%')


def estudiantesConInasistencias(cnx):
    cursor = cnx.cursor()
    cursor.execute("""SELECT e.nombre, e.documento, COUNT(*) as inasistencias FROM ASISTENCIA a
                   JOIN ESTUDIANTE e on e.id_estudiante = a.id_estudiante
                   WHERE asistio = FALSE
                   GROUP BY e.nombre, e.documento
                   HAVING inasistencias > 2""")
    estudiantes = cursor.fetchall()
    if not estudiantes:
        print('No hay estudiantes con 3 o mas inasistencias')
        return
    for estudiante in estudiantes:
        print(f'Nombre: {estudiante[0]}, Documento: {estudiante[1]}')


def actividadesListaEspera(cnx):
    cursor = cnx.cursor()
    cursor.execute("""SELECT a.nombre_actividad FROM ACTIVIDAD a
                   JOIN INSCRIPCION i on i.id_actividad = a.id_actividad
                   WHERE i.estado_inscripcion = 'lista_espera'
                   group by a.nombre_actividad""")
    actividades = cursor.fetchall()
    if not actividades:
        print('No hay actividades con lista de espera')
        return
    print('Las actividades con lista de espera son:')
    for actividad in actividades:
        print(f'Nombre: {actividad[0]}')


def estudiantesNoInscriptos(cnx):
    cursor = cnx.cursor()
    cursor.execute("""SELECT e.nombre, e.documento FROM ESTUDIANTE e
                   LEFT JOIN INSCRIPCION i on e.id_estudiante = i.id_estudiante
                   WHERE i.id_estudiante IS NULL""")
    estudiantes = cursor.fetchall()
    if not estudiantes:
        print('No hay estudiantes sin inscripciones')
        return
    print('Los estudiantes sin inscripciones son:')
    for estudiante in estudiantes:
        print(f'Nombre: {estudiante[0]}, Documento: {estudiante[1]}')


def actividadConMasAusencias(cnx):
    cursor = cnx.cursor()
    cursor.execute("""SELECT a.nombre_actividad,a.cupo_maximo, COUNT(*) as ausencias FROM ACTIVIDAD a
                   JOIN ASISTENCIA asi on asi.id_actividad = a.id_actividad
                   WHERE asi.asistio = FALSE
                   GROUP BY a.nombre_actividad, a.cupo_maximo
                   ORDER BY ausencias DESC
                   LIMIT 1""")
    actividad = cursor.fetchone()
    if actividad is None:
        print('No hay actividades con ausencias')
        return
    print(f'La actividad con mas ausencias es: {actividad[0]} con {((actividad[2]/actividad[1]) * 100):.2f} ausencias')


def registrarAsistencia(cnx):
    cursor = cnx.cursor()
    while True:
        try :
            id_estudiante = int(input('ID estudiante: '))
            cursor.execute('SELECT * FROM ESTUDIANTE WHERE id_estudiante = %s', (id_estudiante,))
            if cursor.fetchone() is not None:
                break
        except ValueError:
            print('No existe un estudiante con ese ID o el formato no es correcto, intente nuevamente')

    while True:
        try :
            id_actividad = int(input('ID actividad: '))
            cursor.execute('SELECT * FROM ACTIVIDAD WHERE id_actividad = %s', (id_actividad,))
            if cursor.fetchone() is not None:
                break
        except ValueError:
            print('No existe una actividad con ese ID o el formato no es correcto, intente nuevamente')

    cursor.execute("""
        SELECT *
        FROM INSCRIPCION
        WHERE id_estudiante = %s
          AND id_actividad = %s
          AND estado_inscripcion = 'inscripto'
    """, (id_estudiante, id_actividad))
    inscripcion = cursor.fetchone()
    if inscripcion is None:
        print('Error: el estudiante no tiene una inscripción confirmada en esta actividad.')
        return
    
    while True:
        try :
            fecha = input('Fecha (AAAA-MM-DD): ')
            datetime.strptime(fecha, '%Y-%m-%d')
            break
        except ValueError:
            print('Formato de fecha incorrecto. Use AAAA-MM-DD.')
    asistio = input('¿Asistió? (s/n): ').lower() == 's'
    

    cursor.execute("""
        INSERT INTO ASISTENCIA
        (id_actividad, fecha, asistio, id_estudiante)
        VALUES (%s, %s, %s, %s)
    """, (id_actividad, fecha, asistio, id_estudiante))
    cnx.commit()
    print('Asistencia registrada correctamente.')


def menu_consultas(cnx):
    numeroConsulta = int(input(
        'Número de consulta:\n'
        ' 1  Actividad con max inscriptos\n'
        ' 2  Actividades con cupos disponibles\n'
        ' 3  Cantidad inscriptos por disciplina\n'
        ' 4  Cantidad inscriptos por facultad\n'
        ' 5  Porcentaje ocupación por actividad\n'
        ' 6  Porcentaje de asistencia por actividad\n'
        ' 7  Estudiantes con 3 o mas inasistencias\n'
        ' 8  Actividades con lista de espera\n'
        ' 9  Estudiantes no inscriptos en ninguna actividad\n'
        ' 10 Actividad con mas porcentaje de ausencias\n'
    ))
    if numeroConsulta == 1:
        actividadMaxInscriptos(cnx)
    elif numeroConsulta == 2:
        actividadesCuposDisponibles(cnx)
    elif numeroConsulta == 3:
        cantInscriptosDisciplina(cnx)
    elif numeroConsulta == 4:
        cantInscriptosFacultad(cnx)
    elif numeroConsulta == 5:
        porciento = porcentajeOcupacionActividad(cnx)
        if porciento is not None:
            print(f'Ocupada al: {porciento}%')
    elif numeroConsulta == 6:
        porcentajeAsistenciaActividad(cnx)
    elif numeroConsulta == 7:
        estudiantesConInasistencias(cnx)
    elif numeroConsulta == 8:
        actividadesListaEspera(cnx)
    elif numeroConsulta == 9:
        estudiantesNoInscriptos(cnx)
    elif numeroConsulta == 10:
        actividadConMasAusencias(cnx)
    else : 
        print('Número de consulta no válido')





def menu_administrador(cnx, cursor):
    while True:
        try :
            print('Seleccione una accion:\n 1 ABM estudiantes\n 2 ABM disciplinas\n 3 ABM Espacios Deportivos\n 4 ABM actividades\n 5 Inscripciones\n 6 Registro de asistencias\n 7 Consultas')
            opt = int(input())
            break
        except ValueError:
            print('Opcion no valida, debe ser un numero entero')

    if opt == 1:
        while True :
            try :
                print('1: Insertar, 2: Editar, 3: Eliminar')
                InsEdEl = int(input())
                break
            except ValueError:  
                print('Opcion no valida, debe ser un numero entero')

        if InsEdEl == 1:
            while True:
                try:
                    documento = int(input('Documento: '))
                    nombre = input_no_vacio('Nombre: ')
                    apellido = input_no_vacio('Apellido: ')
                    email = input_no_vacio('Email: ')
                    carrera = input_no_vacio('Carrera: ')
                    facultad = input_no_vacio('Facultad: ')
                    break
                except ValueError:
                    print('Alguno de los formatos no es correcto, intentelo de vuelta')

            sql = """INSERT INTO ESTUDIANTE (documento, nombre, apellido, email, carrera, facultad)
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            valores = (documento, nombre, apellido, email, carrera, facultad)
            cursor.execute(sql, valores)
            cnx.commit()
            print('Estudiante agregado correctamente.')

        elif InsEdEl == 2:
            cursor.execute('SELECT * FROM ESTUDIANTE')
            estudiantes = cursor.fetchall()
            print('\n=== ESTUDIANTES ===')
            for estudiante in estudiantes:
                print(f'ID: {estudiante[0]} | Nombre: {estudiante[1]} {estudiante[2]} | Documento: {estudiante[3]}')
            while True:
                try:
                    id_estudiante = int(input('ID del estudiante: '))
                    break
                except ValueError:
                    print('ID debe ser un numero entero')

            cursor.execute('SELECT * FROM ESTUDIANTE WHERE id_estudiante = %s', (id_estudiante,))
            estudiante = cursor.fetchone()
            if estudiante is None:
                print('No existe un estudiante con ese ID')
            else:
                while True:
                    try:
                        documento = int(input('Documento: '))
                        nombre = input_no_vacio('Nombre: ')
                        apellido = input_no_vacio('Apellido: ')
                        email = input_no_vacio('Email: ')
                        carrera = input_no_vacio('Carrera: ')
                        facultad = input_no_vacio('Facultad: ')
                        break
                    except ValueError:
                        print('Alguna de las entradas no es del formato correcto, intente nuevamente')

                sql = """UPDATE ESTUDIANTE
                         SET documento = %s, nombre = %s, apellido = %s, email = %s, carrera = %s, facultad = %s
                         WHERE id_estudiante = %s"""
                cursor.execute(sql, (documento, nombre, apellido, email, carrera, facultad, id_estudiante))
                cnx.commit()

        elif InsEdEl == 3:
            cursor.execute('SELECT * FROM ESTUDIANTE')
            estudiantes = cursor.fetchall()
            print('\n=== ESTUDIANTES ===')
            for estudiante in estudiantes:
                print(f'ID: {estudiante[0]} | Nombre: {estudiante[1]} {estudiante[2]} | Documento: {estudiante[3]}')
            while True:
                try:
                    id_estudiante = int(input('ID del estudiante a eliminar: '))
                    break
                except ValueError:
                    print('ID debe ser un numero entero')
            cursor.execute('DELETE FROM ESTUDIANTE WHERE id_estudiante = %s', (id_estudiante,))
            cnx.commit()
        else : 
            print('no se ingreso una opcion valida, vuelva a intentarlo')
    elif opt == 2:
        while True:
            try:
                print('1: Insertar, 2: Editar, 3: Eliminar')
                accion = int(input())
                break
            except ValueError:
                print('Opcion no valida, debe ser un numero entero')
        if accion == 1:
            NombreDisciplina = input_no_vacio('Nombre de Disciplina: ')
            sql = """INSERT INTO DISCIPLINA (nombre_disciplina) VALUES (%s)"""
            cursor.execute(sql, (NombreDisciplina,))
            cnx.commit()

        elif accion == 2:
            cursor.execute('SELECT * FROM DISCIPLINA')
            disciplinas = cursor.fetchall()
            print('\n=== DISCIPLINAS ===')
            for disciplina in disciplinas:
                print(f'ID: {disciplina[0]} | Nombre: {disciplina[1]}')
            while True:
                try:
                    id_disciplina = int(input('ID de la disciplina a editar: '))
                    nombreDisciplina = input_no_vacio('Nombre nuevo: ')
                    break
                except ValueError:
                    print('ID debe ser un numero entero')
            sql = """UPDATE DISCIPLINA SET nombre_disciplina = %s WHERE id_disciplina = %s"""
            cursor.execute(sql, (nombreDisciplina, id_disciplina))
            cnx.commit()

        elif accion == 3:
            cursor.execute('SELECT * FROM DISCIPLINA')
            disciplinas = cursor.fetchall()
            print('\n=== DISCIPLINAS ===')
            for disciplina in disciplinas:
                print(f'ID: {disciplina[0]} | Nombre: {disciplina[1]}')
            while True:
                try:
                    id_disciplina = int(input('ID de la disciplina a eliminar: '))
                    break
                except ValueError:
                    print('ID debe ser un numero entero')
            cursor.execute('DELETE FROM DISCIPLINA WHERE id_disciplina = %s', (id_disciplina,))
            cnx.commit()
        else :
            print('no se ingreso una opcion valida, vuelva a intentarlo')
    elif opt == 3:
        accion = int(input('1: Insertar, 2: Editar, 3: Eliminar\n'))
        if accion == 1:
            while True:
                try:
                    nombre_espacio = input_no_vacio('Nombre: ')
                    ubicacion = input_no_vacio('Ubicacion: ')
                    capacidad = int(input('Capacidad: '))
                    break
                except ValueError:
                    print('Alguno de los formatos no es correcto, intentelo de vuelta')
            sql = """INSERT INTO ESPACIO_DEPORTIVO (nombre_espacio, ubicacion, capacidad) VALUES (%s, %s, %s)"""
            cursor.execute(sql, (nombre_espacio, ubicacion, capacidad))
            cnx.commit()

        elif accion == 2:
            cursor.execute('SELECT * FROM ESPACIO_DEPORTIVO')
            espacios = cursor.fetchall()
            print('\n=== ESPACIOS DEPORTIVOS ===')
            for espacio in espacios:
                print(f'ID: {espacio[0]} | Nombre: {espacio[1]} | Ubicacion: {espacio[2]} | Capacidad: {espacio[3]}')
            while True:
                try:
                    editarID = int(input('ID a cambiar: '))
                    newNombre_espacio = input_no_vacio('Nuevo nombre: ')
                    newUbicacion = input_no_vacio('Nueva ubicacion: ')
                    newCapacidad = int(input('Nueva capacidad: '))
                    break
                except ValueError:
                    print('ID y capacidad deben ser numeros enteros')
            sql = """UPDATE ESPACIO_DEPORTIVO SET nombre_espacio = %s, ubicacion = %s, capacidad = %s WHERE id_espacio = %s"""
            cursor.execute(sql, (newNombre_espacio, newUbicacion, newCapacidad, editarID))
            cnx.commit()

        elif accion == 3:
            cursor.execute('SELECT * FROM ESPACIO_DEPORTIVO')
            espacios = cursor.fetchall()
            print('\n=== ESPACIOS DEPORTIVOS ===')
            for espacio in espacios:
                print(f'ID: {espacio[0]} | Nombre: {espacio[1]} | Ubicacion: {espacio[2]} | Capacidad: {espacio[3]}')
            while True:
                try:
                    eliminarID = int(input('ID a eliminar: '))
                    break
                except ValueError:
                    print('ID debe ser un numero entero')
            cursor.execute('DELETE FROM ESPACIO_DEPORTIVO WHERE id_espacio = %s', (eliminarID,))
            cnx.commit()

    elif opt == 4:
        while True :
            try :
                accion = int(input('Seleccione una accion: 1 Insertar, 2 Editar, 3 Eliminar\n'))
                break
            except ValueError:
                print('Opcion no valida, debe ser un numero entero')

        if accion == 1:
            nombre_actividad = input_no_vacio('Nombre actividad: ')
            while True:
                try:
                    id_espacio = int(input('Id espacio: '))
                    break
                except ValueError:
                    print('ID debe ser un numero entero')
            cursor.execute('SELECT * FROM ESPACIO_DEPORTIVO WHERE id_espacio = %s', (id_espacio,))
            if cursor.fetchone() is None:
                print('No existe un espacio con ese ID')
                return

            while True:
                try:
                    id_disciplina = int(input('Id disciplina: '))
                    break
                except ValueError:
                    print('ID debe ser un numero entero')
            cursor.execute('SELECT * FROM DISCIPLINA WHERE id_disciplina = %s', (id_disciplina,))
            if cursor.fetchone() is None:
                print('No existe una disciplina con ese ID')
                return

            while True:
                try:
                    cupo = int(input('Cupo Maximo: '))
                    diaSemana = input_no_vacio('Dia de semana: ')
                    break
                except ValueError:
                    print('Alguno de los formatos no es correcto, intentelo de vuelta')

            horario_inicio = None
            while True:
                entrada = input('Hora de inicio (HH:MM:SS): ')
                try:
                    horario_inicio = datetime.strptime(entrada, '%H:%M:%S').time()
                    break
                except ValueError:
                    print('Formato incorrecto. Usa HH:MM:SS.')

            horario_final = None
            while True:
                entrada = input('Hora final (HH:MM:SS): ')
                try:
                    horario_final = datetime.strptime(entrada, '%H:%M:%S').time()
                    break
                except ValueError:
                    print('Formato incorrecto. Usa HH:MM:SS.')

            while True:
                estado = input('Estado (abierta/cerrada/finalizada/cancelada): ')
                if estado not in ('abierta', 'cerrada', 'finalizada', 'cancelada'):
                    print('Estado inválido. Debe ser: abierta, cerrada, finalizada o cancelada')
                else:
                    break

            sql = """INSERT INTO ACTIVIDAD
                     (nombre_actividad, id_espacio, id_disciplina, cupo_maximo, dia_semana, horario_inicio, horario_fin, estado)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (nombre_actividad, id_espacio, id_disciplina, cupo, diaSemana, horario_inicio, horario_final, estado))
            cnx.commit()

        elif accion == 2:
            cursor.execute('SELECT * FROM ACTIVIDAD')
            actividades = cursor.fetchall()
            print('\n=== ACTIVIDADES ===')
            for actividad in actividades:
                print(f'ID: {actividad[0]} | Nombre: {actividad[1]} | Espacio: {actividad[2]} | Disciplina: {actividad[3]} | Cupo: {actividad[4]} | Dia: {actividad[5]} | Inicio: {actividad[6]} | Fin: {actividad[7]} | Estado: {actividad[8]}')
            editarID = int(input('ID de la actividad a modificar: '))
            cursor.execute('SELECT * FROM ACTIVIDAD WHERE id_actividad = %s', (editarID,))
            if cursor.fetchone() is None:
                print('No existe una actividad con ese ID')
                return

            nombreActividad = input_no_vacio('Nombre Actividad: ')
            id_espacio = int(input('Id espacio: '))
            cursor.execute('SELECT * FROM ESPACIO_DEPORTIVO WHERE id_espacio = %s', (id_espacio,))
            if cursor.fetchone() is None:
                print('No existe un espacio con ese ID')
                return

            id_disciplina = int(input('Id disciplina: '))
            cursor.execute('SELECT * FROM DISCIPLINA WHERE id_disciplina = %s', (id_disciplina,))
            if cursor.fetchone() is None:
                print('No existe una disciplina con ese ID')
                return

            cupo = int(input('Cupo Maximo: '))
            diaSemana = input_no_vacio('Dia de semana: ')

            horario_inicio = None
            while True:
                entrada = input('Hora de inicio (HH:MM:SS): ')
                try:
                    horario_inicio = datetime.strptime(entrada, '%H:%M:%S').time()
                    break
                except ValueError:
                    print('Formato incorrecto. Usa HH:MM:SS.')

            horario_final = None
            while True:
                entrada = input('Hora final (HH:MM:SS): ')
                try:
                    horario_final = datetime.strptime(entrada, '%H:%M:%S').time()
                    break
                except ValueError:
                    print('Formato incorrecto. Usa HH:MM:SS.')

            while True:
                estado = input_no_vacio('Estado (abierta/cerrada/finalizada/cancelada): ')
                if estado not in ('abierta', 'cerrada', 'finalizada', 'cancelada'):
                    print('Estado inválido. Debe ser: abierta, cerrada, finalizada o cancelada')
                else:
                    break

            sql = """UPDATE ACTIVIDAD
                     SET nombre_actividad = %s, id_espacio = %s, id_disciplina = %s, cupo_maximo = %s,
                         dia_semana = %s, horario_inicio = %s, horario_fin = %s, estado = %s
                     WHERE id_actividad = %s"""
            cursor.execute(sql, (nombreActividad, id_espacio, id_disciplina, cupo, diaSemana, horario_inicio, horario_final, estado, editarID))
            cnx.commit()

        elif accion == 3:
            cursor.execute('SELECT * FROM ACTIVIDAD')
            actividades = cursor.fetchall()
            print('\n=== ACTIVIDADES ===')
            for actividad in actividades:
                print(f'ID: {actividad[0]} | Nombre: {actividad[1]} | Estado: {actividad[8]}')
            borrarID = int(input('ID a borrar: '))
            cursor.execute('SELECT * FROM ACTIVIDAD WHERE id_actividad = %s', (borrarID,))
            if cursor.fetchone() is None:
                print('No existe una actividad con ese ID')
                return
            cursor.execute('DELETE FROM ACTIVIDAD WHERE id_actividad = %s', (borrarID,))
            cnx.commit()

        else :
            print('no se ingreso una opcion valida, vuelva a intentarlo')
    elif opt == 5:
        while True:
            try:
                id_actividad = int(input('ID actividad: '))
                break
            except ValueError:
                print('ID inválido. Debe ser un número entero.')
        cursor.execute('SELECT * FROM ACTIVIDAD WHERE id_actividad = %s', (id_actividad,))
        if cursor.fetchone() is None:
            print('No existe una actividad con ese ID')
            return
        while True:
            try:
                id_estudiante = int(input('ID del estudiante: '))
                break
            except ValueError:
                print('ID inválido. Debe ser un número entero.')
        cursor.execute('SELECT * FROM ESTUDIANTE WHERE id_estudiante = %s', (id_estudiante,))
        if cursor.fetchone() is None:
            print('No existe un estudiante con ese ID')
            return
        inscirpcion_estudiante(cnx, id_estudiante, id_actividad)

    elif opt == 6:
        registrarAsistencia(cnx)

    elif opt == 7:
        menu_consultas(cnx)
    else :
        print('Opción no válida')


def menu_profesor(cnx):
    print('Seleccione una accion:\n 1 Registrar asistencia\n 2 Consultas')
    opt = int(input())
    if opt == 1:
        registrarAsistencia(cnx)
    elif opt == 2:
        menu_consultas(cnx)
    else:
        print('Opción no válida')


def menu_estudiante(cnx):
    print('Seleccione una accion:\n 1 Inscribirse en una actividad\n 2 Ver actividades con cupos disponibles')
    while True:
        try:
            opt = int(input())
            break
        except ValueError:
            print('Opción inválida. Debe ser un número entero.')
    if opt == 1:
        actividadesCuposDisponibles(cnx)
        while True:
            try:
                id_actividad = int(input('ID actividad: '))
                break
            except ValueError:
                print('ID inválido. Debe ser un número entero.')
        while True:
            try:
                documento = int(input('Documento del estudiante: '))
                break
            except ValueError:
                print('Documento inválido. Debe ser un número entero.')
        cursor = cnx.cursor()
        cursor.execute('SELECT id_estudiante FROM ESTUDIANTE WHERE documento = %s', (documento,))
        resultado = cursor.fetchone()
        if resultado is None:
            print('No existe un estudiante con ese documento')
            return
        id_estudiante = resultado[0]
        inscirpcion_estudiante(cnx, id_estudiante, id_actividad)
    elif opt == 2:
        actividadesCuposDisponibles(cnx)
    else:
        print('Opción no válida')


# --- INICIO ---
try:
    print('Bienvenido al sistema de gestión de deportes universitarios\n Eliga un usuario para comenzar (administrador, estudiante, profesor):')
    while True:
        cnx, cursor, rol = ElegirUsuario()
        if cnx is not None:
            break
        print('No se pudo conectar. Intente nuevamente.')

    while True:
        if rol == 'administrador':
            menu_administrador(cnx, cursor)
        elif rol == 'profesor':
            menu_profesor(cnx)
        elif rol == 'estudiante':
            menu_estudiante(cnx)

        quiereContinuar = input('\n¿Desea realizar otra acción? (s/n): ').lower()
        if quiereContinuar != 's':
            print('Saliendo del sistema.')
            break

        quieresCambiarUsuario = input('¿Desea cambiar de usuario? (s/n): ').lower()
        if quieresCambiarUsuario == 's':
            cnx.close()
            while True:
                cnx, cursor, rol = ElegirUsuario()
                if cnx is not None:
                    break
                print('No se pudo conectar. Intente nuevamente.')
except EOFError:
    print('\nEntrada cerrada. Saliendo del sistema.')
