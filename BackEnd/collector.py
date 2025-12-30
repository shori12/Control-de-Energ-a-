import random
import time
import sys
import os

# Mapa para encontrar la carpeta raíz del proyecto (para importaciones)
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

# Usamos importaciones relativas porque son "vecinos" dentro de BackEnd
from .consulta import insertar_lectura
from .notification_service import enviar_alerta_por_correo

ID_CIRCUITO_A_SIMULAR = 1
UMBRAL_ALERTA_POTENCIA = 480000.0

print("--- Iniciando Recolector de Datos (con alertas) ---")
print(f"Guardando datos para el circuito ID: {ID_CIRCUITO_A_SIMULAR}")
print("Presiona CTRL+C para detener.")

while True:
    try:
        potencia_simulada = random.uniform(150000.0, 500000.0)

        insertar_lectura(ID_CIRCUITO_A_SIMULAR, potencia_simulada)  # pylint: disable=no-value-for-parameter
        
        print(f"Lectura guardada: {potencia_simulada:.2f} W")

        # --- Lógica de Alerta ---
        if potencia_simulada > UMBRAL_ALERTA_POTENCIA:
            print(f"¡ALERTA! Potencia ({potencia_simulada:.2f} W) superó el umbral de {UMBRAL_ALERTA_POTENCIA} W.")
            asunto = "ALERTA CRÍTICA: Sobrecarga de Potencia Detectada"
            cuerpo = (f"Se ha detectado un pico de consumo de {potencia_simulada:.2f} W en el circuito principal.\n\n"
                      f"Este valor supera el umbral de seguridad establecido en {UMBRAL_ALERTA_POTENCIA} W.\n\n"
                      "Se recomienda revisar los equipos conectados de inmediato.\n\n"
                      "-- Sistema Automático de Monitoreo de Energía --")
            enviar_alerta_por_correo(asunto, cuerpo)

        time.sleep(10)

    except KeyboardInterrupt:
        print("\nDeteniendo el recolector.")
        break
    except Exception as e:
        print(f"Error en el bucle del recolector: {e}")
        time.sleep(30)