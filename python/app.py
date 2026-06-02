import mysql.connector
cnx = mysql.connector.connect(user='root', password='Locostib2005.', host='127.0.0.1', database='gestion_deportes_universidad')
cursor =cnx.cursor()

print('Seleccione un tipo para reealizar un ABM:  1 estudiantes, 2 disciplinas, 3 Espacios Derpotivos, 4 ..')
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
else : print('error')  
                
        
          
    
