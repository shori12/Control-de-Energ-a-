from functools import wraps
from BackEnd.conexion import crear_conexion
import bcrypt
import secrets
from datetime import datetime, timedelta


# --- Decorador compatible con SQLite ---
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
                cursor = conn.cursor()
                resultado = func(cursor, *args, **kwargs)
                if es_escritura:
                    conn.commit()
            except Exception as e:
                print(f"Error en la base de datos durante '{func.__name__}': {e}")
                if "registrar_usuario" in func.__name__ and "UNIQUE constraint failed" in str(e):
                    return False, f"El nombre de usuario ya existe."
                if es_escritura:
                    return False, f"Error al escribir en la base de datos: {e}"
            finally:
                try:
                    cursor.close()
                    conn.close()
                except:
                    pass
            return resultado
        return wrapper
    return decorador


# --- Funciones de Usuario ---

@manejar_conexion_bd(es_escritura=True)
def registrar_usuario(cursor, nombre_usuario, password_plano, nombre_completo, email, rol):
    # Verificar cupo de ADMIN
    if rol.lower() == "admin":
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'Admin'")
        total_admin = cursor.fetchone()[0]
        if total_admin >= 1:
            return False, "Ya existe un administrador. No se pueden crear más."

    # Verificar si el nombre_usuario ya existe
    cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = ?", (nombre_usuario,))
    if cursor.fetchone():
        return False, "El nombre de usuario ya está en uso."

    # Crear usuario
    password_hash = bcrypt.hashpw(password_plano.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    query = """
        INSERT INTO usuarios (nombre_usuario, password_hash, nombre_completo, email, rol)
        VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(query, (nombre_usuario, password_hash, nombre_completo, email, rol))
    return True, "Usuario registrado exitosamente."


@manejar_conexion_bd()
def verificar_usuario(cursor, nombre_usuario, password_plano):
    query = "SELECT rol, password_hash FROM usuarios WHERE nombre_usuario = ?"
    cursor.execute(query, (nombre_usuario,))
    row = cursor.fetchone()

    if not row:
        return None

    rol, password_hash = row[0], row[1]

    if not password_hash:
        return None

    # Verificar contraseña
    if not bcrypt.checkpw(password_plano.encode('utf-8'), password_hash.encode('utf-8')):
        return None

    # Unificar roles
    rol_db = rol.lower()
    
    if rol_db == "admin":
        return "Admin" 

    if rol_db in ["gerente", "empleado"]:
        return "Empleado"

    return None


@manejar_conexion_bd(es_escritura=True)
def generar_token_reseteo(cursor, email):
    query_check = "SELECT id FROM usuarios WHERE email = ?"
    cursor.execute(query_check, (email,))
    row = cursor.fetchone()

    if not row:
        return None, "No existe un usuario con ese correo electrónico."
    
    usuario_id = row[0]
    token = str(secrets.randbelow(1_000_000)).zfill(6)
    expiracion = datetime.now() + timedelta(minutes=15)

    query_update = "UPDATE usuarios SET reset_token = ?, reset_token_expiration = ? WHERE id = ?"
    cursor.execute(query_update, (token, expiracion, usuario_id))
    return token, "Token generado exitosamente."


@manejar_conexion_bd(es_escritura=True)
def resetear_password_con_token(cursor, token, nueva_password):
    query_find = "SELECT id FROM usuarios WHERE reset_token = ? AND reset_token_expiration > datetime('now')"
    cursor.execute(query_find, (token,))
    row = cursor.fetchone()

    if not row:
        return False, "El código es inválido o ha expirado."

    usuario_id = row[0]
    password_hash = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    query_update = "UPDATE usuarios SET password_hash = ?, reset_token = NULL, reset_token_expiration = NULL WHERE id = ?"
    cursor.execute(query_update, (password_hash, usuario_id))
    return True, "¡Contraseña actualizada exitosamente!"


# --- Funciones de Lecturas ---

@manejar_conexion_bd(es_escritura=True)
def insertar_lectura(cursor, id_circuito, potencia):
    query = "INSERT INTO lecturas (id_circuito, fecha, potencia_w) VALUES (?, datetime('now'), ?)"
    cursor.execute(query, (id_circuito, potencia))


@manejar_conexion_bd()
def obtener_ultima_lectura(cursor, id_circuito):
    query = "SELECT potencia_w FROM lecturas WHERE id_circuito = ? ORDER BY fecha DESC LIMIT 1"
    cursor.execute(query, (id_circuito,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else 0.0


@manejar_conexion_bd()
def obtener_lecturas_para_grafico(cursor, id_circuito, horas=1):
    query = "SELECT fecha, potencia_w FROM lecturas WHERE id_circuito = ? AND fecha > datetime('now', '-' || ? || ' hours') ORDER BY fecha ASC"
    cursor.execute(query, (id_circuito, horas))
    resultados = cursor.fetchall()
    fechas = [datetime.fromisoformat(fila[0]) for fila in resultados]
    potencias = [fila[1] for fila in resultados]
    return fechas, potencias


@manejar_conexion_bd(es_escritura=True)
def insertar_lectura_manual(cursor, id_circuito, voltaje, corriente, potencia):
    try:
        query = "INSERT INTO lecturas (id_circuito, fecha, potencia_w) VALUES (?, datetime('now'), ?)"
        cursor.execute(query, (id_circuito, potencia))
        print(f"[✅ INSERT] ID={id_circuito}, P={potencia}W")
        return True
    except Exception as e:
        print(f"[❌ ERROR INSERT] {e}")
        return False


@manejar_conexion_bd(es_escritura=True)
def modificar_lectura(cursor, id_circuito, potencia, fecha=None):
    try:
        if fecha:
            query = "UPDATE lecturas SET potencia_w = ? WHERE id_circuito = ? AND fecha = ?"
            cursor.execute(query, (potencia, id_circuito, fecha))
        else:
            query = """
            UPDATE lecturas 
            SET potencia_w = ? 
            WHERE id_circuito = ? 
            AND fecha = (SELECT MAX(fecha) FROM lecturas WHERE id_circuito = ?)
            """
            cursor.execute(query, (potencia, id_circuito, id_circuito))
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"[❌ ERROR UPDATE] {e}")
        return False


@manejar_conexion_bd()
def obtener_lecturas_dia(cursor, id_circuito, fecha):
    try:
        from datetime import timedelta
        
        fecha_inicio = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)
        
        query = """
            SELECT fecha, potencia_w 
            FROM lecturas 
            WHERE id_circuito = ? 
            AND fecha >= ? 
            AND fecha < ?
            ORDER BY fecha
        """
        
        cursor.execute(query, (id_circuito, fecha_inicio.isoformat(), fecha_fin.isoformat()))
        resultados = cursor.fetchall()
        
        fechas = [datetime.fromisoformat(fila[0]) for fila in resultados]
        potencias = [fila[1] for fila in resultados]
        
        return fechas, potencias
    except Exception as e:
        print(f"Error al obtener lecturas del día: {e}")
        return [], []