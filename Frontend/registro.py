import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from PIL import Image

# Mapa para encontrar la carpeta 'BackEnd'
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

from BackEnd.consulta import registrar_usuario

# --- Paleta de Colores ---
COLOR_FONDO_MAIN = "#2c3e50"
COLOR_PANEL_DERECHO = "#ffffff"
COLOR_TEXTO_OSCURO = "#333333"
COLOR_BOTON_PRIMARIO = "#FFEB00"
COLOR_BOTON_HOVER = "#FFD700"
COLOR_INPUT_FONDO = "#f0f0f0"
COLOR_BORDE = "#cccccc"
COLOR_PLACEHOLDER = "#8a8a8a"

class RegistroView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")
        self.grid_rowconfigure(0, weight=1)

        # --- Panel Izquierdo ---
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

        # --- Panel Derecho ---
        self.panel_derecho = ctk.CTkFrame(self, fg_color=COLOR_PANEL_DERECHO)
        self.panel_derecho.grid(row=0, column=1, sticky="nsew")
        
        self.form_frame = ctk.CTkFrame(self.panel_derecho, fg_color="transparent")
        self.form_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.form_frame, text="Crear Nuevo Usuario", font=ctk.CTkFont(size=24, weight="bold"), text_color=COLOR_TEXTO_OSCURO).pack(pady=(0, 20))
        
        self.entry_usuario = ctk.CTkEntry(self.form_frame, placeholder_text="Nombre de Usuario", width=280, height=40, corner_radius=10,
                                          fg_color=COLOR_INPUT_FONDO, text_color=COLOR_TEXTO_OSCURO, border_color=COLOR_BORDE)
        self.entry_usuario.pack(pady=8)
        
        self.entry_pass = ctk.CTkEntry(self.form_frame, placeholder_text="Contraseña", show="*", width=280, height=40, corner_radius=10,
                                       fg_color=COLOR_INPUT_FONDO, text_color=COLOR_TEXTO_OSCURO, border_color=COLOR_BORDE)
        self.entry_pass.pack(pady=8)

        self.entry_nombre = ctk.CTkEntry(self.form_frame, placeholder_text="Nombre Completo", width=280, height=40, corner_radius=10,
                                         fg_color=COLOR_INPUT_FONDO, text_color=COLOR_TEXTO_OSCURO, border_color=COLOR_BORDE)
        self.entry_nombre.pack(pady=8)
        
        self.entry_email = ctk.CTkEntry(self.form_frame, placeholder_text="Email", width=280, height=40, corner_radius=10,
                                        fg_color=COLOR_INPUT_FONDO, text_color=COLOR_TEXTO_OSCURO, border_color=COLOR_BORDE)
        self.entry_email.pack(pady=8)

        self.roles_validos = ["Admin", "Empleado"]
        self.placeholder = "Seleccionar rol"
        self.rol_seleccionado = ctk.StringVar(value=self.placeholder)
        
        self.rol_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.rol_seleccionado, 
                                          values=self.roles_validos,
                                          command=self._on_rol_select,
                                          width=280, height=40, corner_radius=10,
                                          fg_color=COLOR_INPUT_FONDO, button_color=COLOR_INPUT_FONDO,
                                          button_hover_color="#e0e0e0", text_color=COLOR_PLACEHOLDER,
                                          dropdown_fg_color=COLOR_INPUT_FONDO, dropdown_hover_color="#e0e0e0",
                                          dropdown_text_color=COLOR_TEXTO_OSCURO,
                                          font=ctk.CTkFont(size=13)) 
        self.rol_menu.pack(pady=8)

        self.btn_registrar = ctk.CTkButton(self.form_frame, text="Registrar Usuario", command=self.registrar,
                                      width=280, height=45, corner_radius=10,
                                      font=ctk.CTkFont(size=16, weight="bold"),
                                      fg_color=COLOR_BOTON_PRIMARIO, hover_color=COLOR_BOTON_HOVER, text_color="#000000")
        self.btn_registrar.pack(pady=(20, 10))

        volver_btn = ctk.CTkButton(self.form_frame, text="Volver al Login",
                                   command=lambda: self.controller.mostrar_frame("LoginView"),
                                   font=ctk.CTkFont(size=12, underline=True), 
                                   fg_color="transparent", 
                                   text_color="#7f8c8d", 
                                   hover=False)
        volver_btn.pack(pady=10)

    # --- Limpieza de campos ---
    def limpiar_campos(self):
        self.entry_usuario.delete(0, "end")
        self.entry_pass.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.rol_seleccionado.set(self.placeholder)
        self.rol_menu.configure(text_color=COLOR_PLACEHOLDER)

    def _on_rol_select(self, choice):
        if choice in self.roles_validos:
            self.rol_menu.configure(text_color=COLOR_TEXTO_OSCURO)

    def registrar(self):
        usuario = self.entry_usuario.get()
        password = self.entry_pass.get()
        nombre = self.entry_nombre.get()
        email = self.entry_email.get()
        rol = self.rol_seleccionado.get()

        if rol == self.placeholder:
            messagebox.showerror("Error de Validación", "Por favor, selecciona un rol válido.")
            return

        if not all([usuario, password, nombre, email]):
            messagebox.showerror("Error de Validación", "Todos los campos son obligatorios.")
            return

        exito, mensaje = registrar_usuario(usuario, password, nombre, email, rol) # pylint: disable=no-value-for-parameter

        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.limpiar_campos()
            self.controller.mostrar_frame("LoginView")
        else:
            messagebox.showerror("Error de Registro", mensaje)
