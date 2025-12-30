import mysql.connector
from mysql.connector import Error

DB_HOST = "localhost"
DB_USUARIO = "root"
DB_PASSWORD = "44616984anaA"
DB_NOMBRE = "energia_db"

def crear_conexion():
    """ 
    Crea una conexión a la base de datos usando la configuración de este archivo.
    """
    try:
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USUARIO,
            passwd=DB_PASSWORD,
            database=DB_NOMBRE
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None