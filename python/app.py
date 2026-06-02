import mysql.connector
cnx = mysql.connector.connect(user='root', password='Locostib2005.', host='127.0.0.1', database='gestion_deportes_universidad')
cursor =cnx.cursor()

print('Seleccione un tipo para reealizar un ABM:  1 estudiantes, 2 disciplinas', 3 ..)
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
     
