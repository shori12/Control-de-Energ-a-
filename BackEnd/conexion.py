import sqlite3

DB_PATH = "energia.db"

def crear_conexion():
    """ 
    Crea una conexión a la base de datos SQLite.
    """
    try:
        conexion = sqlite3.connect(DB_PATH)
        conexion.row_factory = sqlite3.Row
        return conexion
    except Exception as e:
        print(f"Error al conectar a SQLite: {e}")
        return None