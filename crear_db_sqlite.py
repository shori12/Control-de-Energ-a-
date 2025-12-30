import sqlite3
import bcrypt

def crear_base_datos():
    conn = sqlite3.connect('energia.db')
    cursor = conn.cursor()
    
    # Tabla sucursales
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sucursales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        direccion TEXT,
        ciudad TEXT,
        potencia_contratada_kw REAL
    )
    ''')
    
    # Tabla circuitos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS circuitos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_sucursal INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        identificador_hardware TEXT,
        umbral_alerta_w INTEGER,
        FOREIGN KEY (id_sucursal) REFERENCES sucursales(id)
    )
    ''')
    
    # Tabla lecturas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lecturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_circuito INTEGER NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        potencia_w REAL NOT NULL,
        FOREIGN KEY (id_circuito) REFERENCES circuitos(id)
    )
    ''')
    
    # Tabla usuarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_usuario TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        nombre_completo TEXT,
        email TEXT UNIQUE,
        rol TEXT NOT NULL CHECK(rol IN ('Admin', 'Empleado')),
        id_sucursal INTEGER,
        reset_token TEXT,
        reset_token_expiration TIMESTAMP,
        FOREIGN KEY (id_sucursal) REFERENCES sucursales(id)
    )
    ''')
    
    # Tabla alertas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alertas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_circuito INTEGER NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        tipo_alerta TEXT NOT NULL,
        valor_registrado REAL,
        mensaje TEXT,
        estado TEXT DEFAULT 'Nueva' CHECK(estado IN ('Nueva', 'Vista', 'Resuelta')),
        FOREIGN KEY (id_circuito) REFERENCES circuitos(id)
    )
    ''')
    
    # Insertar datos iniciales
    cursor.execute('''
    INSERT OR IGNORE INTO sucursales (id, nombre, direccion, ciudad, potencia_contratada_kw)
    VALUES (1, 'FN MUDAD', 'Los Nogales 1306', 'Tafí Viejo', 500000.00)
    ''')
    
    cursor.execute('''
    INSERT OR IGNORE INTO circuitos (id, id_sucursal, nombre, descripcion)
    VALUES (1, 1, 'Consumo Total Simulado', 'Medición general para pruebas de software')
    ''')
    
    # Crear usuario admin por defecto
    password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute('''
    INSERT OR IGNORE INTO usuarios (nombre_usuario, password_hash, nombre_completo, email, rol)
    VALUES ('admin', ?, 'Administrador', 'admin@test.com', 'Admin')
    ''', (password_hash,))
    
    conn.commit()
    conn.close()
    print("✅ Base de datos SQLite creada exitosamente!")
    print("📁 Archivo: energia.db")
    print("👤 Usuario admin creado: admin / admin123")

if __name__ == '__main__':
    crear_base_datos()