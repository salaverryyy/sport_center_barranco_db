import psycopg2
from faker import Faker
import random

# Conectar a la base de datos
conn = psycopg2.connect(
    host="localhost",     # Dirección del servidor
    database="hito2_bd", # Nombre de la base de datos
    user="postgres",       # Nombre de usuario
    password="Forgiven7x7" # Contraseña de usuario
)


cursor = conn.cursor()
fake = Faker()

# Cambiar el esquema al que se conectará el cursor para insertar datos
def set_schema(cursor, esquema):
    cursor.execute(f'SET search_path TO {esquema};')


# Usuario listo
# Función para insertar datos en la tabla Usuario
def insertar_usuarios(cursor, cantidad):
    dni_contador = 11111111  # Inicializar el contador de DNI
    for _ in range(cantidad):
        dni = dni_contador  # Asignar el DNI desde el contador
        dni_contador += 1  # Incrementar el contador en 1 para el siguiente DNI
        nombre = fake.name()
        # Generar un número de teléfono que comience con 9 y tenga exactamente 9 dígitos
        telefono = "9" + ''.join([random.choice("0123456789") for _ in range(8)])  # 9 seguido de 8 dígitos aleatorios

        distrito = random.choice(["Barranco", "Miraflores", "San Isidro", "Chorrilos", "Lince"])  # Aleatorio
        cursor.execute("""
            INSERT INTO Usuario (dni, nombre, telefono, distrito)
            VALUES (%s, %s, %s, %s)
        """, (dni, nombre, telefono, distrito))


#Tipo Cancha listo
# Función para insertar datos en la tabla TipoCancha
def insertar_tipocancha(cursor):
    # Insertamos los diferentes tipos de cancha con el nombre como id
    tipocanchas = [
        ("fut11", "fútbol","futbol 11" , "césped sintético", 250.0),
        ("fut9", "fútbol", "futbol 9" ,"césped sintético", 150.0),
        ("fut7", "fútbol", "futbol 7","césped sintético", 80.0),
        ("losa", "futsal", "estandar futsal","losa", 40.0),
        ("voley", "vóley", "estandar voley","losa", 40.0),
        ("basquet", "básquet", "estandar basquet","losa", 40.0)
    ]
    for t in tipocanchas:
        cursor.execute("""
            INSERT INTO TipoCancha (id_tipo_cancha, deporte, tamaño, superficie, precio_base_hora)
            VALUES (%s, %s, %s, %s, %s)
        """, (t[0], t[1], t[2], t[3], t[4]))


#Cancha Listo
# Función para insertar datos en la tabla Cancha
def insertar_canchas(cursor):
    # La cantidad de canchas es limitada a la cantidad de tipos
    canchas = [
        ("cancha 1", "fut11"), ("cancha 2", "fut9"), ("cancha 3", "fut9"), ("cancha 4", "fut7"), ("cancha 5", "fut7"),
        ("losa 1", "losa"), ("losa 2", "losa"), ("losa 3", "losa"), ("losa 4", "losa"), ("cancha voley 1", "voley"),
        ("cancha voley 2", "voley"), ("cancha basquet 1", "basquet"), ("cancha basquet 2", "basquet")
    ]
    
    # Insertamos las canchas, utilizando el id_tipo_cancha como nombre(varchar))
    for i, c in enumerate(canchas, start=1):
        cursor.execute("""
            INSERT INTO Cancha (id_cancha, id_tipo_cancha, nombre)
            VALUES (%s, %s, %s)
        """, (i, c[1], c[0]))  # El id_tipo_cancha es ahora el nombre como VARCHAR

#Horario listo
# Función para insertar datos en la tabla Horario
def insertar_horarios(cursor, cantidad):
    # El horario es desde 7 AM hasta 10 PM, con franjas de 1, 2 o 3 horas
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
    horas_disponibles = [1, 2, 3]  # reservas de 1, 2 hasta 3 horas
    horario_id = 1  # Comenzamos el contador de id_horario desde 1
    
    horarios_insertados = 0  # Contador de horarios insertados
    
    while horarios_insertados < cantidad:  # Mientras no se hayan insertado la cantidad requerida de horarios
        for dia in dias:
            for hora in range(7, 22):  # Desde las 7 AM hasta las 10 PM
                for duracion in horas_disponibles:
                    hora_inicio = f"{hora:02}:00"  # Formato de hora 07:00, 08:00, etc.
                    
                    # Insertamos el horario en la base de datos
                    cursor.execute("""
                        INSERT INTO Horario (id_horario, dia_semana, hora_inicio, cant_horas)
                        VALUES (%s, %s, %s, %s)
                    """, (horario_id, dia, hora_inicio, duracion))
                    
                    horarios_insertados += 1  # Incrementamos el contador de horarios insertados
                    horario_id += 1  # Incrementamos el id_horario para el siguiente
                    
                    # Si hemos insertado la cantidad de horarios que necesitamos, terminamos el bucle
                    if horarios_insertados >= cantidad:
                        break
                if horarios_insertados >= cantidad:
                    break
            if horarios_insertados >= cantidad:
                break



# Reserva listo
# Función para insertar datos en la tabla Reserva
def insertar_reservas(cursor, cantidad):
    # Obtener todos los DNI existentes en la tabla Usuario
    cursor.execute("SELECT dni FROM Usuario")
    dni_usuarios = [row[0] for row in cursor.fetchall()]  # Lista de los DNI de usuarios existentes
    
    # Obtener todos los ID de horarios existentes en la tabla Horario
    cursor.execute("SELECT id_horario FROM Horario")
    horarios_disponibles = [row[0] for row in cursor.fetchall()]  # Lista de los id_horarios existentes
    
    if len(horarios_disponibles) < cantidad:
        raise ValueError("No hay suficientes horarios disponibles para asignar a las reservas.")

    # Barajamos los horarios disponibles para asignar aleatoriamente
    random.shuffle(horarios_disponibles)

    for i in range(cantidad):
        # Elegir aleatoriamente un DNI de los usuarios existentes
        dni_usuario = random.choice(dni_usuarios)  # Solo tomamos usuarios existentes
        
        # Asignamos un horario único de los horarios disponibles
        id_horario = horarios_disponibles.pop()  # Sacamos un horario único de la lista (y lo eliminamos de la lista)
        
        id_cancha = random.randint(1, 13)  # 13 canchas disponibles
        fecha = fake.date_this_year()  # Fecha aleatoria dentro del año
        estado = random.choice(["pendiente", "pagada", "cancelada"])  # "pagada", "pendiente", "cancelada"
        
        # Insertamos la reserva; el costo_total será calculado automáticamente por el trigger
        cursor.execute("""
            INSERT INTO Reserva (dni, id_cancha, id_horario, fecha, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (dni_usuario, id_cancha, id_horario, fecha, estado))


# Pago listo
# Función para insertar datos en la tabla Pago
def insertar_pagos(cursor):
    # Obtener todas las reservas con estado "pagada"
    cursor.execute("SELECT id_reserva, costo_total, fecha FROM Reserva WHERE estado = 'pagada'")
    reservas_pagadas = cursor.fetchall()  # Lista de reservas pagadas con su costo_total y fecha

    # Verificamos si hay reservas pagadas para asignar los pagos
    if len(reservas_pagadas) == 0:
        print("No hay reservas con estado 'pagada' para asignar pagos.")
        return  # Si no hay reservas pagadas, terminamos la función

    # Barajamos las reservas pagadas para asignar aleatoriamente los pagos
    random.shuffle(reservas_pagadas)
    
    for reserva in reservas_pagadas:
        id_reserva, costo_total, fecha_reserva = reserva
        
        # Generamos un medio de pago aleatorio
        medio_pago = random.choice(["Yape", "Plin", "Tarjeta"])
        
        # Generamos una fecha de pago aleatoria: debe ser el mismo día o antes de la fecha de la reserva
        fecha_pago = fake.date_this_year()  # Fecha aleatoria dentro del año
        while fecha_pago > fecha_reserva:  # Aseguramos que la fecha de pago sea igual o antes de la reserva
            fecha_pago = fake.date_this_year()  # Repetimos si la fecha es posterior a la fecha de la reserva
        
        # Insertamos el pago en la tabla Pago
        cursor.execute("""
            INSERT INTO Pago (id_reserva, medio_pago, monto_pagado, fecha_pago)
            VALUES (%s, %s, %s, %s)
        """, (id_reserva, medio_pago, costo_total, fecha_pago))  # El monto pagado es igual al costo_total de la reserva




set_schema(cursor, 'datos_100k')
insertar_usuarios(cursor, 100000)
insertar_tipocancha(cursor)
insertar_canchas(cursor)
insertar_horarios(cursor,100000)
insertar_reservas(cursor, 100000)
insertar_pagos(cursor) 

# Guardar los cambios
conn.commit()

# Cerrar la conexión
cursor.close()
conn.close()
