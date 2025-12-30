import smtplib
import ssl
from email.message import EmailMessage
import sys
import os

# Mapa para encontrar el archivo de configuración
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

import config

def enviar_alerta_por_correo(asunto, cuerpo_mensaje):
    """Envía un correo electrónico usando las credenciales del archivo de configuración."""

    msg = EmailMessage()
    msg['Subject'] = asunto
    msg['From'] = config.EMAIL_SENDER
    msg['To'] = config.EMAIL_RECEIVER
    msg.set_content(cuerpo_mensaje)

    # Creamos un contexto seguro para la conexión
    contexto_seguro = ssl.create_default_context()

    try:
        print(f"Intentando enviar correo a {config.EMAIL_RECEIVER}...")
        # Nos conectamos al servidor de Gmail por un puerto seguro
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto_seguro) as smtp:
            smtp.login(config.EMAIL_SENDER, config.EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("¡Correo de alerta enviado exitosamente!")
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False

# --- Ejemplo de cómo usar la función (para pruebas) ---
if __name__ == '__main__':
    asunto_prueba = "Alerta de Prueba - Sistema de Energía"
    cuerpo_prueba = "Este es un mensaje de prueba para verificar que el servicio de notificaciones funciona."
    enviar_alerta_por_correo(asunto_prueba, cuerpo_prueba)