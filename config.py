import os
from pathlib import Path

# Intentar cargar dotenv si está instalado
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Variables de entorno cargadas desde .env")
except ImportError:
    print("⚠️ python-dotenv no instalado. Instalar con: pip install python-dotenv")
except Exception as e:
    print(f"⚠️ Error cargando .env: {e}")

# Variables de entorno con valores por defecto
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "ejemplo@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "ejemplo@gmail.com")

# Validación
if not EMAIL_PASSWORD:
    print("⚠️ WARNING: EMAIL_PASSWORD no configurado en .env")