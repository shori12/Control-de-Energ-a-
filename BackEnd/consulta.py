from functools import wraps
from BackEnd.conexion import crear_conexion
from mysql.connector import Error
import bcrypt
import secrets
from datetime import datetime, timedelta


# --- "Asistente" Decorador ---
def manejar_conexion_bd(es_escritura=False):
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            resultado = None
            conn = crear_conexion()
            if not conn:
                if "registrar" in func.__name__ or "resetear" in func.__name__:
                    return False, "Error de conexión a la base de datos."
                if "generar_token" in func.__name__:
                    return None, "Error de conexión a la base de datos."
                return None
            try:
                cursor = conn.cursor(dictionary=True)
                resultado = func(cursor, *args, **kwargs)
                if es_escritura:
                    conn.commit()
            except Error as e:
                print(f"Error en la base de datos durante '{func.__name__}': {e}")
                if "registrar_usuario" in func.__name__ and e.errno == 1062:
                    return False, f"El nombre de usuario ya existe."
                if es_escritura:
                    return False, f"Error al escribir en la base de datos: {e}"
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
            return resultado
        return wrapper
    return decorador


# --- Funciones de Usuario ---

@manejar_conexion_bd(es_escritura=True)
def registrar_usuario(cursor, nombre_usuario, password_plano, nombre_completo, email, rol):

    # --- Verificar cupo de ADMIN ---
    if rol == "admin":
        cursor.execute("SELECT COUNT(*) AS total FROM usuarios WHERE rol = 'admin'")
        total_admin = cursor.fetchone()["total"]
        if total_admin >= 1:
            return False, "Ya existe un administrador. No se pueden crear más."

    # --- Verificar si el nombre_usuario ya existe ---
    cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", (nombre_usuario,))
    if cursor.fetchone():
        return False, "El nombre de usuario ya está en uso."

    # --- Crear usuario ---
    password_hash = bcrypt.hashpw(password_plano.encode('utf-8'), bcrypt.gensalt())
    query = """
        INSERT INTO usuarios (nombre_usuario, password_hash, nombre_completo, email, rol)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (nombre_usuario, password_hash, nombre_completo, email, rol))

    return True, "Usuario registrado exitosamente."




@manejar_conexion_bd()
def verificar_usuario(cursor, nombre_usuario, password_plano):
    query = "SELECT rol, password_hash FROM usuarios WHERE nombre_usuario = %s"
    cursor.execute(query, (nombre_usuario,))
    usuario = cursor.fetchone()

    if not usuario:
        return None

    if usuario["password_hash"] is None:
        return None

    # Verificar contraseña
    if not bcrypt.checkpw(password_plano.encode('utf-8'), usuario["password_hash"].encode('utf-8')):
        return None

    # --- MODIFICACIÓN CLAVE AQUÍ ---
    # Unificamos la comparación a minúsculas para evitar errores de case.
    rol_db = usuario["rol"].lower()
    
    # 1. Si el rol es 'admin', devolvemos 'Admin' (con mayúscula inicial para el Frontend)
    if rol_db == "admin":
        return "Admin" 

    # 2. Si es 'gerente' o 'empleado', devolvemos 'Empleado' (unificando el rol Gerente)
    if rol_db in ["gerente", "empleado"]:
        return "Empleado"

    # Si hay un rol desconocido, fallamos.
    return None


@manejar_conexion_bd(es_escritura=True)
def generar_token_reseteo(cursor, email):
    """Genera y guarda un token de reseteo de 6 dígitos."""
    query_check = "SELECT id FROM usuarios WHERE email = %s"
    cursor.execute(query_check, (email,))
    usuario = cursor.fetchone()

    if not usuario:
        return None, "No existe un usuario con ese correo electrónico."
    
    token = str(secrets.randbelow(1_000_000)).zfill(6)
    expiracion = datetime.now() + timedelta(minutes=15)

    query_update = "UPDATE usuarios SET reset_token = %s, reset_token_expiration = %s WHERE id = %s"
    cursor.execute(query_update, (token, expiracion, usuario['id']))
    return token, "Token generado exitosamente."


@manejar_conexion_bd(es_escritura=True)
def resetear_password_con_token(cursor, token, nueva_password):
    """Verifica un token y actualiza la contraseña."""
    query_find = "SELECT id FROM usuarios WHERE reset_token = %s AND reset_token_expiration > NOW()"
    cursor.execute(query_find, (token,))
    usuario = cursor.fetchone()

    if not usuario:
        return False, "El código es inválido o ha expirado."

    password_hash = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt())
    query_update = "UPDATE usuarios SET password_hash = %s, reset_token = NULL, reset_token_expiration = NULL WHERE id = %s"
    cursor.execute(query_update, (password_hash, usuario['id']))
    return True, "¡Contraseña actualizada exitosamente!"


# --- Funciones de Lecturas ---

@manejar_conexion_bd(es_escritura=True)
def insertar_lectura(cursor, id_circuito, potencia):
    """Inserta una nueva lectura de potencia."""
    query = "INSERT INTO lecturas (id_circuito, fecha, potencia_w) VALUES (%s, NOW(3), %s)"
    cursor.execute(query, (id_circuito, potencia))


@manejar_conexion_bd()
def obtener_ultima_lectura(cursor, id_circuito):
    """Obtiene la última lectura de potencia registrada."""
    query = "SELECT potencia_w FROM lecturas WHERE id_circuito = %s ORDER BY fecha DESC LIMIT 1"
    cursor.execute(query, (id_circuito,))
    resultado = cursor.fetchone()
    return resultado['potencia_w'] if resultado else 0.0


@manejar_conexion_bd()
def obtener_lecturas_para_grafico(cursor, id_circuito, horas=1):
    """Obtiene las lecturas de las últimas 'X' horas."""
    query = "SELECT fecha, potencia_w FROM lecturas WHERE id_circuito = %s AND fecha > NOW() - INTERVAL %s HOUR ORDER BY fecha ASC"
    cursor.execute(query, (id_circuito, horas))
    resultados = cursor.fetchall()
    fechas = [fila['fecha'] for fila in resultados]
    potencias = [fila['potencia_w'] for fila in resultados]
    return fechas, potencias


# --- ✅ FUNCIONES CORREGIDAS CON DECORADOR ---

@manejar_conexion_bd(es_escritura=True)
def insertar_lectura_manual(cursor, id_circuito, voltaje, corriente, potencia):
    """
    Inserta una lectura manual en la base de datos.
    
    Parámetros:
        cursor: Cursor de la base de datos (proporcionado por el decorador)
        id_circuito (int): ID del circuito
        voltaje (float): Voltaje en voltios
        corriente (float): Corriente en amperios
        potencia (float): Potencia en watts
    
    Retorna:
        bool: True si se insertó correctamente, False en caso contrario
    """
    try:
        # Query para MySQL usando %s como placeholder
        query = """
        INSERT INTO lecturas (id_circuito, fecha, voltaje_v, corriente_a, potencia_w)
        VALUES (%s, NOW(3), %s, %s, %s)
        """
        cursor.execute(query, (id_circuito, voltaje, corriente, potencia))
        print(f"[✅ INSERT] ID={id_circuito}, V={voltaje}V, I={corriente}A, P={potencia}W")
        return True
        
    except Error as e:
        print(f"[❌ ERROR INSERT] {e}")
        # Si la tabla no tiene columnas voltaje_v y corriente_a, usar solo potencia_w
        try:
            query_simple = """
            INSERT INTO lecturas (id_circuito, fecha, potencia_w)
            VALUES (%s, NOW(3), %s)
            """
            cursor.execute(query_simple, (id_circuito, potencia))
            print(f"[✅ INSERT SIMPLE] ID={id_circuito}, P={potencia}W")
            return True
        except Error as e2:
            print(f"[❌ ERROR INSERT SIMPLE] {e2}")
            return False


@manejar_conexion_bd(es_escritura=True)
def modificar_lectura(cursor, id_circuito, potencia, fecha=None):
    """
    Modifica una lectura existente en la base de datos.
    
    Parámetros:
        cursor: Cursor de la base de datos (proporcionado por el decorador)
        id_circuito (int): ID del circuito
        potencia (float): Nueva potencia en watts
        fecha (str, opcional): Fecha en formato 'YYYY-MM-DD HH:MM:SS'
    
    Retorna:
        bool: True si se modificó correctamente, False en caso contrario
    """
    try:
        if fecha:
            # Modificar lectura específica por fecha
            query = """
            UPDATE lecturas 
            SET potencia_w = %s 
            WHERE id_circuito = %s AND fecha = %s
            """
            cursor.execute(query, (potencia, id_circuito, fecha))
        else:
            # Modificar la última lectura del circuito
            query = """
            UPDATE lecturas 
            SET potencia_w = %s 
            WHERE id_circuito = %s 
            AND fecha = (
                SELECT MAX(fecha) 
                FROM (SELECT fecha FROM lecturas WHERE id_circuito = %s) AS subquery
            )
            """
            cursor.execute(query, (potencia, id_circuito, id_circuito))
        
        filas_afectadas = cursor.rowcount
        
        if filas_afectadas > 0:
            print(f"[✅ UPDATE] ID={id_circuito}, P={potencia}W, Filas={filas_afectadas}")
            return True
        else:
            print(f"[⚠️ UPDATE] No se encontró ninguna lectura para modificar")
            return False
            
    except Error as e:
        print(f"[❌ ERROR UPDATE] {e}")
        return False
    
    
# --- ✅ Inicialización automática: 1 gerente, 1 admin, 10 Empleados ---

# --- ✅ Inicialización automática: 1 gerente, 1 admin, 10 Empleados ---

@manejar_conexion_bd(es_escritura=True)
def inicializar_usuarios(cursor):
    """
    Configuración inicial:
    - Deja solo 1 Admin (el más antiguo).
    - Convierte cualquier 'Gerente' a 'Empleado'.
    - Deja solo 10 Empleados (los más antiguos).
    """
    print("--- Iniciando limpieza y unificación de roles ---")

    # 1. Convertir todos los Gerentes a Empleados (unificación de rol)
    cursor.execute("UPDATE usuarios SET rol = 'Empleado' WHERE rol = 'Gerente' OR rol = 'gerente'")
    print(f"[✔] Roles 'Gerente' convertidos a 'Empleado': {cursor.rowcount} usuarios afectados.")
    
    # 2. Limpiar Admins (dejar solo 1)
    # Nota: Usamos 'Admin' y 'admin' para asegurar la limpieza, pero el rol final será 'Admin' o 'Empleado'.
    cursor.execute("DELETE FROM usuarios WHERE rol = 'Admin' OR rol = 'admin' AND id NOT IN (SELECT id FROM (SELECT id FROM usuarios WHERE rol = 'Admin' OR rol = 'admin' ORDER BY id ASC LIMIT 1) as t)")
    print(f"[✔] Administradores duplicados eliminados.")
    
    # 3. Limpiar Empleados (dejar solo 10)
    cursor.execute("DELETE FROM usuarios WHERE rol = 'Empleado' OR rol = 'empleado' AND id NOT IN (SELECT id FROM (SELECT id FROM usuarios WHERE rol = 'Empleado' OR rol = 'empleado' ORDER BY id ASC LIMIT 10) as t)")
    print(f"[✔] Empleados en exceso eliminados (quedan 10).")

    print("--- Limpieza completada. Solo quedan roles 'Admin' y 'Empleado' ---")
    
@manejar_conexion_bd()
def obtener_lecturas_dia(cursor, id_circuito, fecha):
    """
    Obtiene todas las lecturas de un día específico
    
    Args:
        cursor: Cursor de la base de datos (proporcionado por el decorador)
        id_circuito: ID del circuito
        fecha: datetime object con la fecha a consultar
    
    Returns:
        tuple: (lista_fechas, lista_potencias)
    """
    try:
        from datetime import timedelta
        
        # Calcular inicio y fin del día
        fecha_inicio = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)
        
        query = """
            SELECT fecha, potencia_w 
            FROM lecturas 
            WHERE id_circuito = %s 
            AND fecha >= %s 
            AND fecha < %s
            ORDER BY fecha
        """
        
        cursor.execute(query, (id_circuito, fecha_inicio, fecha_fin))
        resultados = cursor.fetchall()
        
        fechas = [fila['fecha'] for fila in resultados]
        potencias = [fila['potencia_w'] for fila in resultados]
        
        return fechas, potencias
        
    except Error as e:
        print(f"Error al obtener lecturas del día: {e}")
        return [], []