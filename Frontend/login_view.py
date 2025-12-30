import customtkinter as ctk
from tkinter import messagebox
import os
import sys
from PIL import Image

def resource_path(relative_path):
    
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
imagen_fondo = Image.open(resource_path("Frontend/assets/fn_mudad_fondo.png")) 

# --- Mapa para encontrar la carpeta 'BackEnd' ---
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

# Intentar importar verificar_usuario con manejo de errores
try:
    from BackEnd.consulta import verificar_usuario
except Exception as e:
    import traceback
    print("\n ERROR al importar 'verificar_usuario' desde BackEnd.consulta ")
    traceback.print_exc()
    verificar_usuario = None  # Evita que la app se rompa


# --- Paleta de Colores ---
COLOR_FONDO_MAIN = "#2c3e50"
COLOR_PANEL_DERECHO = "#ffffff"
COLOR_TEXTO_OSCURO = "#333333"
COLOR_BOTON_PRIMARIO = "#8e44ad"
COLOR_BOTON_HOVER = "#9b59b6"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class LoginView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Configuración del layout
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")
        self.grid_rowconfigure(0, weight=1)

        # --- Panel Izquierdo ---
        self.panel_izquierdo = ctk.CTkFrame(self, fg_color=COLOR_FONDO_MAIN, corner_radius=0)
        self.panel_izquierdo.grid(row=0, column=0, sticky="nsew")

        # --- Panel Derecho ---
        self.panel_derecho = ctk.CTkFrame(self, fg_color=COLOR_PANEL_DERECHO)
        self.panel_derecho.grid(row=0, column=1, sticky="nsew")

        # --- Imagen de fondo ---
        script_dir = os.path.dirname(__file__)
        fondo_path = os.path.join(script_dir, "assets", "fn_mudad_fondo.png")
        color_btn_primario = "#FFEB00"
        color_btn_hover = "#FFD700"

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
            print(f"⚠️ Error al cargar imagen de fondo: {e}")

        # --- Formulario ---
        form_frame = ctk.CTkFrame(self.panel_derecho, fg_color="transparent")
        form_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(form_frame, text="Bienvenido", font=ctk.CTkFont(size=24, weight="bold"), text_color=COLOR_TEXTO_OSCURO).pack(pady=(0, 5))
        ctk.CTkLabel(form_frame, text="Inicia sesión en tu cuenta", font=ctk.CTkFont(size=14), text_color=COLOR_TEXTO_OSCURO).pack(pady=(0, 30))

        # --- Iconos ---
        try:
            self.email_icon = ctk.CTkImage(Image.open(os.path.join(script_dir, "assets", "email_icon.png")), size=(20, 20))
            self.password_icon = ctk.CTkImage(Image.open(os.path.join(script_dir, "assets", "password_icon.png")), size=(20, 20))
        except Exception as e:
            print(f"⚠️ Error al cargar íconos: {e}")
            self.email_icon = self.password_icon = None

        # Campo usuario
        frame_usuario = ctk.CTkFrame(form_frame, fg_color="transparent")
        frame_usuario.pack(pady=5, padx=0, fill="x")
        if self.email_icon:
            ctk.CTkLabel(frame_usuario, image=self.email_icon, text="").pack(side="left", padx=(0, 10))
        self.entry_usuario = ctk.CTkEntry(frame_usuario, placeholder_text="Tu usuario", height=40, corner_radius=10, fg_color="#f0f0f0", text_color=COLOR_TEXTO_OSCURO, border_color="#cccccc")
        self.entry_usuario.pack(side="left", fill="x", expand=True)

        # Campo contraseña
        frame_password = ctk.CTkFrame(form_frame, fg_color="transparent")
        frame_password.pack(pady=(20, 5), padx=0, fill="x")
        if self.password_icon:
            ctk.CTkLabel(frame_password, image=self.password_icon, text="").pack(side="left", padx=(0, 10))
        self.entry_pass = ctk.CTkEntry(frame_password, placeholder_text="Tu contraseña", show="*", height=40, corner_radius=10, fg_color="#f0f0f0", text_color=COLOR_TEXTO_OSCURO, border_color="#cccccc")
        self.entry_pass.pack(side="left", fill="x", expand=True)

        # Botón recuperar contraseña
        ctk.CTkButton(form_frame, text="¿Olvidaste tu contraseña?",
                      command=lambda: self.controller.mostrar_frame("PasswordResetView"),
                      font=ctk.CTkFont(size=12, underline=True),
                      fg_color="transparent", text_color="#7f8c8d", hover=False).pack(anchor="center", pady=(5, 0))

        # Botón ingresar
        ctk.CTkButton(form_frame, text="Ingresar", command=self.login, width=250, height=45, corner_radius=10,
                      font=ctk.CTkFont(size=16, weight="bold"), fg_color=color_btn_primario,
                      hover_color=color_btn_hover, text_color="#000000").pack(pady=(30, 15))

        # Botón registro
        ctk.CTkButton(form_frame, text="¿No tienes una cuenta? Regístrate aquí",
                      command=lambda: self.controller.mostrar_frame("RegistroView"),
                      font=ctk.CTkFont(size=12, underline=True),
                      fg_color="transparent", text_color="#7f8c8d", hover=False).pack(pady=(10, 20))

    def login(self):
        usuario = self.entry_usuario.get()
        password = self.entry_pass.get()

        if not usuario or not password:
            messagebox.showwarning("Campos vacíos", "Por favor ingresa tu usuario y contraseña.")
            return

        if not verificar_usuario:
            messagebox.showerror("Error interno", "No se pudo acceder al módulo de verificación de usuario.")
            return

        rol = verificar_usuario(usuario, password)
        if rol:
            self.controller.login_exitoso(rol)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    def limpiar_campos(self):
        """Limpia los campos de texto y fuerza la reaparición de los placeholders."""
        self.entry_usuario.delete(0, "end")
        self.entry_pass.delete(0, "end")
        
        # --- ESTA ES LA LÍNEA CLAVE ---
        # Enfocamos el botón de login (o cualquier otro widget que no sea un entry)
        # Esto hace que los campos de texto pierdan el foco y muestren el placeholder.
        self.focus_set()