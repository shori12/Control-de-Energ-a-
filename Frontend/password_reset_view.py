import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from PIL import Image

# Mapa para encontrar la carpeta 'BackEnd'
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

from BackEnd.consulta import generar_token_reseteo, resetear_password_con_token
from BackEnd.notification_service import enviar_alerta_por_correo

# --- Paleta de Colores ---
COLOR_FONDO_MAIN = "#2c3e50"
COLOR_PANEL_DERECHO = "#ffffff"
COLOR_TEXTO_OSCURO = "#333333"
COLOR_BOTON_PRIMARIO = "#FFEB00"  # Amarillo
COLOR_BOTON_HOVER = "#FFD700"
COLOR_INPUT_FONDO = "#f0f0f0"
COLOR_BORDE = "#cccccc"
COLOR_ROJO = "#e74c3c"
COLOR_PLACEHOLDER = "#8a8a8a"

class PasswordResetView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")
        self.grid_rowconfigure(0, weight=1)

        # --- Panel Izquierdo con imagen ---
        self.panel_izquierdo = ctk.CTkFrame(self, fg_color=COLOR_FONDO_MAIN, corner_radius=0)
        self.panel_izquierdo.grid(row=0, column=0, sticky="nsew")
        
        script_dir = os.path.dirname(__file__)
        fondo_path = os.path.join(script_dir, "assets", "fn_mudad_fondo.png")
        try:
            original_image = Image.open(fondo_path)
            target_width, target_height = 400, 600
            img_width, img_height = original_image.size
            scale = max(target_width / img_width, target_height / img_height)
            new_width, new_height = int(img_width * scale), int(img_height * scale)
            resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            x_offset, y_offset = (new_width - target_width) // 2, (new_height - target_height) // 2
            cropped_image = resized_image.crop((x_offset, y_offset, x_offset + target_width, y_offset + target_height))
            self.fondo_mudad_image = ctk.CTkImage(light_image=cropped_image, dark_image=cropped_image, size=(target_width, target_height))
            fondo_label = ctk.CTkLabel(self.panel_izquierdo, image=self.fondo_mudad_image, text="")
            fondo_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error al cargar imagen de fondo: {e}")

        # --- Panel Derecho con formulario ---
        self.panel_derecho = ctk.CTkFrame(self, fg_color=COLOR_PANEL_DERECHO)
        self.panel_derecho.grid(row=0, column=1, sticky="nsew")
        
        self.main_frame = ctk.CTkFrame(self.panel_derecho, fg_color="transparent")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Inicialmente mostramos la fase 1
        self.mostrar_fase_1_pedir_email()

    def limpiar_frame(self):
        """Elimina todos los widgets del frame principal para cambiar de fase."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def mostrar_fase_1_pedir_email(self):
        """Muestra la interfaz para que el usuario ingrese su email."""
        self.limpiar_frame()
        
        ctk.CTkLabel(self.main_frame, text="Recuperar Contraseña", font=ctk.CTkFont(size=24, weight="bold"), text_color=COLOR_TEXTO_OSCURO).pack(pady=10)
        ctk.CTkLabel(self.main_frame, text="Ingresa tu correo para recibir un código.", wraplength=300, text_color=COLOR_TEXTO_OSCURO, font=ctk.CTkFont(size=14)).pack(pady=10)
        
        self.entry_email = ctk.CTkEntry(
            self.main_frame, placeholder_text="tu.correo@ejemplo.com",
            width=300, height=40, corner_radius=10, fg_color=COLOR_INPUT_FONDO,
            text_color=COLOR_TEXTO_OSCURO, border_color=COLOR_BORDE
        )
        self.entry_email.pack(pady=20)
        
        ctk.CTkButton(
            self.main_frame, text="Enviar Código", command=self.enviar_codigo,
            width=300, height=40, corner_radius=10, font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_BOTON_PRIMARIO, hover_color=COLOR_BOTON_HOVER, text_color="#000000"
        ).pack(pady=10)
        ctk.CTkButton(
            self.main_frame, text="Volver al Login", fg_color="transparent",
            text_color="#7f8c8d", hover=False, font=ctk.CTkFont(size=12, underline=True),
            command=lambda: self.controller.mostrar_frame("LoginView")
        ).pack(pady=10)

    def enviar_codigo(self):
        email = self.entry_email.get()
        if not email:
            messagebox.showerror("Error", "Por favor, ingresa un correo electrónico.")
            return

        token, mensaje = generar_token_reseteo(email)  # pylint: disable=no-value-for-parameter

        if token:
            asunto = "Código de Recuperación de Contraseña - FN MUDAD"
            cuerpo = f"Has solicitado recuperar tu contraseña.\n\nTu código de verificación es:\n\n{token}\n\nEste código expirará en 15 minutos."
            
            correo_enviado = enviar_alerta_por_correo(asunto, cuerpo)
            
            if correo_enviado:
                messagebox.showinfo("Correo Enviado", "Se ha enviado un código a tu correo. Revisa tu bandeja de entrada (y la carpeta de spam).")
                self.mostrar_fase_2_ingresar_codigo()
            else:
                messagebox.showerror("Error de Envío", "No se pudo enviar el correo. Revisa la configuración o inténtalo más tarde.")
        else:
            messagebox.showerror("Error", mensaje)

    def mostrar_fase_2_ingresar_codigo(self):
        """Muestra la interfaz para ingresar el código y la nueva contraseña."""
        self.limpiar_frame()
        
        ctk.CTkLabel(self.main_frame, text="Restablecer Contraseña", font=ctk.CTkFont(size=24, weight="bold"), text_color=COLOR_TEXTO_OSCURO).pack(pady=10)
        
        self.entry_token = ctk.CTkEntry(
            self.main_frame, placeholder_text="Pega aquí el código de 6 dígitos",
            width=300, height=40, corner_radius=10, fg_color=COLOR_INPUT_FONDO,
            text_color=COLOR_TEXTO_OSCURO, border_color=COLOR_BORDE
        )
        self.entry_token.pack(pady=10)

        self.entry_new_pass = ctk.CTkEntry(
            self.main_frame, placeholder_text="Nueva Contraseña", show="*",
            width=300, height=40, corner_radius=10, fg_color=COLOR_INPUT_FONDO,
            text_color=COLOR_TEXTO_OSCURO, border_color=COLOR_BORDE
        )
        self.entry_new_pass.pack(pady=10)

        ctk.CTkButton(
            self.main_frame, text="Cambiar Contraseña", command=self.cambiar_password,
            width=300, height=40, corner_radius=10, font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_BOTON_PRIMARIO, hover_color=COLOR_BOTON_HOVER, text_color="#000000"
        ).pack(pady=20)
        ctk.CTkButton(
            self.main_frame, text="Volver al Login", fg_color="transparent", text_color="#7f8c8d",
            hover=False, font=ctk.CTkFont(size=12, underline=True),
            command=lambda: self.controller.mostrar_frame("LoginView")
        ).pack(pady=10)

    def cambiar_password(self):
        token = self.entry_token.get()
        nueva_pass = self.entry_new_pass.get()

        if not token or not nueva_pass:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        exito, mensaje = resetear_password_con_token(token, nueva_pass)  # pylint: disable=no-value-for-parameter
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            # Limpiamos todo y volvemos a la fase 1 para que no quede nada
            self.mostrar_fase_1_pedir_email()
            self.controller.mostrar_frame("LoginView")
        else:
            messagebox.showerror("Error", mensaje)
