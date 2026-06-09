import datetime
from datetime import datetime
import mysql.connector
cnx = mysql.connector.connect(user='root', password='Locostib2005.', host='127.0.0.1', database='gestion_deportes_universidad')
cursor =cnx.cursor()

def inscirpcion_estudiante(cnx, id_estudiante, id_actividad) :
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(("""SELECT cupo_maximo, estado FROM ACTIVIDAD
                   WHERE id_actividad = %s"""), (id_actividad,))
    actividad = cursor.fetchone()


    if actividad is None or actividad['estado'] != 'abierta' : 
         print('error')
         return
    else : 
         cursor.execute(("""SELECT * FROM INSCRIPCION
                        WHERE id_estudiante = %s AND id_actividad = %s AND estado_inscripcion NOT IN ('cancelada')"""), (id_estudiante, id_actividad))
         duplicado = cursor.fetchone()
         if duplicado is None :
              
                cursor.execute("""SELECT COUNT(*) as cupo_actual FROM INSCRIPCION
                WHERE id_actividad = %s AND estado_inscripcion = 'inscripto'
                """, (id_actividad,))
                
                resultado = cursor.fetchone()
                cupo_actual = resultado['cupo_actual']
                if cupo_actual < actividad['cupo_maximo']:  

                     estado_inscripcion = 'inscripto'
                     print('INSCRIPCION POSIBLE')
                else : 
                     estado_inscripcion = 'lista_espera'
                     print('LISTA DE ESPERA')

                sql = """INSERT INTO INSCRIPCION (id_estudiante, id_actividad, fecha_inscripcion, estado_inscripcion)
                            VALUES (%s, %s, CURDATE(), %s)"""
                valores = (
                          id_estudiante,
                          id_actividad,
                          estado_inscripcion
                     )

                
                cursor.execute(sql, valores)
                cnx.commit()
                print('Inscripcion realizada correctamente')
         else : 
              print('esta duplicado')
              return
    return  
    

def actividadMaxInscriptos(cnx) :
     cursor = cnx.cursor()
     cursor.execute("""SELECT a.id_actividad, a.nombre_actividad, COUNT(*) as cantidadInscriptos FROM ACTIVIDAD a
                    JOIN INSCRIPCION i on i.id_actividad = a.id_actividad
                    GROUP BY a.id_actividad, a.nombre_actividad
                    ORDER BY cantidadInscriptos desc
                    LIMIT 1;""")
     actividad = cursor.fetchone()
     print('la actividad con mayor inscripciones es:  %s\n con %s inscriptos' % (actividad[1], actividad[2]))


def actividadesCuposDisponibles(cnx) :
    cursor = cnx.cursor()
    cursor.execute("""SELECT a.id_actividad, a.nombre_actividad, COUNT(*) as cantidadInscriptos
                   FROM ACTIVIDAD a
                   LEFT JOIN INSCRIPCION i on i.id_actividad = a.id_actividad
                   GROUP BY a.id_actividad, a.nombre_actividad, a.cupo_maximo
                   HAVING a.cupo_maximo > COUNT(*);""")
    actividades = cursor.fetchall()
    print('actividades disponibles\n')
    for actividad in actividades :
         print(f'Actividad : {actividad[1]}\n')

def cantInscriptosDisciplina(cnx) :
    cursor = cnx.cursor()
    cursor.execute("""SELECT d.nombre_disciplina, COUNT(*) FROM DISCIPLINA d
                   LEFT JOIN ACTIVIDAD a on d.id_disciplina = a.id_disciplina
                   LEFT JOIN INSCRIPCION i on a.id_actividad = i.id_actividad
                   GROUP BY d.nombre_disciplina""")
    
    disciplinas = cursor.fetchall()
    for disciplina in disciplinas :
         print(f'Disciplina : {disciplina[0]}, Cantidad inscriptos : {disciplina[1]}')
        
def cantInscriptosFacultad(cnx) :
    cursor = cnx.cursor()
    cursor.execute("""SELECT e.facultad, COUNT(*) as cantInscriptos FROM ESTUDIANTE e
                   JOIN INSCRIPCION i on e.id_estudiante = i.id_estudiante
                   GROUP BY e.facultad;""")
    
    facultades = cursor.fetchall()
    for facultad in facultades :
         print(f'Facultad : {facultad[0]}, cantidad inscriptos : {facultad[1]}')


def porcentajeOcupacionActividad(cnx) :
    cursor = cnx.cursor()
    id_actividad = int(input('ID de la actividad'))

    cursor.execute("""SELECT a.id_actividad, a.cupo_maximo, COUNT(*) FROM ACTIVIDAD a
                   JOIN INSCRIPCION i on a.id_actividad = i.id_actividad
                   WHERE a.id_actividad = %s AND i.estado_inscripcion = 'inscripto'
                   GROUP BY a.id_actividad, a.cupo_maximo""", (id_actividad,))
    
    actividad = cursor.fetchone()
    if actividad is None :
         print('ocupada al 0 %')
         return
    porcentaje = (actividad[2]/actividad[1]) * 100
    return porcentaje

def porcentajeAsistenciaActividad(cnx) :
    cursor = cnx.cursor()
    id_actividad = int(input('ID actividad\n'))
    cursor.execute("""SELECT id_actividad, COUNT(*) FROM ASISTENCIA
                   WHERE id_actividad = %s AND asistio = True""", (id_actividad,))
    asistio = cursor.fetchone()
    asistencias = asistio[1]

    cursor.execute("""SELECT id_actividad, COUNT(*) FROM ASISTENCIA
                   WHERE id_actividad = %s""", (id_actividad,))
    total = cursor.fetchone()
    clasesTotales = total[1]
    if clasesTotales == 0 :
         print('No hubo clases de esa actividad')
         exit()
    if total is None or asistio is None :
         print('nadie asistio a esa actividad')
         exit()
    porcentaje = (asistencias/clasesTotales) * 100
    print(f'Porcentaje de asistencias es : {porcentaje} %')
    return

def estudiantesConInasistencias(cnx) :
    cursor = cnx.cursor()

    cursor.execute("""SELECT e.nombre, e.documento, COUNT(*) as inasistencias FROM ASISTENCIA a
                   JOIN ESTUDIANTE e on e.id_estudiante = a.id_estudiante
                   WHERE asistio = FALSE
                   GROUP BY e.nombre, e.documento
                   HAVING inasistencias > 2""")
    
    estudiantes = cursor.fetchall()
    if estudiantes is None :
        print('No hay estudiantes con 3 o mas inasistencias')
        exit() 
    for estudiante in estudiantes :
         print(f'nombre : {estudiante[0]} documento : {estudiante[1]}')

print('Seleccione una accion :  ABM(1 estudiantes, 2 disciplinas, 3 Espacios Derpotivos, 4 actividades), 5 Inscripciones, 6 registro de asistencias, 7 consultas')
opt = int(input())
#ESTUDIANTES

if opt == 1 : #agregar
    print('1: insertar, 2 : editar, 3: eliminar')
    InsEdEl = int(input())
    if InsEdEl == 1 :
        documento = int(input("Documento: "))

        nombre = input("Nombre: ")

        apellido = input("Apellido: ")

        email = input("Email: ")

        carrera = input("Carrera: ")

        facultad = input("Facultad: ")

        sql = """INSERT INTO ESTUDIANTE

        (documento, nombre, apellido, email, carrera, facultad)

        VALUES (%s, %s, %s, %s, %s, %s)"""
    
        valores = (

        documento,

        nombre,

        apellido,

        email,

        carrera,

        facultad
        )

        cursor.execute(sql, valores)

        cnx.commit()

        print("Estudiante agregado correctamente.")
    elif InsEdEl == 2 : #editar
        cursor.execute("SELECT * FROM ESTUDIANTE")
        estudiantes = cursor.fetchall()
        #(44321098, 'Agustín', 'Silva', 'agustin.silva@fing.edu.uy', 'Ingeniería Mecánica', 'FING'),
        print("\n=== ESTUDIANTES ===")

        for estudiante in estudiantes:
                print(
                f"ID: {estudiante[0]} | "
                f"Nombre: {estudiante[1]} {estudiante[2]} | "
                f"Documento: {estudiante[3]}"
            )
        id_estudiante = int(input("ID del estudiante: "))
        cursor.execute("SELECT * FROM ESTUDIANTE WHERE id_estudiante = %s",(id_estudiante,))
        estudiante = cursor.fetchone()
        if estudiante is None :
            print('no existe un estudiante con ese ID')
        else :

            documento = int(input("Documento: "))
            nombre = input("Nombre: ")
            apellido = input("Apellido: ")
            email = input("Email: ")
            carrera = input("Carrera: ")
            facultad = input("Facultad: ")

            sql = """
            UPDATE ESTUDIANTE
            SET documento = %s,
                nombre = %s,
                apellido = %s,
                email = %s,
                carrera = %s,
                facultad = %s
            WHERE id_estudiante = %s
            """

            cursor.execute(sql, (
                documento,
                nombre,
                apellido,
                email,
                carrera,
                facultad,
                id_estudiante
            ))
            cnx.commit()
    elif InsEdEl == 3 :
        cursor.execute("SELECT * FROM ESTUDIANTE")
        estudiantes = cursor.fetchall()
        #(44321098, 'Agustín', 'Silva', 'agustin.silva@fing.edu.uy', 'Ingeniería Mecánica', 'FING'),
        print("\n=== ESTUDIANTES ===")

        for estudiante in estudiantes:
                print(
                f"ID: {estudiante[0]} | "
                f"Nombre: {estudiante[1]} {estudiante[2]} | "
                f"Documento: {estudiante[3]}"
            )
        id_estudiante = int(input("ID del estudiante a eliminar: "))
        cursor.execute("DELETE FROM ESTUDIANTE WHERE id_estudiante = %s", (id_estudiante,))
        cnx.commit()
elif opt == 2 : 
     accion = int(input('1: Insertar, 2: Editar, 3: Eliminar'))
    
     if accion == 1 :
            NombreDisciplina = input('Nombre de Disciplina :')
            sql = ("""INSERT INTO DISCIPLINA 
                         (nombre_disciplina)
                          VALUES (%s)""")
            valores = (NombreDisciplina,)
            cursor.execute(sql, valores)
            cnx.commit()
    
     elif accion == 2 : 
        cursor.execute("SELECT * FROM DISCIPLINA")
        disciplinas = cursor.fetchall()

        print("\n=== DISCIPLINAS ===")
        for disciplina in disciplinas:
                print(
                f"ID: {disciplina[0]} | "
                f"Nombre: {disciplina[1]} | "
            )
        
        nombreDisciplina = input('nombre nuevo : ')
        id_disciplina = int(input('ID de la disciplina a editar :'))
        sql = """UPDATE DISCIPLINA
                SET nombre_disciplina = %s
                WHERE id_disciplina = %s"""    
        valores = (nombreDisciplina, id_disciplina)   
        cursor.execute(sql, valores)
        cnx.commit()
   
     elif  accion == 3 :
        cursor.execute("SELECT * FROM DISCIPLINA")
        disciplinas = cursor.fetchall()
        print("\n=== DISCIPLINAS ===")
        for disciplina in disciplinas:
                print(
                f"ID: {disciplina[0]} | "
                f"Nombre: {disciplina[1]} | "
            )
        
        id_disciplina = int(input('ID a borrar:'))
        sql = """DELETE FROM DISCIPLINA WHERE id_disciplina = %s"""
        valores = (id_disciplina,)
        cursor.execute(sql, valores)
        cnx.commit()
        
elif opt == 3 :
     accion = int(input('1 : Insertar, 2: Editar, 3 : Eliminar'))
     if accion == 1 :
          sql = """INSERT INTO ESPACIO_DEPORTIVO 
          (nombre_espacio, ubicacion, capacidad)
          VALUES (%s, %s, %s)"""
          nombre_espacio = input('Nombre : ')
          ubicacion = input('Ubicacion : ')
          capacidad = int(input('Capacidad : '))
          valores = (
               nombre_espacio,
               ubicacion,
               capacidad
          )

          cursor.execute(sql, valores)
          cnx.commit()
     elif accion == 2 :
        cursor.execute("SELECT * FROM ESPACIO_DEPORTIVO")
        espacios = cursor.fetchall()
        print("\n=== ESPACIOS DEPORTIVOS ===")

        for espacio in espacios:
                print(
                f"ID: {espacio[0]} | "
                f"Nombre espacio: {espacio[1]}| "
                f"Ubicacion: {espacio[2]} |"
                f"Capacidad: {espacio[3]}"
            )
        editarID = input('ID a cambiar: ')
        newNombre_espacio = input('Nuevo nombre : ')
        newUbicacion = input('Nueva ubicacion : ')
        newCapacidad = int(input('Nueva capacidad : '))
       
        valores = (
             newNombre_espacio,
             newUbicacion,
             newCapacidad,
             editarID
        )
       
        sql = """UPDATE ESPACIO_DEPORTIVO 
        SET nombre_espacio = %s,
        ubicacion = %s,
        capacidad = %s
        WHERE id_espacio = %s"""
       
        cursor.execute(sql, valores)
        cnx.commit()

     elif accion == 3 :

        cursor.execute("SELECT * FROM ESPACIO_DEPORTIVO")
        espacios = cursor.fetchall()
        print("\n=== ESPACIOS DEPORTIVOS ===")

        for espacio in espacios:
                print(
                f"ID: {espacio[0]} | "
                f"Nombre espacio: {espacio[1]}| "
                f"Ubicacion: {espacio[2]} |"
                f"Capacidad: {espacio[3]}"
            )
                
        eliminarID = int(input('ID a eliminar : '))
        sql = """DELETE FROM ESPACIO_DEPORTIVO WHERE id_espacio = %s"""
        valores = (eliminarID,)
        cursor.execute(sql, valores)
        cnx.commit()
     else : 
          print('error')
elif opt == 4 :
     accion = int(input('1: Insertar, 2: Editar, 3: Eliminar'))
     if accion == 1 :
            nombre_actividad = input('Nombre actividad : ')
           
            id_espacio = int(input('Id espacio'))
            cursor.execute("SELECT * FROM ESPACIO_DEPORTIVO WHERE id_espacio = %s",(id_espacio,))
            espacio = cursor.fetchone()
            if espacio is None :
                print('no existe un espacio con ese ID')
                exit()


            id_disciplina = int(input('Id disciplina'))
            cursor.execute("SELECT * FROM DISCIPLINA WHERE id_disciplina = %s",(id_disciplina,))
            disciplina = cursor.fetchone()
            if disciplina is None :
                print('no existe una disciplina con ese ID')
                exit()
            
            
            
            cupo = int(input('Cupo Maximo'))
            diaSemana = input('Dia de semana')
            
            horario_inicio = None
            while True:
                 entrada = input("Ingresa la hora de inicio (HH:MM:SS): ")
                 try:
                     # Intenta la conversión
                     horario_inicio = datetime.strptime(entrada, "%H:%M:%S").time()
                     break  # Rompe el bucle si todo salió bien
                 except ValueError:
                     # Se ejecuta si el formato ingresado es incorrecto
                     print("Formato incorrecto. Usa HH:MM:SS.")
            
            horario_final = None
            while True:
                 entrada = input("Ingresa la hora final (HH:MM:SS): ")
                 try:
                     # Intenta la conversión
                     horario_final = datetime.strptime(entrada, "%H:%M:%S").time()
                     break  # Rompe el bucle si todo salió bien
                 except ValueError:
                     # Se ejecuta si el formato ingresado es incorrecto
                     print("Formato incorrecto. Usa HH:MM:SS.")
            
            estado = input('Estado :')
            if estado != 'abierta' and estado != 'cerrada' and estado != 'finalizada' and estado != 'cancelada' :
                 print("NO EXISTE ESE ESTADO")
                 exit()
            else : 
                 sql = """INSERT INTO ACTIVIDAD
                 (nombre_actividad, id_espacio, id_disciplina, cupo_maximo, dia_semana, horario_inicio, horario_fin, estado)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

                 valores = (
                      nombre_actividad,
                      id_espacio,
                      id_disciplina,
                      cupo,
                      diaSemana,
                      horario_inicio,
                      horario_final,
                      estado
                 )

                 cursor.execute(sql, valores)
                 cnx.commit()
     elif accion == 2 : 
        cursor.execute("SELECT * FROM ACTIVIDAD")
        actividades = cursor.fetchall()
        print("\n=== ACTIVIDADES ===")

        for actividad in actividades:
                print(
                f"ID: {actividad[0]} | "
                f"Nombre actividad: {actividad[1]}| "
                f"ID actividad: {actividad[2]} |"
                f"ID disciplina: {actividad[3]} |"
                f"cupo : {actividad[4]} |"
                f"Dia : {actividad[5]} |"
                f"horario inicio : {actividad[6]}|"
                f"horario fin {actividad[7]}|"
                f"estado : {actividad[8]}"
            )
                
        editarID = int(input('ID de la actividad a modificar'))
        cursor.execute("SELECT * FROM ACTIVIDAD WHERE id_actividad = %s",(editarID,))
        actividad = cursor.fetchone()
        if actividad is None :
            print('no existe una actividad con ese ID')
            exit()
        else :
            nombreActividad = input('Nombre Actividad :')
            id_espacio = int(input('Id espacio'))
            cursor.execute("SELECT * FROM ESPACIO_DEPORTIVO WHERE id_espacio = %s",(id_espacio,))
            espacio = cursor.fetchone()
            if espacio is None :
                print('no existe un espacio con ese ID')
                exit()


            id_disciplina = int(input('Id disciplina'))
            cursor.execute("SELECT * FROM DISCIPLINA WHERE id_disciplina = %s",(id_disciplina,))
            disciplina = cursor.fetchone()
            if disciplina is None :
                print('no existe una disciplina con ese ID')
                exit()
            
            
            
            cupo = int(input('Cupo Maximo'))
            diaSemana = input('Dia de semana')
            
            horario_inicio = None
            while True:
                 entrada = input("Ingresa la hora de inicio (HH:MM:SS): ")
                 try:
                     # Intenta la conversión
                     horario_inicio = datetime.strptime(entrada, "%H:%M:%S").time()
                     break  # Rompe el bucle si todo salió bien
                 except ValueError:
                     # Se ejecuta si el formato ingresado es incorrecto
                     print("Formato incorrecto. Usa HH:MM:SS.")
            
            horario_final = None
            while True:
                 entrada = input("Ingresa la hora final (HH:MM:SS): ")
                 try:
                     # Intenta la conversión
                     horario_final = datetime.strptime(entrada, "%H:%M:%S").time()
                     break  # Rompe el bucle si todo salió bien
                 except ValueError:
                     # Se ejecuta si el formato ingresado es incorrecto
                     print("Formato incorrecto. Usa HH:MM:SS.")
            
            estado = input('Estado :')
            if estado != 'abierta' and estado != 'cerrada' and estado != 'finalizada' and estado != 'cancelada' :
                 print("NO EXISTE ESE ESTADO")
                 exit()
            else : 
                 sql = """UPDATE ACTIVIDAD
                 SET nombre_actividad = %s,
                 id_espacio = %s,
                 id_disciplina = %s,
                 cupo_maximo = %s,
                 dia_semana = %s,
                 horario_inicio = %s,
                 horario_fin = %s,
                 estado = %s
                 WHERE id_actividad = %s"""
                 valores = (
                      nombreActividad,
                      id_espacio,
                      id_disciplina,
                      cupo,
                      diaSemana,
                      horario_inicio,
                      horario_final,
                      estado,
                      editarID
                 )             
                 cursor.execute(sql, valores)
                 cnx.commit()
     elif accion == 3 :
        cursor.execute("SELECT * FROM ACTIVIDAD")
        actividades = cursor.fetchall()
        print("\n=== ACTIVIDADES ===")

        for actividad in actividades:
                print(
                f"ID: {actividad[0]} | "
                f"Nombre actividad: {actividad[1]}| "
                f"ID actividad: {actividad[2]} |"
                f"ID disciplina: {actividad[3]} |"
                f"cupo : {actividad[4]} |"
                f"Dia : {actividad[5]} |"
                f"horario inicio : {actividad[6]}|"
                f"horario fin {actividad[7]}|"
                f"estado : {actividad[8]}"
            )
        borrarID = int(input('id a borrar\n'))
        cursor.execute("SELECT * FROM ACTIVIDAD WHERE id_actividad = %s",(borrarID,))
        actividad = cursor.fetchone()
        if actividad is None :
            print('no existe una actividad con ese ID')
            exit()
        else : 
             sql = """DELETE FROM ACTIVIDAD WHERE id_actividad = %s"""
             valores = (borrarID,)
             cursor.execute(sql, valores)
             cnx.commit()
     else : 
        print('error')
        exit()
elif opt == 5 : 
     id_actividad = int(input('ID a actividad\n'))
     cursor.execute("SELECT * FROM ACTIVIDAD WHERE id_actividad = %s",(id_actividad,))
     actividad = cursor.fetchone()
     if actividad is None :
         print('no existe una actividad con ese ID')
         exit()
     id_estudiante = int(input("ID del estudiante: "))
     cursor.execute("SELECT * FROM ESTUDIANTE WHERE id_estudiante = %s",(id_estudiante,))
     estudiante = cursor.fetchone()
     if estudiante is None :
         print('no existe un estudiante con ese ID')
         exit()
     inscirpcion_estudiante(cnx, id_estudiante, id_actividad)
elif opt == 6 :
    
    id_actividad = int(input('ID a actividad\n'))
    cursor.execute("SELECT * FROM ACTIVIDAD WHERE id_actividad = %s",(id_actividad,))
    actividad = cursor.fetchone()
    if actividad is None :
        print('no existe una actividad con ese ID')
        exit()

    id_estudiante = int(input("ID del estudiante: "))
    cursor.execute("SELECT * FROM ESTUDIANTE WHERE id_estudiante = %s",(id_estudiante,))
    estudiante = cursor.fetchone()
    if estudiante is None :
        print('no existe un estudiante con ese ID')
        exit()
    
    cursor.execute("""SELECT * FROM INSCRIPCION
        WHERE id_estudiante = %s AND id_actividad = %s AND estado_inscripcion = 'inscripto'""", (id_estudiante, id_actividad))
    inscripcion = cursor.fetchone()
    if inscripcion is None :
        print("No existe una incripcion con ese estudiante y esa actividad o esta en lista de espera")
        exit()    
   
    while True:
                 entrada = input("Ingresa la hora de inicio (HH:MM): ")
                 try:
                     # Intenta la conversión
                     horario_inicio = datetime.strptime(entrada, "%H:%M").time()
                     break  # Rompe el bucle si todo salió bien
                 except ValueError:
                     # Se ejecuta si el formato ingresado es incorrecto
                     print("Formato incorrecto. Usa HH:MM:SS.")
    

elif opt == 7 : 
     numeroConsulta = int(input('numero de consulta a realizar :\n 1 Actividad con max inscriptos\n 2 consulta actividades con cupos disponibles\n' \
     ' 3 cantidad Inscriptos por disciplina\n 4 : cantidad inscriptos por facultad\n 5 porcentaje ocupados por actividad\n ' \
     '6 porcentaje de asistencia por actividad\n 7 estudiantes con 3 o mas inasistencias'))

     if numeroConsulta == 1 :
        actividadMaxInscriptos(cnx)   

     elif numeroConsulta == 2 :
        actividadesCuposDisponibles(cnx)

     elif numeroConsulta == 3 : 
        cantInscriptosDisciplina(cnx)
     
     elif numeroConsulta == 4 :
        cantInscriptosFacultad(cnx)

     elif numeroConsulta == 5 :
        porciento = porcentajeOcupacionActividad(cnx)
        if porciento is None :
            exit()
        print(f'ocupada al : {porciento} % ')
     elif numeroConsulta == 6 :
        porcentajeAsistenciaActividad(cnx)

     elif numeroConsulta == 7 :
        estudiantesConInasistencias(cnx)
else : exit()

     
                
            

            

          
        
          
    
