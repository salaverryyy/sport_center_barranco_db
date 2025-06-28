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

# Función para insertar datos en la tabla Usuario
def insertar_usuarios(cursor, cantidad):
    for _ in range(cantidad):
        dni = fake.random_int(min=10000000, max=99999999)  # Genera un DNI aleatorio
        nombre = fake.name()
        telefono = fake.phone_number()
        distrito = random.choice(["Barranco", "Miraflores", "San Isidro", "Chorrilos", "Lince"])  # Aleatorio
        cursor.execute("""
            INSERT INTO Usuario (dni, nombre, telefono, distrito)
            VALUES (%s, %s, %s, %s)
        """, (dni, nombre, telefono, distrito))

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
            INSERT INTO TipoCancha (id_tipo_cancha, deporte,tamaño, superficie, precio_base_hora)
            VALUES (%s, %s, %s, %s)
        """, (t[0], t[1], t[2], t[3]))

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


# Función para insertar datos en la tabla Horario
def insertar_horarios(cursor):
    # El horario es desde 7 AM hasta 10 PM, con franjas de 1 o 2 horas
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes','Sabado','Domingo']
    
    # Se puede definir la cantidad de horas de cada reserva (en este caso 1, 2 hasta 3 horas)
    horas_disponibles = [1, 2, 3]  # reservas de 1, 2 hasta 3 horas
    
    for dia in dias:
        for hora in range(7, 22):  # Desde las 7 AM hasta las 10 PM
            for duracion in horas_disponibles:
                hora_inicio = f"{hora:02}:00"  # Formato de hora 07:00, 08:00, etc.
                cursor.execute("""
                    INSERT INTO Horario (dia_semana, hora_inicio, cant_horas)
                    VALUES (%s, %s, %s)
                """, (dia, hora_inicio, duracion))



# Función para insertar datos en la tabla Reserva
def insertar_reservas(cursor, cantidad):
    # Obtener todos los DNI existentes en la tabla Usuario
    cursor.execute("SELECT dni FROM Usuario")
    dni_usuarios = [row[0] for row in cursor.fetchall()]  # Lista de los DNI de usuarios existentes
    
    for _ in range(cantidad):
        # Elegir aleatoriamente un DNI de los usuarios existentes
        dni_usuario = random.choice(dni_usuarios)  # Solo tomamos usuarios existentes
        id_cancha = random.randint(1, 13)  # 13 canchas disponibles
        id_horario = random.randint(1, 39)  # 39 horarios disponibles
        fecha = fake.date_this_year()  # Fecha aleatoria dentro del año
        estado = random.choice(["pendiente", "pagada", "cancelada"])  # "pagada", "pendiente", "cancelada"
        
        # Insertamos la reserva; el costo_total será calculado automáticamente por el trigger
        cursor.execute("""
            INSERT INTO Reserva (dni, id_cancha, id_horario, fecha, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (dni_usuario, id_cancha, id_horario, fecha, estado))

        # Si el estado es "pagada", insertar el pago correspondiente
        if estado == "pagada":
            # Elegimos aleatoriamente el medio de pago (Yape, Plin o Tarjeta)
            medio_pago = random.choice(["Yape", "Plin", "Visa", "MasterCard"])
            cursor.execute("""
                INSERT INTO Pago (id_reserva, medio_pago, monto_pagado, fecha_pago)
                VALUES (currval('reserva_id_reserva_seq'), %s, (SELECT costo_total FROM Reserva WHERE id_reserva = currval('reserva_id_reserva_seq')), %s)
            """, (medio_pago, fecha))


# Función para insertar datos en la tabla Pago
def insertar_pagos(cursor, cantidad):
    for _ in range(cantidad):
        id_reserva = random.randint(1, 10000)  # Aleatorio de las reservas generadas
        medio_pago = random.choice(["Yape", "Plin", "Visa", "MasterCard"])
        monto_pagado = random.uniform(50.0, 200.0)  # Asumimos que pagan el costo total
        fecha_pago = fake.date_this_year()
        cursor.execute("""
            INSERT INTO Pago (id_reserva, medio_pago, monto_pagado, fecha_pago)
            VALUES (%s, %s, %s, %s)
        """, (id_reserva, medio_pago, monto_pagado, fecha_pago))

# Inserta 10,000 usuarios, 13 canchas, 39 horarios y 10,000 reservas como ejemplo
insertar_usuarios(cursor, 10000)
insertar_tipocancha(cursor)
insertar_canchas(cursor)
insertar_horarios(cursor)
insertar_reservas(cursor, 10000)
insertar_pagos(cursor, 800)  # 800 pagos para reservas pagadas, el resto será pendiente o cancelado

# Guardar los cambios
conn.commit()

# Cerrar la conexión
cursor.close()
conn.close()