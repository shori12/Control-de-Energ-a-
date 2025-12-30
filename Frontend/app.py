import customtkinter as ctk
import sys
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from tkinter import messagebox, filedialog
from datetime import datetime
import calendar
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Mapa para encontrar la carpeta 'BackEnd'
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

from BackEnd.consulta import obtener_ultima_lectura, obtener_lecturas_para_grafico

# --- Paleta de colores mejorada ---
COLOR_FONDO_MAIN       = "#1e293b"
COLOR_PANEL_DERECHO    = "#ffffff"
COLOR_PANEL            = "#34495e"
COLOR_TEXTO_OSCURO     = "#1e293b"
COLOR_TEXTO            = "#ffffff"
COLOR_BOTON_PRIMARIO   = "#8e44ad"
COLOR_BOTON_HOVER      = "#9b59b6"
COLOR_VERDE_PASTEL     = "#27ae60"
COLOR_ALERTA_ALTA      = "#e74c3c"
COLOR_ALERTA_BAJA      = "#3498db"
COLOR_BORDE            = "#e2e8f0"
COLOR_DESTACADO        = "#f1c40f"
COLOR_LOGOUT           = "#dc2626"


# ===================================
# SISTEMA DE PERMISOS POR ROL
# ===================================

class PermisosRol:
    """Clase centralizada para gestionar permisos según rol"""

    PERMISOS = {
        'Admin': {
            'visualizar_dashboard': True,
            'visualizar_graficos': True,
            'visualizar_reportes': True,
            'modificar_datos': True,
            'agregar_datos': True,
            'eliminar_datos': True,
            'gestionar_alertas': True,
            'gestionar_usuarios': True,
            'exportar_datos': True,
            'configuracion_sistema': True
        },
        'Empleado': {
            'visualizar_dashboard': True,
            'visualizar_graficos': True,
            'visualizar_reportes': True,
            'modificar_datos': False,
            'agregar_datos': True,
            'eliminar_datos': False,
            'gestionar_alertas': True,
            'gestionar_usuarios': False,
            'exportar_datos': True,
            'configuracion_sistema': True
        }
    }

    @classmethod
    def puede(cls, rol, accion):
        """Verifica si un rol tiene permiso para realizar una acción"""
        return cls.PERMISOS.get(rol, {}).get(accion, False)

    @classmethod
    def obtener_permisos(cls, rol):
        """Retorna todos los permisos de un rol"""
        return cls.PERMISOS.get(rol, {})


# ===================================
# MODAL GESTIÓN DE USUARIOS (ADMIN)
# ===================================

class ModalGestionUsuarios(ctk.CTkToplevel):
    """Modal para gestionar usuarios - Solo Admin"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gestión de Usuarios")
        self.geometry("900x700")
        self.configure(fg_color=COLOR_FONDO_MAIN)
        self.resizable(False, False)

        # Centrar ventana
        self.update_idletasks()
        self.x = (self.winfo_screenwidth() // 2) - (900 // 2)
        self.y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"900x700+{self.x}+{self.y}")
        self.transient(parent)
        self.grab_set()

        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL_DERECHO, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)

        # Título
        ctk.CTkLabel(
            main_frame,
            text="Gestión de Usuarios del Sistema",
            font=("Helvetica", 24, "bold"),
            text_color=COLOR_BOTON_PRIMARIO
        ).pack(pady=(20, 15))

        # Botones de acción
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkButton(
            btn_frame,
            text="Agregar Usuario",
            fg_color=COLOR_VERDE_PASTEL,
            hover_color="#229954",
            height=45,
            corner_radius=10,
            font=("Helvetica", 13, "bold"),
            command=self.abrir_modal_agregar_usuario
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Actualizar Lista",
            fg_color=COLOR_BOTON_PRIMARIO,
            hover_color=COLOR_BOTON_HOVER,
            height=45,
            corner_radius=10,
            font=("Helvetica", 13, "bold"),
            command=self.cargar_usuarios
        ).pack(side="left", padx=5)

        # Frame scrollable para lista de usuarios
        self.scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="white",
            corner_radius=10,
            height=450
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Botón cerrar
        ctk.CTkButton(
            main_frame,
            text="Cerrar",
            fg_color="#6b7280",
            hover_color="#4b5563",
            height=45,
            corner_radius=10,
            font=("Helvetica", 13, "bold"),
            command=self.destroy
        ).pack(pady=(0, 20), padx=20, fill="x")

        # Cargar usuarios
        self.cargar_usuarios()

        # Animación de entrada
        self.attributes('-alpha', 0.0)
        self.animar_entrada()

    def animar_entrada(self):
        alpha = self.attributes('-alpha')
        if alpha < 1.0:
            self.attributes('-alpha', alpha + 0.1)
            self.after(15, self.animar_entrada)

    def cargar_usuarios(self):
        """Carga la lista de usuarios (simulado con datos de ejemplo)"""
        # Limpiar frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Datos de ejemplo - REEMPLAZAR con consulta a BD
        usuarios_ejemplo = [
            {'id': 1, 'usuario': 'admin', 'nombre': 'Administrador', 'rol': 'Admin', 'estado': 'Activo'},
            {'id': 2, 'usuario': 'gerente1', 'nombre': 'Carlos Pérez', 'rol': 'Gerente', 'estado': 'Activo'},
            {'id': 3, 'usuario': 'empleado1', 'nombre': 'Ana García', 'rol': 'Empleado', 'estado': 'Activo'},
            {'id': 4, 'usuario': 'empleado2', 'nombre': 'Luis Martínez', 'rol': 'Empleado', 'estado': 'Inactivo'}
        ]

        for usuario in usuarios_ejemplo:
            self.crear_card_usuario(usuario)

    def crear_card_usuario(self, usuario):
        """Crea una tarjeta visual para cada usuario"""
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#f8f9fa",
            corner_radius=10,
            border_width=2,
            border_color=COLOR_VERDE_PASTEL if usuario['estado'] == 'Activo' else "#dc2626"
        )
        card.pack(fill="x", pady=8, padx=10)

        # Header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10, 5))

        icono_rol = {"Admin": "🛡️", "Gerente": "👔", "Empleado": "👤"}.get(usuario['rol'], "👤")

        ctk.CTkLabel(
            header,
            text=f"{icono_rol} {usuario['nombre']}",
            text_color=COLOR_TEXTO_OSCURO,
            font=("Helvetica", 14, "bold")
        ).pack(side="left")

        estado_color = COLOR_VERDE_PASTEL if usuario['estado'] == 'Activo' else "#dc2626"
        ctk.CTkLabel(
            header,
            text=usuario['estado'],
            text_color=estado_color,
            font=("Helvetica", 11, "bold")
        ).pack(side="right")

        # Detalles
        detalle_text = f"Usuario: {usuario['usuario']}  |  Rol: {usuario['rol']}  |  ID: {usuario['id']}"
        ctk.CTkLabel(
            card,
            text=detalle_text,
            text_color="#6b7280",
            font=("Consolas", 10)
        ).pack(padx=15, pady=(0, 5))

        # Botones de acción
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(5, 10))

        ctk.CTkButton(
            btn_frame,
            text="Editar",
            fg_color=COLOR_BOTON_PRIMARIO,
            hover_color=COLOR_BOTON_HOVER,
            width=100,
            height=32,
            corner_radius=8,
            font=("Helvetica", 10, "bold"),
            command=lambda u=usuario: self.editar_usuario(u)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Eliminar",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            width=100,
            height=32,
            corner_radius=8,
            font=("Helvetica", 10, "bold"),
            command=lambda u=usuario: self.eliminar_usuario(u)
        ).pack(side="left", padx=5)

        if usuario['estado'] == 'Activo':
            ctk.CTkButton(
                btn_frame,
                text="Desactivar",
                fg_color="#f59e0b",
                hover_color="#d97706",
                width=110,
                height=32,
                corner_radius=8,
                font=("Helvetica", 10, "bold"),
                command=lambda u=usuario: self.cambiar_estado_usuario(u)
            ).pack(side="left", padx=5)
        else:
            ctk.CTkButton(
                btn_frame,
                text="Activar",
                fg_color=COLOR_VERDE_PASTEL,
                hover_color="#229954",
                width=110,
                height=32,
                corner_radius=8,
                font=("Helvetica", 10, "bold"),
                command=lambda u=usuario: self.cambiar_estado_usuario(u)
            ).pack(side="left", padx=5)

    def abrir_modal_agregar_usuario(self):
        """Abre modal para agregar nuevo usuario"""
        ModalAgregarUsuario(self, callback=self.cargar_usuarios)

    def editar_usuario(self, usuario):
        """Edita un usuario existente"""
        ModalEditarUsuario(self, usuario, callback=self.cargar_usuarios)

    def eliminar_usuario(self, usuario):
        """Elimina un usuario del sistema"""
        respuesta = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar al usuario?\n\n"
            f"{usuario['nombre']}\n"
            f"ID: {usuario['id']}\n\n"
            f"Esta acción no se puede deshacer.",
            parent=self
        )

        if respuesta:
            # Aquí iría la lógica para eliminar de la BD
            messagebox.showinfo(
                "Usuario Eliminado",
                f"El usuario '{usuario['usuario']}' ha sido eliminado del sistema.",
                parent=self
            )
            self.cargar_usuarios()

    def cambiar_estado_usuario(self, usuario):
        """Activa o desactiva un usuario"""
        nuevo_estado = "Inactivo" if usuario['estado'] == "Activo" else "Activo"
        accion = "desactivar" if nuevo_estado == "Inactivo" else "activar"

        respuesta = messagebox.askyesno(
            "Cambiar Estado",
            f"¿Deseas {accion} al usuario '{usuario['usuario']}'?",
            parent=self
        )

        if respuesta:
            # Aquí iría la lógica para actualizar en BD
            messagebox.showinfo(
                "Estado Actualizado",
                f"Usuario '{usuario['usuario']}' ahora está {nuevo_estado}.",
                parent=self
            )
            self.cargar_usuarios()


class ModalAgregarUsuario(ctk.CTkToplevel):
    """Modal para agregar nuevo usuario"""
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.title("Agregar Usuario")
        self.geometry("600x700")
        self.configure(fg_color=COLOR_FONDO_MAIN)
        self.resizable(False, False)

        # Centrar
        self.update_idletasks()
        self.x = (self.winfo_screenwidth() // 2) - (600 // 2)
        self.y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"600x700+{self.x}+{self.y}")
        self.transient(parent)
        self.grab_set()

        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL_DERECHO, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(
            main_frame,
            text="Crear Nuevo Usuario",
            font=("Helvetica", 24, "bold"),
            text_color=COLOR_BOTON_PRIMARIO
        ).pack(pady=(25, 35))

        campos_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        campos_frame.pack(fill="both", expand=True, padx=40)

        # Campos
        ctk.CTkLabel(campos_frame, text="Nombre Completo:", text_color=COLOR_TEXTO_OSCURO, font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 10))
        self.entry_nombre = ctk.CTkEntry(campos_frame, height=50, fg_color="#f8f9fa", border_color=COLOR_BOTON_PRIMARIO, border_width=2, corner_radius=10, font=("Helvetica", 14), text_color=COLOR_TEXTO_OSCURO, placeholder_text="Ej: Juan Pérez")
        self.entry_nombre.pack(fill="x", pady=(0, 22))

        ctk.CTkLabel(campos_frame, text="Usuario:", text_color=COLOR_TEXTO_OSCURO, font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 10))
        self.entry_usuario = ctk.CTkEntry(campos_frame, height=50, fg_color="#f8f9fa", border_color=COLOR_BOTON_PRIMARIO, border_width=2, corner_radius=10, font=("Helvetica", 14), text_color=COLOR_TEXTO_OSCURO, placeholder_text="Ej: jperez")
        self.entry_usuario.pack(fill="x", pady=(0, 22))

        ctk.CTkLabel(campos_frame, text="Contraseña:", text_color=COLOR_TEXTO_OSCURO, font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 10))
        self.entry_password = ctk.CTkEntry(campos_frame, height=50, fg_color="#f8f9fa", border_color=COLOR_BOTON_PRIMARIO, border_width=2, corner_radius=10, font=("Helvetica", 14), text_color=COLOR_TEXTO_OSCURO, placeholder_text="••••••••", show="•")
        self.entry_password.pack(fill="x", pady=(0, 22))

        ctk.CTkLabel(campos_frame, text="Rol:", text_color=COLOR_TEXTO_OSCURO, font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 10))
        self.combo_rol = ctk.CTkComboBox(campos_frame, values=["Admin", "Gerente", "Empleado"], height=50, fg_color="#f8f9fa", border_color=COLOR_BOTON_PRIMARIO, border_width=2, corner_radius=10, font=("Helvetica", 14), text_color=COLOR_TEXTO_OSCURO, state="readonly")
        self.combo_rol.set("Empleado")
        self.combo_rol.pack(fill="x", pady=(0, 25))

        # Botones
        botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botones_frame.pack(fill="x", padx=40, pady=(10, 30))
        botones_frame.columnconfigure((0, 1), weight=1)

        ctk.CTkButton(botones_frame, text="Cancelar", fg_color="#6b7280", hover_color="#4b5563", height=55, corner_radius=10, font=("Helvetica", 13, "bold"), command=self.destroy).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(botones_frame, text="Crear Usuario", fg_color=COLOR_VERDE_PASTEL, hover_color="#229954", height=55, corner_radius=10, font=("Helvetica", 13, "bold"), command=self.guardar_usuario).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.attributes('-alpha', 0.0)
        self.animar_entrada()

    def animar_entrada(self):
        alpha = self.attributes('-alpha')
        if alpha < 1.0:
            self.attributes('-alpha', alpha + 0.1)
            self.after(15, self.animar_entrada)

    def guardar_usuario(self):
        """Guarda el nuevo usuario"""
        if not all([self.entry_nombre.get(), self.entry_usuario.get(), self.entry_password.get()]):
            messagebox.showerror("Error", "Todos los campos son obligatorios", parent=self)
            return

        # Aquí iría la lógica para guardar en BD
        messagebox.showinfo(
            "Usuario Creado",
            f"Usuario '{self.entry_usuario.get()}' creado exitosamente\n\n"
            f"Nombre: {self.entry_nombre.get()}\n"
            f"Rol: {self.combo_rol.get()}",
            parent=self
        )

        if self.callback:
            self.callback()
        self.destroy()


class ModalEditarUsuario(ctk.CTkToplevel):
    """Modal para editar usuario existente"""
    def __init__(self, parent, usuario, callback=None):
        super().__init__(parent)
        self.usuario = usuario
        self.callback = callback
        self.title("Editar Usuario")
        self.geometry("600x650")
        self.configure(fg_color=COLOR_FONDO_MAIN)
        self.resizable(False, False)

        # Centrar
        self.update_idletasks()
        self.x = (self.winfo_screenwidth() // 2) - (600 // 2)
        self.y = (self.winfo_screenheight() // 2) - (650 // 2)
        self.geometry(f"600x650+{self.x}+{self.y}")
        self.transient(parent)
        self.grab_set()

        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL_DERECHO, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(
            main_frame,
            text=f"Editar Usuario: {usuario['usuario']}",
            font=("Helvetica", 22, "bold"),
            text_color=COLOR_BOTON_PRIMARIO
        ).pack(pady=(25, 35))

        campos_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        campos_frame.pack(fill="both", expand=True, padx=40)

        # Campos pre-llenados
        ctk.CTkLabel(campos_frame, text="Nombre Completo:", text_color=COLOR_TEXTO_OSCURO, font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 10))
        self.entry_nombre = ctk.CTkEntry(campos_frame, height=50, fg_color="#f8f9fa", border_color=COLOR_BOTON_PRIMARIO, border_width=2, corner_radius=10, font=("Helvetica", 14), text_color=COLOR_TEXTO_OSCURO)
        self.entry_nombre.insert(0, usuario['nombre'])
        self.entry_nombre.pack(fill="x", pady=(0, 22))

        ctk.CTkLabel(campos_frame, text="Nueva Contraseña (dejar vacío para no cambiar):", text_color=COLOR_TEXTO_OSCURO, font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 10))
        self.entry_password = ctk.CTkEntry(campos_frame, height=50, fg_color="#f8f9fa", border_color=COLOR_BOTON_PRIMARIO, border_width=2, corner_radius=10, font=("Helvetica", 14), text_color=COLOR_TEXTO_OSCURO, placeholder_text="••••••••", show="•")
        self.entry_password.pack(fill="x", pady=(0, 22))

        ctk.CTkLabel(campos_frame, text="Rol:", text_color=COLOR_TEXTO_OSCURO, font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 10))
        self.combo_rol = ctk.CTkComboBox(campos_frame, values=["Admin", "Gerente", "Empleado"], height=50, fg_color="#f8f9fa", border_color=COLOR_BOTON_PRIMARIO, border_width=2, corner_radius=10, font=("Helvetica", 14), text_color=COLOR_TEXTO_OSCURO, state="readonly")
        self.combo_rol.set(usuario['rol'])
        self.combo_rol.pack(fill="x", pady=(0, 25))

        # Botones
        botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botones_frame.pack(fill="x", padx=40, pady=(10, 30))
        botones_frame.columnconfigure((0, 1), weight=1)

        ctk.CTkButton(botones_frame, text="Cancelar", fg_color="#6b7280", hover_color="#4b5563", height=55, corner_radius=10, font=("Helvetica", 13, "bold"), command=self.destroy).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(botones_frame, text="Guardar Cambios", fg_color=COLOR_VERDE_PASTEL, hover_color="#229954", height=55, corner_radius=10, font=("Helvetica", 13, "bold"), command=self.guardar_cambios).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.attributes('-alpha', 0.0)
        self.animar_entrada()

    def animar_entrada(self):
        alpha = self.attributes('-alpha')
        if alpha < 1.0:
            self.attributes('-alpha', alpha + 0.1)
            self.after(15, self.animar_entrada)

    def guardar_cambios(self):
        """Guarda los cambios del usuario"""
        if not self.entry_nombre.get():
            messagebox.showerror("Error", "El nombre no puede estar vacío", parent=self)
            return

        # Aquí iría la lógica para actualizar en BD
        messagebox.showinfo(
            "Cambios Guardados",
            f"Usuario '{self.usuario['usuario']}' actualizado exitosamente",
            parent=self
        )

        if self.callback:
            self.callback()
        self.destroy()


class ModalModificar(ctk.CTkToplevel):
    """Modal para modificar datos con animación de entrada"""
    def __init__(self, parent, callback_actualizar=None):
        super().__init__(parent)
        self.callback_actualizar = callback_actualizar
        self.title("Modificar Datos")
        self.geometry("600x600")
        self.configure(fg_color=COLOR_FONDO_MAIN)
        self.resizable(False, False)

        # Centrar la ventana
        self.update_idletasks()
        self.x = (self.winfo_screenwidth() // 2) - (600 // 2)
        self.y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"600x600+{self.x}+{self.y}")
        self.transient(parent)
        self.grab_set()

        # Frame principal con mejor diseño
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL_DERECHO, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)

        # Título con ícono
        ctk.CTkLabel(
            main_frame,
            text="Modificar Datos del Circuito",
            font=("Helvetica", 24, "bold"),
            text_color=COLOR_BOTON_PRIMARIO
        ).pack(pady=(25, 35))

        campos_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        campos_frame.pack(fill="both", expand=True, padx=40)

        # Campo ID Circuito
        ctk.CTkLabel(
            campos_frame,
            text="ID Circuito:",
            text_color=COLOR_TEXTO_OSCURO,
            font=("Helvetica", 15, "bold")
        ).pack(anchor="w", pady=(0, 10))
        self.entry_id = ctk.CTkEntry(
            campos_frame,
            height=50,
            fg_color="#f8f9fa",
            border_color=COLOR_BOTON_PRIMARIO,
            border_width=2,
            corner_radius=10,
            font=("Helvetica", 14),
            text_color=COLOR_TEXTO_OSCURO,
            placeholder_text="Ej: 1"
        )
        self.entry_id.pack(fill="x", pady=(0, 25))
        self.entry_id.bind("<KeyRelease>", lambda e: self.validar_entero(self.entry_id))

        # Campo Potencia
        ctk.CTkLabel(
            campos_frame,
            text="Nueva Potencia (W):",
            text_color=COLOR_TEXTO_OSCURO,
            font=("Helvetica", 15, "bold")
        ).pack(anchor="w", pady=(0, 10))
        self.entry_potencia = ctk.CTkEntry(
            campos_frame,
            height=50,
            fg_color="#f8f9fa",
            border_color=COLOR_BOTON_PRIMARIO,
            border_width=2,
            corner_radius=10,
            font=("Helvetica", 14),
            text_color=COLOR_TEXTO_OSCURO,
            placeholder_text="Ej: 500.75"
        )
        self.entry_potencia.pack(fill="x", pady=(0, 25))
        self.entry_potencia.bind("<KeyRelease>", lambda e: self.validar_decimal(self.entry_potencia))

        # Campo Fecha
        ctk.CTkLabel(
            campos_frame,
            text="Fecha/Hora (opcional):",
            text_color=COLOR_TEXTO_OSCURO,
            font=("Helvetica", 15, "bold")
        ).pack(anchor="w", pady=(0, 10))
        self.entry_fecha = ctk.CTkEntry(
            campos_frame,
            height=50,
            fg_color="#f8f9fa",
            border_color=COLOR_BOTON_PRIMARIO,
            border_width=2,
            corner_radius=10,
            placeholder_text="YYYY-MM-DD HH:MM:SS",
            font=("Helvetica", 14),
            text_color=COLOR_TEXTO_OSCURO
        )
        self.entry_fecha.pack(fill="x", pady=(0, 30))

        # Botones
        botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botones_frame.pack(fill="x", padx=40, pady=(0, 25))
        botones_frame.columnconfigure((0, 1), weight=1, uniform="botones")

        btn_cancelar = ctk.CTkButton(
            botones_frame,
            text="Cancelar",
            fg_color="#6b7280",
            hover_color="#4b5563",
            height=55,
            corner_radius=10,
            font=("Helvetica", 13, "bold"),
            command=self.destroy
        )
        btn_cancelar.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        btn_guardar = ctk.CTkButton(
            botones_frame,
            text="Guardar Cambios",
            fg_color=COLOR_VERDE_PASTEL,
            hover_color="#229954",
            height=55,
            corner_radius=10,
            font=("Helvetica", 13, "bold"),
            command=self.guardar_modificacion
        )
        btn_guardar.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.attributes('-alpha', 0.0)
        self.animar_entrada()

    def animar_entrada(self):
        alpha = self.attributes('-alpha')
        if alpha < 1.0:
            self.attributes('-alpha', alpha + 0.1)
            self.after(15, self.animar_entrada)

    def validar_entero(self, entry):
        valor = entry.get()
        if valor and not valor.isdigit():
            nuevo_valor = ''.join(filter(str.isdigit, valor))
            entry.delete(0, 'end')
            entry.insert(0, nuevo_valor)

    def validar_decimal(self, entry):
        valor = entry.get()
        if valor:
            partes = valor.split('.')
            if len(partes) > 2:
                entry.delete(0, 'end')
                entry.insert(0, '.'.join(partes[:-1]) + partes[-1])
            else:
                nuevo_valor = ''
                punto_usado = False
                for char in valor:
                    if char.isdigit():
                        nuevo_valor += char
                    elif char == '.' and not punto_usado:
                        nuevo_valor += char
                        punto_usado = True
                if nuevo_valor != valor:
                    entry.delete(0, 'end')
                    entry.insert(0, nuevo_valor)

    def guardar_modificacion(self):
        """Guarda las modificaciones en la base de datos"""
        try:
            if not self.entry_id.get() or not self.entry_potencia.get():
                messagebox.showerror("Error", "ID y Potencia son obligatorios")
                return

            id_circuito = int(self.entry_id.get())
            potencia = float(self.entry_potencia.get())
            fecha_str = self.entry_fecha.get().strip() if self.entry_fecha.get() else None

            # Validar formato de fecha si se proporciona
            if fecha_str:
                try:
                    datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    messagebox.showerror("Error", "Formato de fecha inválido.\nUse: YYYY-MM-DD HH:MM:SS")
                    return
            else:
                # Si no se provee fecha, usar la actual
                fecha_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Intentar guardar
            try:
                from BackEnd.consulta import modificar_lectura

                # Corrección: Enviar fecha para evitar error de argumentos
                exito = modificar_lectura(id_circuito, potencia, fecha_str) # pylint: disable=no-value-for-parameter

            except ImportError:
                messagebox.showerror("Error", "No se encontró el módulo BackEnd.consulta\n\n Verifique la instalación.")
                return
            except Exception as e:
                print(f"[ERROR GENERAL] {e}")
                messagebox.showerror("Error de Backend", f"Error al conectar con la base de datos:\n{str(e)}\n\n Verifique la conexión.")
                return

            if exito:
                messagebox.showinfo("Éxito", f"Datos modificados correctamente\n\n ID: {id_circuito}\n Potencia: {potencia:.2f}W")
                if self.callback_actualizar:
                    self.callback_actualizar()
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo modificar los datos.\nVerifique que el ID del circuito exista y tenga lecturas.")

        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")


class ModalAgregarDato(ctk.CTkToplevel):
    """Modal para agregar dato manual con animación"""
    def __init__(self, parent, callback_actualizar=None):
        super().__init__(parent)
        self.callback_actualizar = callback_actualizar

        self.title("Agregar Dato Manual")
        self.geometry("650x650")
        self.configure(fg_color=COLOR_FONDO_MAIN)
        self.resizable(False, False)

        # Centrar la ventana
        self.update_idletasks()
        self.x = (self.winfo_screenwidth() // 2) - (650 // 2)
        self.y = (self.winfo_screenheight() // 2) - (650 // 2)
        self.geometry(f"650x650+{self.x}+{self.y}")

        self.transient(parent)
        self.grab_set()

        # Panel principal
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL_DERECHO, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(
            main_frame,
            text="Agregar Lectura Manual",
            font=("Helvetica", 26, "bold"),
            text_color=COLOR_BOTON_PRIMARIO
        ).pack(pady=(25, 35))

        campos_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        campos_frame.pack(fill="both", expand=True, padx=40)

        # Campo ID Circuito
        ctk.CTkLabel(
            campos_frame,
            text="ID Circuito:",
            text_color=COLOR_TEXTO_OSCURO,
            font=("Helvetica", 16, "bold")
        ).pack(anchor="w", pady=(0, 10))
        self.entry_id = ctk.CTkEntry(
            campos_frame,
            height=55,
            fg_color="#f8f9fa",
            border_color=COLOR_BOTON_PRIMARIO,
            border_width=2,
            corner_radius=10,
            font=("Helvetica", 15),
            text_color=COLOR_TEXTO_OSCURO,
            placeholder_text="Ej: 1"
        )
        self.entry_id.pack(fill="x", pady=(0, 22))
        self.entry_id.bind("<KeyRelease>", lambda e: self.validar_entero(self.entry_id))

        # Campo Voltaje
        ctk.CTkLabel(
            campos_frame,
            text="Voltaje (V):",
            text_color=COLOR_TEXTO_OSCURO,
            font=("Helvetica", 16, "bold")
        ).pack(anchor="w", pady=(0, 10))
        self.entry_voltaje = ctk.CTkEntry(
            campos_frame,
            height=55,
            fg_color="#f8f9fa",
            border_color=COLOR_BOTON_PRIMARIO,
            border_width=2,
            corner_radius=10,
            font=("Helvetica", 15),
            text_color=COLOR_TEXTO_OSCURO,
            placeholder_text="Ej: 220"
        )
        self.entry_voltaje.pack(fill="x", pady=(0, 22))
        self.entry_voltaje.bind("<KeyRelease>", lambda e: self.validar_decimal(self.entry_voltaje))

        # Campo Potencia
        ctk.CTkLabel(
            campos_frame,
            text="Potencia (W):",
            text_color=COLOR_TEXTO_OSCURO,
            font=("Helvetica", 16, "bold")
        ).pack(anchor="w", pady=(0, 10))
        self.entry_potencia = ctk.CTkEntry(
            campos_frame,
            height=55,
            fg_color="#f8f9fa",
            border_color=COLOR_BOTON_PRIMARIO,
            border_width=2,
            corner_radius=10,
            font=("Helvetica", 15),
            text_color=COLOR_TEXTO_OSCURO,
            placeholder_text="Ej: 500.75"
        )
        self.entry_potencia.pack(fill="x", pady=(0, 25))
        self.entry_potencia.bind("<KeyRelease>", lambda e: self.validar_decimal(self.entry_potencia))

        # Nota informativa
        nota_frame = ctk.CTkFrame(campos_frame, fg_color="#e3f2fd", corner_radius=8)
        nota_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(
            nota_frame,
            text="La corriente se calculará automáticamente (I = P / V)",
            text_color=COLOR_TEXTO_OSCURO,
            font=("Helvetica", 11),
            wraplength=500
        ).pack(padx=10, pady=8)

        # Botones
        botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botones_frame.pack(fill="x", padx=40, pady=(10, 30))
        botones_frame.columnconfigure((0, 1), weight=1, uniform="botones")

        btn_cancelar = ctk.CTkButton(
            botones_frame,
            text="Cancelar",
            fg_color="#6b7280",
            hover_color="#4b5563",
            height=55,
            corner_radius=10,
            font=("Helvetica", 13, "bold"),
            command=self.destroy
        )
        btn_cancelar.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        btn_agregar = ctk.CTkButton(
            botones_frame,
            text="Agregar Lectura",
            fg_color=COLOR_BOTON_PRIMARIO,
            hover_color=COLOR_BOTON_HOVER,
            height=55,
            corner_radius=10,
            font=("Helvetica", 13, "bold"),
            command=self.agregar_dato
        )
        btn_agregar.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.attributes('-alpha', 0.0)
        self.animar_entrada()

    def animar_entrada(self):
        alpha = self.attributes('-alpha')
        if alpha < 1.0:
            self.attributes('-alpha', alpha + 0.1)
            self.after(15, self.animar_entrada)

    def validar_entero(self, entry):
        valor = entry.get()
        if valor and not valor.isdigit():
            nuevo_valor = ''.join(filter(str.isdigit, valor))
            entry.delete(0, 'end')
            entry.insert(0, nuevo_valor)

    def validar_decimal(self, entry):
        valor = entry.get()
        if valor:
            partes = valor.split('.')
            if len(partes) > 2:
                entry.delete(0, 'end')
                entry.insert(0, '.'.join(partes[:-1]) + partes[-1])
            else:
                nuevo_valor = ''
                punto_usado = False
                for char in valor:
                    if char.isdigit():
                        nuevo_valor += char
                    elif char == '.' and not punto_usado:
                        nuevo_valor += char
                        punto_usado = True
                if nuevo_valor != valor:
                    entry.delete(0, 'end')
                    entry.insert(0, nuevo_valor)

    def agregar_dato(self):
        """Guarda la lectura manual en la base de datos"""
        try:
            if not self.entry_id.get() or not self.entry_voltaje.get() or not self.entry_potencia.get():
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return

            id_circuito = int(self.entry_id.get())
            voltaje = float(self.entry_voltaje.get())
            potencia = float(self.entry_potencia.get())

            if voltaje <= 0:
                messagebox.showerror("Error", "El voltaje debe ser mayor a 0")
                return

            if potencia < 0:
                messagebox.showerror("Error", "La potencia no puede ser negativa")
                return

            # Calcular corriente: I = P / V
            corriente = potencia / voltaje if voltaje != 0 else 0

            # Mostrar confirmación
            respuesta = messagebox.askyesno(
                "Confirmar",
                f"Datos a guardar:\n"
                f"\n"
                f"ID Circuito: {id_circuito}\n"
                f"Voltaje: {voltaje:.2f} V\n"
                f"Corriente: {corriente:.2f} A (calculada)\n"
                f"Potencia: {potencia:.2f} W\n"
                f"\n\n"
                f"¿Desea guardar estos datos?"
            )

            if not respuesta:
                return

            # Intentar guardar
            try:
                from BackEnd.consulta import insertar_lectura_manual

                # Corrección: enviar fecha actual
                fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                exito = insertar_lectura_manual(id_circuito, voltaje, corriente, potencia, fecha_actual) # pylint: disable=no-value-for-parameter

            except ImportError:
                messagebox.showerror("Error", "No se encontró el módulo BackEnd.consulta\n\n Verifique la instalación.")
                return
            except Exception as e:
                print(f"[ERROR GENERAL] {e}")
                messagebox.showerror("Error de Base de Datos", f"Error al guardar:\n{str(e)}\n\n Verifique la conexión a la BD.")
                return

            if exito:
                messagebox.showinfo(
                    "Éxito",
                    f"Lectura agregada correctamente\n\n"
                    f"ID: {id_circuito}\n"
                    f"Voltaje: {voltaje:.2f}V\n"
                    f"Corriente: {corriente:.2f}A\n"
                    f"Potencia: {potencia:.2f}W"
                )
                if self.callback_actualizar:
                    self.callback_actualizar()
                self.destroy()
            else:
                messagebox.showerror(
                    " Error",
                    "No se pudo agregar la lectura.\n\n"
                    "Verifique:\n"
                    "• Que el ID del circuito exista\n"
                    "• La conexión a la base de datos\n"
                    "• Que las columnas necesarias existan en la tabla"
                )

        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

# ==========================================
# CLASE VENTANA DETALLE (VA PRIMERO)
# ==========================================
class VentanaDetalleDia(ctk.CTkToplevel):
    """Ventana modal que muestra los detalles de un día específico"""
    def __init__(self, parent, id_circuito, fecha):
        super().__init__(parent)
        self.id_circuito = id_circuito
        self.fecha = fecha
        
        self.title(f"Detalles - {fecha.strftime('%d/%m/%Y')}")
        self.geometry("900x700")
        self.configure(fg_color=COLOR_FONDO_MAIN)
        self.resizable(False, False)
        
        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"900x700+{x}+{y}")
        self.transient(parent)
        self.grab_set()
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL_DERECHO, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Título
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dia_semana = dias_semana[fecha.weekday()]
        
        ctk.CTkLabel(
            main_frame,
            text=f"📅 {dia_semana} {fecha.strftime('%d/%m/%Y')}",
            font=("Helvetica", 24, "bold"),
            text_color=COLOR_BOTON_PRIMARIO
        ).pack(pady=(20, 10))
        
        # Frame para el gráfico
        self.frame_grafico = ctk.CTkFrame(main_frame, fg_color="#f8f9fa", corner_radius=10, height=300)
        self.frame_grafico.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.frame_grafico.pack_propagate(False)
        
        # Frame para estadísticas
        frame_stats = ctk.CTkFrame(main_frame, fg_color="#f8f9fa", corner_radius=10)
        frame_stats.pack(fill="x", padx=20, pady=(0, 15))
        
        self.label_stats = ctk.CTkLabel(
            frame_stats,
            text="Cargando estadísticas...",
            font=("Consolas", 11),
            text_color=COLOR_TEXTO_OSCURO,
            justify="left"
        )
        self.label_stats.pack(padx=15, pady=15)
        
        # Frame para botones
        botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botones_frame.pack(fill="x", padx=20, pady=(0, 10))
        botones_frame.columnconfigure((0, 1, 2), weight=1, uniform="botones")
        
        # Botón Guardar Gráfico
        ctk.CTkButton(
            botones_frame,
            text="💾 Guardar\nGráfico",
            fg_color=COLOR_VERDE_PASTEL,
            hover_color="#229954",
            height=50,
            corner_radius=10,
            font=("Helvetica", 11, "bold"),
            command=self.guardar_grafico
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Botón Ver Torta
        ctk.CTkButton(
            botones_frame,
            text="📊 Ver\nTorta",
            fg_color=COLOR_BOTON_PRIMARIO,
            hover_color=COLOR_BOTON_HOVER,
            height=50,
            corner_radius=10,
            font=("Helvetica", 11, "bold"),
            command=self.mostrar_torta
        ).grid(row=0, column=1, sticky="ew", padx=5)
        
        # Botón Generar PDF
        ctk.CTkButton(
            botones_frame,
            text="📄 Generar\nPDF",
            fg_color=COLOR_BOTON_PRIMARIO,
            hover_color=COLOR_BOTON_HOVER,
            height=50,
            corner_radius=10,
            font=("Helvetica", 11, "bold"),
            command=self.generar_pdf
        ).grid(row=0, column=2, sticky="ew", padx=(5, 0))
        
        # Botón Cerrar
        ctk.CTkButton(
            main_frame,
            text="Cerrar",
            fg_color="#6b7280",
            hover_color="#4b5563",
            height=45,
            corner_radius=10,
            font=("Helvetica", 13, "bold"),
            command=self.destroy
        ).pack(pady=(0, 20), padx=20, fill="x")
        
        # Cargar datos
        self.cargar_datos()
        
        # Animación de entrada
        self.attributes('-alpha', 0.0)
        self.animar_entrada()
    
    def animar_entrada(self):
        alpha = self.attributes('-alpha')
        if alpha < 1.0:
            self.attributes('-alpha', alpha + 0.1)
            self.after(15, self.animar_entrada)
    
    def cargar_datos(self):
        """Carga y muestra los datos del día"""
        try:
            from BackEnd.consulta import obtener_lecturas_dia
            
            fechas, potencias = obtener_lecturas_dia(self.id_circuito, self.fecha) # pylint: disable=no-value-for-parameter
            
            if not fechas or not potencias:
                ctk.CTkLabel(
                    self.frame_grafico,
                    text="❌ No hay datos disponibles",
                    font=("Helvetica", 16, "bold"),
                    text_color="#6b7280"
                ).pack(expand=True)
                return
            
            # Guardar datos para exportar
            self.fechas = fechas
            self.potencias = potencias
            
            # Crear gráfico
            self.figura = Figure(figsize=(8, 4), dpi=100)
            self.figura.patch.set_facecolor('#f8f9fa')
            ax = self.figura.add_subplot(1, 1, 1)
            
            # Línea principal
            ax.plot(
                fechas,
                potencias,
                color=COLOR_BOTON_PRIMARIO,
                linewidth=2.5,
                marker='o',
                markersize=4,
                markerfacecolor=COLOR_BOTON_HOVER,
                markeredgecolor='white',
                markeredgewidth=1.5,
                label='Consumo',
                zorder=3
            )
            
            # Área sombreada
            ax.fill_between(fechas, potencias, color=COLOR_BOTON_PRIMARIO, alpha=0.15, zorder=1)
            
            # Líneas de umbral
            ax.axhline(y=480000, color=COLOR_ALERTA_ALTA, linestyle='--', linewidth=1.5, 
                       alpha=0.7, label='Umbral Alto (480kW)', zorder=2)
            ax.axhline(y=200000, color=COLOR_ALERTA_BAJA, linestyle='--', linewidth=1.5, 
                       alpha=0.7, label='Umbral Bajo (200kW)', zorder=2)
            
            # Estilo
            ax.set_facecolor('#f8f9fa')
            ax.set_title(f"Consumo - {self.fecha.strftime('%d/%m/%Y')}", 
                         fontsize=13, fontweight='bold', color=COLOR_TEXTO_OSCURO, pad=12)
            ax.set_ylabel("Potencia (W)", fontsize=10, fontweight='bold', color=COLOR_TEXTO_OSCURO)
            ax.grid(True, linestyle='--', alpha=0.3, linewidth=0.5, zorder=0)
            ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            self.figura.autofmt_xdate(rotation=45)
            ax.tick_params(colors=COLOR_TEXTO_OSCURO, labelsize=8)
            
            # Renderizar
            canvas = FigureCanvasTkAgg(self.figura, master=self.frame_grafico)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Calcular estadísticas
            promedio = sum(potencias) / len(potencias)
            maximo = max(potencias)
            minimo = min(potencias)
            total_lecturas = len(potencias)
            variacion = maximo - minimo
            porcentaje_var = (variacion / promedio) * 100 if promedio > 0 else 0
            
            texto_stats = (
                f"📊 Estadísticas del Día:\n\n"
                f"• Promedio:      {promedio:>15,.2f} W\n"
                f"• Máximo:        {maximo:>15,.2f} W\n"
                f"• Mínimo:        {minimo:>15,.2f} W\n"
                f"• Variación:     {variacion:>15,.2f} W ({porcentaje_var:.1f}%)\n"
                f"• Lecturas:      {total_lecturas:>15}"
            )
            
            self.label_stats.configure(text=texto_stats)
            
        except ImportError:
            messagebox.showerror(
                "Error",
                "No se encontró la función 'obtener_lecturas_dia' en BackEnd.consulta",
                parent=self
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{str(e)}", parent=self)
    
    def guardar_grafico(self):
        """Guarda el gráfico como PNG"""
        if not hasattr(self, 'figura'):
            messagebox.showwarning("Sin Datos", "No hay gráfico para guardar", parent=self)
            return
        
        try:
            fecha_str = self.fecha.strftime("%Y%m%d")
            nombre_archivo = f"consumo_{fecha_str}_circuito_{self.id_circuito}.png"
            
            archivo = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Todos", "*.*")],
                initialfile=nombre_archivo,
                title="Guardar Gráfico",
                parent=self
            )
            
            if archivo:
                self.figura.savefig(archivo, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Éxito", f"Gráfico guardado en:\n{archivo}", parent=self)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}", parent=self)
    
    def mostrar_torta(self):
        """Muestra gráfico de torta en nueva ventana"""
        if not hasattr(self, 'potencias'):
            messagebox.showwarning("Sin Datos", "No hay datos para el gráfico de torta", parent=self)
            return
        
        # Ventana de torta
        ventana_torta = ctk.CTkToplevel(self)
        ventana_torta.title(f"Gráfico de Torta - {self.fecha.strftime('%d/%m/%Y')}")
        ventana_torta.geometry("700x650")
        ventana_torta.configure(fg_color=COLOR_FONDO_MAIN)
        ventana_torta.resizable(False, False)
        ventana_torta.transient(self)
        ventana_torta.grab_set()
        
        ventana_torta.update_idletasks()
        x = (ventana_torta.winfo_screenwidth() // 2) - (700 // 2)
        y = (ventana_torta.winfo_screenheight() // 2) - (650 // 2)
        ventana_torta.geometry(f"700x650+{x}+{y}")
        
        frame_principal = ctk.CTkFrame(ventana_torta, fg_color=COLOR_PANEL_DERECHO, corner_radius=15)
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame_principal,
            text=f"📊 Distribución de Consumo\n{self.fecha.strftime('%d/%m/%Y')}",
            text_color=COLOR_BOTON_PRIMARIO,
            font=("Helvetica", 18, "bold")
        ).pack(pady=(15, 5))
        
        frame_grafico = ctk.CTkFrame(frame_principal, fg_color="white", corner_radius=10)
        frame_grafico.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Crear figura de torta
        figura = Figure(figsize=(6, 5), dpi=100)
        figura.patch.set_facecolor('white')
        ax = figura.add_subplot(111)
        
        # Calcular rangos
        bajo = sum(1 for p in self.potencias if 0 < p <= 200000)
        normal = sum(1 for p in self.potencias if 200000 < p < 480000)
        alto = sum(1 for p in self.potencias if p >= 480000)
        total = bajo + normal + alto
        
        if total > 0:
            categorias, valores, colores = [], [], []
            
            if bajo > 0:
                categorias.append(f'Bajo\n({bajo})')
                valores.append(bajo)
                colores.append(COLOR_ALERTA_BAJA)
            
            if normal > 0:
                categorias.append(f'Normal\n({normal})')
                valores.append(normal)
                colores.append(COLOR_VERDE_PASTEL)
            
            if alto > 0:
                categorias.append(f'Alto\n({alto})')
                valores.append(alto)
                colores.append(COLOR_ALERTA_ALTA)
            
            wedges, texts, autotexts = ax.pie(
                valores,
                labels=categorias,
                colors=colores,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'color': COLOR_TEXTO_OSCURO, 'fontsize': 10, 'weight': 'bold'},
                explode=[0.05] * len(valores),
                shadow=True
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(12)
            
            ax.set_title(f"Total: {total} lecturas", color=COLOR_TEXTO_OSCURO, 
                         fontsize=13, fontweight='bold', pad=15)
            
            canvas = FigureCanvasTkAgg(figura, master=frame_grafico)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        else:
            ctk.CTkLabel(frame_grafico, text="Sin datos", font=("Helvetica", 14), 
                         text_color="#6b7280").pack(expand=True, pady=50)
        
        ctk.CTkButton(
            frame_principal,
            text="Cerrar",
            fg_color="#6b7280",
            hover_color="#4b5563",
            height=45,
            corner_radius=10,
            font=("Helvetica", 12, "bold"),
            command=ventana_torta.destroy
        ).pack(pady=(0, 15), padx=15, fill="x")
    
    def generar_pdf(self):
        """Genera PDF con el reporte del día"""
        if not hasattr(self, 'potencias'):
            messagebox.showwarning("Sin Datos", "No hay datos para generar PDF", parent=self)
            return
        
        try:
            fecha_str = self.fecha.strftime("%Y%m%d")
            nombre_archivo = f"reporte_{fecha_str}_circuito_{self.id_circuito}.pdf"
            
            archivo = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
                initialfile=nombre_archivo,
                title="Guardar Reporte PDF",
                parent=self
            )
            
            if archivo:
                doc = SimpleDocTemplate(archivo, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#8e44ad'),
                    spaceAfter=30,
                    alignment=1
                )
                
                elements.append(Paragraph("REPORTE DIARIO DE CONSUMO", title_style))
                elements.append(Spacer(1, 0.3*inch))
                
                dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                dia_semana = dias_semana[self.fecha.weekday()]
                
                info_data = [
                    ['Fecha:', f"{dia_semana} {self.fecha.strftime('%d/%m/%Y')}"],
                    ['Circuito:', f'#{self.id_circuito}'],
                    ['Generado:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')]
                ]
                
                info_table = Table(info_data, colWidths=[2*inch, 4*inch])
                info_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
                ]))
                
                elements.append(info_table)
                elements.append(Spacer(1, 0.4*inch))
                
                promedio = sum(self.potencias) / len(self.potencias)
                maximo = max(self.potencias)
                minimo = min(self.potencias)
                
                elements.append(Paragraph("ESTADÍSTICAS DEL DÍA", styles['Heading2']))
                elements.append(Spacer(1, 0.2*inch))
                
                stats_data = [
                    ['Métrica', 'Valor'],
                    ['Consumo Promedio', f'{promedio:,.2f} W'],
                    ['Consumo Máximo', f'{maximo:,.2f} W'],
                    ['Consumo Mínimo', f'{minimo:,.2f} W'],
                    ['Total Lecturas', f'{len(self.potencias)}']
                ]
                
                stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(stats_table)
                
                doc.build(elements)
                
                messagebox.showinfo("Éxito", f"Reporte PDF guardado:\n{archivo}", parent=self)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{str(e)}", parent=self)


# ==========================================
# 2. CLASE MODAL CALENDARIO (VA SEGUNDO)
# ==========================================
class ModalCalendarioHistorico(ctk.CTkToplevel):
    """Modal de calendario para ver consumos históricos"""
    def __init__(self, parent, id_circuito):
        super().__init__(parent)
        self.id_circuito = id_circuito
        self.fecha_seleccionada = None
        self.mes_actual = datetime.now().month
        self.anio_actual = datetime.now().year
        self.figura_actual = None
        self.datos_actuales = None

        self.title("Calendario - Historial de Consumos")
        self.geometry("1200x800")
        self.configure(fg_color=COLOR_FONDO_MAIN)
        self.resizable(False, False)

        # Centrar ventana
        self.update_idletasks()
        self.x = (self.winfo_screenwidth() // 2) - (1200 // 2)
        self.y = (self.winfo_screenheight() // 2) - (800 // 2)
        self.geometry(f"1200x800+{self.x}+{self.y}")
        self.transient(parent)
        self.grab_set()

        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL_DERECHO, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)

        # Título
        ctk.CTkLabel(
            main_frame,
            text="📅 Historial de Consumos por Fecha",
            font=("Helvetica", 24, "bold"),
            text_color=COLOR_BOTON_PRIMARIO
        ).pack(pady=(20, 10))

        # Frame contenedor con dos columnas
        contenedor = ctk.CTkFrame(main_frame, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=20, pady=10)
        contenedor.columnconfigure(0, weight=1)
        contenedor.columnconfigure(1, weight=2)

        # COLUMNA IZQUIERDA - CALENDARIO
        frame_calendario = ctk.CTkFrame(contenedor, fg_color="white", corner_radius=12, border_width=2, border_color=COLOR_BORDE)
        frame_calendario.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Navegación del calendario
        nav_frame = ctk.CTkFrame(frame_calendario, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkButton(
            nav_frame,
            text="◀",
            width=40,
            height=35,
            fg_color=COLOR_BOTON_PRIMARIO,
            hover_color=COLOR_BOTON_HOVER,
            font=("Helvetica", 16, "bold"),
            command=self.mes_anterior
        ).pack(side="left", padx=5)

        self.label_mes_anio = ctk.CTkLabel(
            nav_frame,
            text="",
            font=("Helvetica", 16, "bold"),
            text_color=COLOR_TEXTO_OSCURO
        )
        self.label_mes_anio.pack(side="left", expand=True)

        ctk.CTkButton(
            nav_frame,
            text="▶",
            width=40,
            height=35,
            fg_color=COLOR_BOTON_PRIMARIO,
            hover_color=COLOR_BOTON_HOVER,
            font=("Helvetica", 16, "bold"),
            command=self.mes_siguiente
        ).pack(side="right", padx=5)

        # Grid del calendario
        self.frame_grid_calendario = ctk.CTkFrame(frame_calendario, fg_color="transparent")
        self.frame_grid_calendario.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # COLUMNA DERECHA - DETALLES DEL DÍA
        frame_detalles = ctk.CTkFrame(contenedor, fg_color="white", corner_radius=12, border_width=2, border_color=COLOR_BORDE)
        frame_detalles.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.label_fecha_seleccionada = ctk.CTkLabel(
            frame_detalles,
            text="Selecciona una fecha en el calendario",
            font=("Helvetica", 18, "bold"),
            text_color=COLOR_TEXTO_OSCURO
        )
        self.label_fecha_seleccionada.pack(pady=(20, 10))

        # Frame para el gráfico
        self.frame_grafico = ctk.CTkFrame(frame_detalles, fg_color="#f8f9fa", corner_radius=10)
        self.frame_grafico.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Estadísticas del día
        self.frame_stats = ctk.CTkFrame(frame_detalles, fg_color="#f8f9fa", corner_radius=10)
        self.frame_stats.pack(fill="x", padx=15, pady=(0, 10))

        self.label_stats = ctk.CTkLabel(
            self.frame_stats,
            text="",
            font=("Consolas", 11),
            text_color=COLOR_TEXTO_OSCURO,
            justify="left"
        )
        self.label_stats.pack(padx=15, pady=15)

        # Botones de acción
        botones_frame = ctk.CTkFrame(frame_detalles, fg_color="transparent")
        botones_frame.pack(fill="x", padx=15, pady=(0, 15))
        botones_frame.columnconfigure((0, 1, 2), weight=1, uniform="botones_dia")

        self.btn_guardar_grafico = ctk.CTkButton(
            botones_frame,
            text="💾 Guardar\nGráfico",
            fg_color=COLOR_VERDE_PASTEL,
            hover_color="#229954",
            height=50,
            corner_radius=10,
            font=("Helvetica", 11, "bold"),
            command=self.guardar_grafico_dia,
            state="disabled"
        )
        self.btn_guardar_grafico.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        
        self.btn_ver_torta = ctk.CTkButton(
            botones_frame,
            text="📊 Ver\nTorta",
            fg_color=COLOR_BOTON_PRIMARIO,
            hover_color=COLOR_BOTON_HOVER,
            height=50,
            corner_radius=10,
            font=("Helvetica", 11, "bold"),
            command=self.mostrar_grafico_torta_dia,
            state="disabled"
        )
        self.btn_ver_torta.grid(row=0, column=1, sticky="ew", padx=3)

        self.btn_generar_pdf = ctk.CTkButton(
            botones_frame,
            text="📄 Generar PDF",  
            fg_color=COLOR_BOTON_PRIMARIO,
            hover_color=COLOR_BOTON_HOVER,
            height=45,
            corner_radius=10,
            font=("Helvetica", 12, "bold"),
            command=self.generar_pdf_dia,
            state="disabled"
        )
        self.btn_generar_pdf.grid(row=0, column=2, sticky="ew", padx=(5, 0))

        # Botón cerrar
        ctk.CTkButton(
            main_frame,
            text="Cerrar",
            fg_color="#6b7280",
            hover_color="#4b5563",
            height=45,
            corner_radius=10,
            font=("Helvetica", 13, "bold"),
            command=self.destroy
        ).pack(pady=(0, 20), padx=20, fill="x")

        # Generar calendario inicial
        self.generar_calendario()

        # Animación de entrada
        self.attributes('-alpha', 0.0)
        self.animar_entrada()

    def animar_entrada(self):
        alpha = self.attributes('-alpha')
        if alpha < 1.0:
            self.attributes('-alpha', alpha + 0.1)
            self.after(15, self.animar_entrada)

    def mes_anterior(self):
        """Navega al mes anterior"""
        if self.mes_actual == 1:
            self.mes_actual = 12
            self.anio_actual -= 1
        else:
            self.mes_actual -= 1
        self.generar_calendario()

    def mes_siguiente(self):
        """Navega al mes siguiente"""
        if self.mes_actual == 12:
            self.mes_actual = 1
            self.anio_actual += 1
        else:
            self.mes_actual += 1
        self.generar_calendario()

    def generar_calendario(self):
        """Genera la vista del calendario mensual"""
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.label_mes_anio.configure(text=f"{meses[self.mes_actual - 1]} {self.anio_actual}")

        for widget in self.frame_grid_calendario.winfo_children():
            widget.destroy()

        for i in range(7):
            self.frame_grid_calendario.columnconfigure(i, weight=1, uniform="dias")

        dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for i, dia in enumerate(dias_semana):
            ctk.CTkLabel(
                self.frame_grid_calendario,
                text=dia,
                font=("Helvetica", 11, "bold"),
                text_color=COLOR_BOTON_PRIMARIO
            ).grid(row=0, column=i, pady=5, sticky="ew")

        cal = calendar.monthcalendar(self.anio_actual, self.mes_actual)
        hoy = datetime.now()

        fila = 1
        for semana in cal:
            for i, dia in enumerate(semana):
                if dia == 0:
                    ctk.CTkFrame(self.frame_grid_calendario, fg_color="transparent").grid(row=fila, column=i, padx=2, pady=2, sticky="nsew")
                else:
                    fecha_dia = datetime(self.anio_actual, self.mes_actual, dia)
                    es_hoy = (fecha_dia.date() == hoy.date())
                    es_futuro = fecha_dia.date() > hoy.date()
                    tiene_datos = self.verificar_datos_dia(fecha_dia)

                    if es_futuro:
                        fg_color, hover_color, text_color, estado = "#e5e7eb", "#e5e7eb", "#9ca3af", "disabled"
                    elif es_hoy:
                        fg_color, hover_color, text_color, estado = COLOR_BOTON_PRIMARIO, COLOR_BOTON_HOVER, COLOR_TEXTO, "normal"
                    elif tiene_datos:
                        fg_color, hover_color, text_color, estado = COLOR_VERDE_PASTEL, "#229954", COLOR_TEXTO, "normal"
                    else:
                        fg_color, hover_color, text_color, estado = "#f3f4f6", "#e5e7eb", COLOR_TEXTO_OSCURO, "normal"

                    btn_dia = ctk.CTkButton(
                        self.frame_grid_calendario,
                        text=str(dia),
                        width=50,
                        height=50,
                        fg_color=fg_color,
                        hover_color=hover_color,
                        text_color=text_color,
                        corner_radius=8,
                        font=("Helvetica", 12, "bold"),
                        command=lambda f=fecha_dia: self.seleccionar_dia(f),
                        state=estado
                    )
                    btn_dia.grid(row=fila, column=i, padx=2, pady=2, sticky="nsew")
            fila += 1

    def verificar_datos_dia(self, fecha):
        """Verifica si hay datos para un día específico"""
        try:
            from BackEnd.consulta import obtener_lecturas_dia
            fechas, potencias = obtener_lecturas_dia(self.id_circuito, fecha)  # pylint: disable=no-value-for-parameter
            return len(fechas) > 0
        except Exception:
            return False

    def seleccionar_dia(self, fecha):
        """Abre ventana emergente con los detalles del día seleccionado"""
        self.fecha_seleccionada = fecha

        if not self.verificar_datos_dia(fecha):
            messagebox.showinfo(
                "Sin Datos",
                f"No hay datos disponibles para {fecha.strftime('%d/%m/%Y')}",
                parent=self
            )
            return

        VentanaDetalleDia(self, self.id_circuito, fecha)

    def guardar_grafico_dia(self):
        """Guarda el gráfico del día seleccionado"""
        if not hasattr(self, 'figura_actual') or self.figura_actual is None:
            messagebox.showwarning("Sin Datos", "No hay gráfico para guardar", parent=self)
            return

        try:
            fecha_str = self.fecha_seleccionada.strftime("%Y%m%d")
            nombre_archivo = f"consumo_{fecha_str}_circuito_{self.id_circuito}.png"
            archivo = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Todos", "*.*")],
                initialfile=nombre_archivo,
                title="Guardar Gráfico",
                parent=self
            )
            if archivo:
                self.figura_actual.savefig(archivo, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Éxito", f"Gráfico guardado en:\n{archivo}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el gráfico:\n{str(e)}", parent=self)

    def generar_pdf_dia(self):
        """Genera un PDF con el reporte completo del día"""
        if not hasattr(self, 'datos_actuales') or self.datos_actuales is None:
            messagebox.showwarning("Sin Datos", "No hay datos para generar el PDF", parent=self)
            return

        try:
            fecha_str = self.fecha_seleccionada.strftime("%Y%m%d")
            nombre_archivo = f"reporte_{fecha_str}_circuito_{self.id_circuito}.pdf"
            archivo = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
                initialfile=nombre_archivo,
                title="Guardar Reporte PDF",
                parent=self
            )

            if archivo:
                fechas, potencias = self.datos_actuales 
                doc = SimpleDocTemplate(archivo, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()

                title_style = ParagraphStyle(
                    'CustomTitle', parent=styles['Heading1'], fontSize=24,
                    textColor=colors.HexColor('#8e44ad'), spaceAfter=30, alignment=1
                )
                elements.append(Paragraph("REPORTE DIARIO DE CONSUMO", title_style))
                elements.append(Spacer(1, 0.3 * inch))

                dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                dia_semana = dias_semana[self.fecha_seleccionada.weekday()]
                info_data = [
                    ['Fecha:', f"{dia_semana} {self.fecha_seleccionada.strftime('%d/%m/%Y')}"],
                    ['Circuito:', f'#{self.id_circuito}'],
                    ['Generado:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')]
                ]
                info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
                info_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
                ]))
                elements.append(info_table)
                elements.append(Spacer(1, 0.4 * inch))

                promedio = sum(potencias) / len(potencias)
                maximo = max(potencias)
                minimo = min(potencias)

                elements.append(Paragraph("ESTADÍSTICAS DEL DÍA", styles['Heading2']))
                elements.append(Spacer(1, 0.2 * inch))
                stats_data = [
                    ['Métrica', 'Valor'],
                    ['Consumo Promedio', f'{promedio:,.2f} W'],
                    ['Consumo Máximo', f'{maximo:,.2f} W'],
                    ['Consumo Mínimo', f'{minimo:,.2f} W'],
                    ['Total Lecturas', f'{len(potencias)}']
                ]
                stats_table = Table(stats_data, colWidths=[3 * inch, 3 * inch])
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(stats_table)
                doc.build(elements)
                messagebox.showinfo("Éxito", f"Reporte PDF generado:\n{archivo}", parent=self)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{str(e)}", parent=self)

    def mostrar_grafico_torta_dia(self):
        """Muestra gráfico de torta para el día seleccionado"""
        if not hasattr(self, 'datos_actuales') or self.datos_actuales is None:
            messagebox.showwarning("Sin Datos", "No hay datos para generar el gráfico", parent=self)
            return

        try:
            fechas, potencias = self.datos_actuales
            ventana = ctk.CTkToplevel(self)
            ventana.title(f"Gráfico de Torta - {self.fecha_seleccionada.strftime('%d/%m/%Y')}")
            ventana.geometry("700x650")
            ventana.configure(fg_color=COLOR_FONDO_MAIN)
            ventana.grab_set()

            ventana.update_idletasks()
            x = (ventana.winfo_screenwidth() // 2) - (700 // 2)
            y = (ventana.winfo_screenheight() // 2) - (650 // 2)
            ventana.geometry(f"700x650+{x}+{y}")

            frame_principal = ctk.CTkFrame(ventana, fg_color=COLOR_PANEL_DERECHO, corner_radius=15)
            frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

            ctk.CTkLabel(
                frame_principal,
                text=f"📊 Distribución de Consumo\n{self.fecha_seleccionada.strftime('%d/%m/%Y')}",
                text_color=COLOR_BOTON_PRIMARIO,
                font=("Helvetica", 18, "bold")
            ).pack(pady=(15, 5))

            frame_grafico = ctk.CTkFrame(frame_principal, fg_color="white", corner_radius=10)
            frame_grafico.pack(fill="both", expand=True, padx=15, pady=15)

            figura = Figure(figsize=(6, 5), dpi=100)
            figura.patch.set_facecolor('white')
            ax = figura.add_subplot(111)

            UMBRAL_BAJA = 200000.00
            UMBRAL_ALTA = 480000.00
            bajo = sum(1 for p in potencias if 0 < p <= UMBRAL_BAJA)
            normal = sum(1 for p in potencias if UMBRAL_BAJA < p < UMBRAL_ALTA)
            alto = sum(1 for p in potencias if p >= UMBRAL_ALTA)
            total = bajo + normal + alto

            if total == 0:
                ctk.CTkLabel(frame_grafico, text="Sin datos válidos", text_color="#6b7280").pack(expand=True)
            else:
                categorias, valores, colores = [], [], []
                if bajo > 0:
                    categorias.append(f'Bajo\n({bajo})')
                    valores.append(bajo)
                    colores.append(COLOR_ALERTA_BAJA)
                if normal > 0:
                    categorias.append(f'Normal\n({normal})')
                    valores.append(normal)
                    colores.append(COLOR_VERDE_PASTEL)
                if alto > 0:
                    categorias.append(f'Alto\n({alto})')
                    valores.append(alto)
                    colores.append(COLOR_ALERTA_ALTA)

                wedges, texts, autotexts = ax.pie(
                    valores, labels=categorias, colors=colores, autopct='%1.1f%%',
                    startangle=90, textprops={'color': COLOR_TEXTO_OSCURO, 'fontsize': 10, 'weight': 'bold'},
                    explode=[0.05] * len(valores), shadow=True
                )
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')

                ax.set_title(f"Total: {total} lecturas", color=COLOR_TEXTO_OSCURO, fontsize=13, fontweight='bold')
                canvas = FigureCanvasTkAgg(figura, master=frame_grafico)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

            ctk.CTkButton(
                frame_principal, text="Cerrar", fg_color="#6b7280", hover_color="#4b5563",
                height=45, corner_radius=10, command=ventana.destroy
            ).pack(pady=(0, 15), padx=15, fill="x")

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar gráfico: {str(e)}", parent=self)


class DashboardApp(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.rol = None

        self.configure(fg_color=COLOR_FONDO_MAIN)


        self.id_circuito = 1
        self.UMBRAL_ALTA_TENSION = 480000.00  # 480 kW = 480,000 W
        self.UMBRAL_BAJA_TENSION = 200000.00  # 200 kW = 200,000 W

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Panel Izquierdo
        self.panel_izquierdo = ctk.CTkFrame(
            self,
            fg_color=COLOR_PANEL_DERECHO,
            corner_radius=15,
            width=700,
            height=500,
            border_width=1,
            border_color=COLOR_BORDE
        )
        self.panel_izquierdo.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        self.panel_izquierdo.grid_propagate(False)

        # Widget del Gráfico
        self.figura = Figure(figsize=(5, 4), dpi=100)
        self.figura.patch.set_facecolor(COLOR_PANEL_DERECHO)
        self.canvas = FigureCanvasTkAgg(self.figura, master=self.panel_izquierdo)
        self.ax = self.figura.add_subplot(1, 1, 1)
        self.widget_grafico = self.canvas.get_tk_widget()
        self.widget_grafico.pack(fill="both", expand=True, padx=10, pady=10)

        # Widget del Reporte
        self.widget_reporte = ctk.CTkTextbox(
            self.panel_izquierdo,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLOR_PANEL_DERECHO,
            text_color=COLOR_TEXTO_OSCURO,
            border_width=0
        )

        # Botón Volver
        self.btn_volver_grafico = ctk.CTkButton(
            self.panel_izquierdo,
            text="Volver al Gráfico",
            fg_color=COLOR_BOTON_PRIMARIO,
            hover_color=COLOR_BOTON_HOVER,
            text_color=COLOR_TEXTO,
            height=45,
            corner_radius=10,
            font=("Helvetica", 13, "bold"),
            command=self.mostrar_vista_grafico
        )

        # Panel Derecho (más ancho para mejor visibilidad)
        panel_derecho = ctk.CTkScrollableFrame(self, fg_color="transparent")
        panel_derecho.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        panel_derecho.columnconfigure((0, 1), weight=1, uniform="alertas")

        # Configurar filas con peso para distribución
        panel_derecho.rowconfigure(6, weight=1)  # Espacio flexible antes del botón logout
        panel_derecho.rowconfigure(7, weight=0)  # Botón logout sin expansión

        # Card de Consumo
        frame_consumo = ctk.CTkFrame(
            panel_derecho,
            fg_color=COLOR_PANEL_DERECHO,
            corner_radius=15,
            border_width=2,
            border_color=COLOR_BORDE
        )
        frame_consumo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        ctk.CTkLabel(
            frame_consumo,
            text="Consumo Instantáneo",
            font=("Helvetica", 16, "bold"),
            text_color=COLOR_TEXTO_OSCURO
        ).pack(pady=(15, 5))

        self.label_potencia = ctk.CTkLabel(
            frame_consumo,
            text="Cargando...",
            font=("Arial", 42, "bold"),
            text_color=COLOR_BOTON_PRIMARIO
        )
        self.label_potencia.pack(pady=(5, 15))

        # Título Alertas
        ctk.CTkLabel(
            panel_derecho,
            text="⚠️ Alertas del Sistema",
            font=("Helvetica", 15, "bold"),
            text_color=COLOR_TEXTO
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 10))

        # Alertas
        self.caja_alerta_alta = ctk.CTkFrame(
            panel_derecho,
            fg_color=COLOR_PANEL_DERECHO,
            corner_radius=12,
            height=55,
            border_width=3,
            border_color=COLOR_BORDE
        )
        self.caja_alerta_alta.grid(row=2, column=0, sticky="nsew", padx=(0, 5), pady=(10,5))
        ctk.CTkLabel(
            self.caja_alerta_alta,
            text="⏫ Alta\nTensión",
            text_color=COLOR_TEXTO_OSCURO,
            font=("Helvetica", 11, "bold"),
            justify="center"
        ).pack(expand=True, pady=10)

        self.caja_alerta_baja = ctk.CTkFrame(
            panel_derecho,
            fg_color=COLOR_PANEL_DERECHO,
            corner_radius=12,
            height=55,
            border_width=3,
            border_color=COLOR_BORDE
        )
        self.caja_alerta_baja.grid(row=2, column=1, sticky="nsew", padx=(5, 0), pady=(10,5))
        ctk.CTkLabel(
            self.caja_alerta_baja,
            text="⏬ Baja\nTensión",
            text_color=COLOR_TEXTO_OSCURO,
            font=("Helvetica", 11, "bold"),
            justify="center"
        ).pack(expand=True, pady=10)

        # Notificación
        notificacion_frame = ctk.CTkFrame(
            panel_derecho,
            fg_color=COLOR_PANEL_DERECHO,
            corner_radius=12,
            border_width=2,
            border_color=COLOR_BORDE
        )
        notificacion_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=0, pady=15)

        self.label_notificacion = ctk.CTkLabel(
            notificacion_frame,
            text="✅ Sistema funcionando correctamente",
            text_color=COLOR_VERDE_PASTEL,
            wraplength=280,
            font=("Helvetica", 12, "bold"),
            justify="center"
        )
        self.label_notificacion.pack(expand=True, padx=15, pady=20)

        # Frame de botones principales
        self.botones_frame = ctk.CTkFrame(panel_derecho, fg_color="transparent")
        self.botones_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.botones_frame.columnconfigure((0, 1), weight=1)

        # Frame de estadísticas calculadas
        self.frame_estadisticas = ctk.CTkFrame(
            panel_derecho,
            fg_color=COLOR_PANEL_DERECHO,
            corner_radius=12,
            border_width=2,
            border_color=COLOR_BORDE
        )
        self.frame_estadisticas.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        ctk.CTkLabel(
            self.frame_estadisticas,
            text="🔢 Datos Calculados (24h)",
            text_color=COLOR_TEXTO_OSCURO,
            font=("Helvetica", 13, "bold")
        ).pack(pady=(10, 5))

        self.label_estadisticas = ctk.CTkLabel(
            self.frame_estadisticas,
            text="Cargando estadísticas...",
            text_color=COLOR_TEXTO_OSCURO,
            font=("Consolas", 10),
            justify="left"
        )
        self.label_estadisticas.pack(padx=15, pady=(5, 12))

        # Frame de gestión
        self.botones_gestion_frame = ctk.CTkFrame(
            panel_derecho,
            fg_color=COLOR_PANEL_DERECHO,
            corner_radius=12,
            border_width=2,
            border_color=COLOR_BORDE
        )
        self.botones_gestion_frame.grid(row=6, column=0, columnspan=2, sticky="new", pady=(0, 8))
        self.botones_gestion_frame.columnconfigure((0, 1), weight=1)

        # Botón cerrar sesión - CENTRADO Y VISIBLE
        btn_logout = ctk.CTkButton(
            panel_derecho,
            text="Cerrar Sesión",
            fg_color=COLOR_LOGOUT,
            hover_color="#b91c1c",
            text_color=COLOR_TEXTO,
            height=50,
            corner_radius=10,
            font=("Helvetica", 14, "bold"),
            command=self.cerrar_sesion
        )
        btn_logout.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def cerrar_sesion(self):
        """Cierra la sesión con confirmación y mensaje de despedida"""
        respuesta = messagebox.askyesno(
            "Cerrar Sesión",
            "¿Seguro que quieres cerrar sesión?\n\nPerderás acceso al dashboard actual.",
            icon='question'
        )

        if respuesta:
            # Ventana de carga con animación
            ventana_carga = ctk.CTkToplevel(self)
            ventana_carga.title("Cerrando...")
            ventana_carga.geometry("400x200")
            ventana_carga.configure(fg_color=COLOR_FONDO_MAIN)
            ventana_carga.resizable(False, False)
            ventana_carga.overrideredirect(True)

            ventana_carga.update_idletasks()
            x = (ventana_carga.winfo_screenwidth() // 2) - (400 // 2)
            y = (ventana_carga.winfo_screenheight() // 2) - (200 // 2)
            ventana_carga.geometry(f"400x200+{x}+{y}")

            frame_carga = ctk.CTkFrame(ventana_carga, fg_color=COLOR_PANEL_DERECHO, corner_radius=15)
            frame_carga.pack(fill="both", expand=True, padx=20, pady=20)

            ctk.CTkLabel(
                frame_carga,
                text="👋",
                font=("Helvetica", 48),
                text_color=COLOR_BOTON_PRIMARIO
            ).pack(pady=(20, 10))

            ctk.CTkLabel(
                frame_carga,
                text="Cerrando sesión...",
                font=("Helvetica", 20, "bold"),
                text_color=COLOR_TEXTO_OSCURO
            ).pack(pady=5)

            ctk.CTkLabel(
                frame_carga,
                text="Espera un momento",
                font=("Helvetica", 12),
                text_color="#6b7280"
            ).pack(pady=(0, 20))

            progress = ctk.CTkProgressBar(frame_carga, width=300, height=8, corner_radius=4)
            progress.pack(pady=10)
            progress.set(0)

            ventana_carga.update()

            # --- CORRECCIÓN DE INDENTACIÓN AQUÍ ---
            def animar_cierre(paso=0):
                if paso < 10:
                    progress.set((paso + 1) / 10)
                    ventana_carga.update()
                    self.after(100, lambda: animar_cierre(paso + 1))
                else:
                    ventana_carga.destroy()
                    self.rol = None
                    self.controller.mostrar_login()
            
            animar_cierre()

    def abrir_modal_modificar(self):
        """Abre modal de modificación con validación de permisos"""
        if not PermisosRol.puede(self.rol, 'modificar_datos'):
            messagebox.showerror(
                "Acceso Denegado",
                "No tienes permisos para modificar datos"
            )
            return
        ModalModificar(self, callback_actualizar=self.actualizar_datos_inmediato)

    def abrir_modal_agregar(self):
        """Abre modal de agregar datos con validación de permisos"""
        if not PermisosRol.puede(self.rol, 'agregar_datos'):
            messagebox.showerror(
                "Acceso Denegado",
                "No tienes permisos para agregar datos"
            )
            return
        ModalAgregarDato(self, callback_actualizar=self.actualizar_datos_inmediato)

    def abrir_gestion_usuarios(self):
        """Abre el modal de gestión de usuarios - Solo Admin"""
        if not PermisosRol.puede(self.rol, 'gestionar_usuarios'):
            messagebox.showerror(
                " Acceso Denegado",
                "Solo los administradores pueden gestionar usuarios"
            )
            return
        ModalGestionUsuarios(self)

    def actualizar_datos_inmediato(self):
        """Actualiza datos inmediatamente después de agregar/modificar"""
        self.actualizar_datos()
        self.actualizar_estadisticas()

    def configurar_dashboard_por_rol(self, rol):
        """Versión mejorada con sistema de permisos centralizado"""
        self.rol = rol
        permisos = PermisosRol.obtener_permisos(rol)

        self.controller.title(f"Dashboard de Energía - {self.rol}")

        # Limpiar botones existentes
        for widget in self.botones_frame.winfo_children():
            widget.destroy()
        for widget in self.botones_gestion_frame.winfo_children():
            widget.destroy()

        # ===== BOTONES PRINCIPALES CON CALENDARIO =====
        if permisos.get('visualizar_graficos'):
            # Configurar 3 columnas para los 3 botones
            self.botones_frame.columnconfigure((0, 1, 2), weight=1, uniform="botones_principales")

            # Botón Gráfico de Torta
            btn_torta = ctk.CTkButton(
                self.botones_frame,
                text="📊 Gráfico",
                fg_color=COLOR_BOTON_PRIMARIO,
                text_color=COLOR_TEXTO,
                hover_color=COLOR_BOTON_HOVER,
                height=45,
                corner_radius=10,
                font=("Helvetica", 11, "bold"),
                command=self.mostrar_grafico_torta
            )
            btn_torta.grid(row=0, column=0, sticky="ew", padx=(0, 3), pady=5)

            # Botón Calendario (NUEVO)
            btn_calendario = ctk.CTkButton(
                self.botones_frame,
                text="📅 Calendario",
                fg_color=COLOR_BOTON_PRIMARIO,
                text_color=COLOR_TEXTO,
                hover_color=COLOR_BOTON_HOVER,
                height=45,
                corner_radius=10,
                font=("Helvetica", 11, "bold"),
                command=self.abrir_calendario_historico
            )
            btn_calendario.grid(row=0, column=1, sticky="ew", padx=3, pady=5)

            # Botón Reporte
            if permisos.get('visualizar_reportes'):
                btn_reporte = ctk.CTkButton(
                    self.botones_frame,
                    text="🗂️ Reporte",
                    fg_color=COLOR_BOTON_PRIMARIO,
                    text_color=COLOR_TEXTO,
                    hover_color=COLOR_BOTON_HOVER,
                    height=45,
                    corner_radius=10,
                    font=("Helvetica", 11, "bold"),
                    command=self.mostrar_vista_reporte
                )
                btn_reporte.grid(row=0, column=2, sticky="ew", padx=(3, 0), pady=5)
        else:
            # Si solo tiene permisos de reportes (sin gráficos)
            if permisos.get('visualizar_reportes'):
                btn_reporte = ctk.CTkButton(
                    self.botones_frame,
                    text="🗂️ Reporte",
                    fg_color=COLOR_BOTON_PRIMARIO,
                    text_color=COLOR_TEXTO,
                    hover_color=COLOR_BOTON_HOVER,
                    height=45,
                    corner_radius=10,
                    font=("Helvetica", 12, "bold"),
                    command=self.mostrar_vista_reporte
                )
                btn_reporte.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)

        # ===== SECCIÓN GESTIÓN DE DATOS Y USUARIOS (Solo Admin) =====
        if permisos.get('modificar_datos') or permisos.get('agregar_datos') or permisos.get('gestionar_usuarios'):

            ctk.CTkLabel(
                self.botones_gestion_frame,
                text="🛠️ Panel de Administración",
                text_color=COLOR_TEXTO_OSCURO,
                font=("Helvetica", 13, "bold")
            ).grid(row=0, column=0, columnspan=2, pady=(12, 8))

            fila = 1
            columna = 0

            # Botones de gestión de datos
            if permisos.get('modificar_datos'):
                btn_modificar = ctk.CTkButton(
                    self.botones_gestion_frame,
                    text="✏️ Modificar",
                    fg_color="white",
                    text_color=COLOR_VERDE_PASTEL,
                    hover_color="#f0f0f0",
                    border_width=2,
                    border_color=COLOR_VERDE_PASTEL,
                    height=38,
                    corner_radius=10,
                    font=("Helvetica", 11, "bold"),
                    command=self.abrir_modal_modificar
                )
                btn_modificar.grid(row=fila, column=columna, sticky="ew", padx=(15, 5), pady=(0, 12))
                columna += 1

            if permisos.get('agregar_datos'):
                btn_manual = ctk.CTkButton(
                    self.botones_gestion_frame,
                    text="➕ Agregar",
                    fg_color="white",
                    text_color=COLOR_VERDE_PASTEL,
                    hover_color="#f0f0f0",
                    border_width=2,
                    border_color=COLOR_VERDE_PASTEL,
                    height=38,
                    corner_radius=10,
                    font=("Helvetica", 11, "bold"),
                    command=self.abrir_modal_agregar
                )
                padx = (5, 15) if columna > 0 else (15, 15)
                btn_manual.grid(row=fila, column=columna, sticky="ew", padx=padx, pady=(0, 12))

            # Botón de gestión de usuarios (Solo Admin)
            if permisos.get('gestionar_usuarios'):
                btn_usuarios = ctk.CTkButton(
                    self.botones_gestion_frame,
                    text="👥 Gestionar Usuarios",
                    fg_color=COLOR_BOTON_PRIMARIO,
                    hover_color=COLOR_BOTON_HOVER,
                    text_color=COLOR_TEXTO,
                    height=38,
                    corner_radius=10,
                    font=("Helvetica", 11, "bold"),
                    command=self.abrir_gestion_usuarios
                )
                btn_usuarios.grid(row=fila+1, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 12))

        # ===== GESTIÓN DE ALERTAS (Gerente y Admin) =====
        if permisos.get('gestionar_alertas'):
            # --- CORRECCIÓN AQUÍ: Todo indentado dentro del if ---
            frame_alertas = ctk.CTkFrame(
                self.botones_gestion_frame,
                fg_color="transparent"
            )
            fila_alertas = 3 if permisos.get('gestionar_usuarios') else 2
            frame_alertas.grid(row=fila_alertas, column=0, columnspan=2, sticky="ew", pady=(10, 0))
            frame_alertas.columnconfigure((0, 1), weight=1)

            ctk.CTkLabel(
                frame_alertas,
                text="🚨 Gestión de Alertas",
                text_color=COLOR_TEXTO_OSCURO,
                font=("Helvetica", 13, "bold")
            ).grid(row=0, column=0, columnspan=2, pady=(5, 8))

            btn_ver_alertas = ctk.CTkButton(
                frame_alertas,
                text="Ver Alertas",
                fg_color=COLOR_BOTON_PRIMARIO,
                hover_color=COLOR_BOTON_HOVER,
                text_color=COLOR_TEXTO,
                height=38,
                corner_radius=10,
                font=("Helvetica", 11, "bold"),
                command=self.abrir_gestion_alertas
            )
            btn_ver_alertas.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 12))

        self.mostrar_vista_grafico()
        self.actualizar_datos()
        self.actualizar_estadisticas()

    # --- CORRECCIÓN AQUÍ: Método movido fuera de 'abrir_gestion_alertas' ---
    def abrir_calendario_historico(self):
        """Abre el modal de calendario histórico"""
        if not hasattr(self, 'rol') or self.rol not in ['Admin', 'Empleado']:
            messagebox.showerror(
                "Acceso Denegado",
                "No tienes permisos para acceder al calendario"
            )
            return

        ModalCalendarioHistorico(self, self.id_circuito)

    def abrir_gestion_alertas(self):
        """Ventana de gestión de alertas para Gerente y Admin - CON PERSISTENCIA"""
        if not PermisosRol.puede(self.rol, 'gestionar_alertas'):
            messagebox.showerror(
                " Acceso Denegado",
                "No tienes permisos para gestionar alertas"
            )
            return

        ventana = ctk.CTkToplevel(self)
        ventana.title("Gestión de Alertas")
        ventana.geometry("800x600")
        ventana.configure(fg_color=COLOR_FONDO_MAIN)
        ventana.resizable(False, False)
        ventana.grab_set()

        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (800 // 2)
        y = (ventana.winfo_screenheight() // 2) - (600 // 2)
        ventana.geometry(f"800x600+{x}+{y}")

        frame_principal = ctk.CTkFrame(
            ventana,
            fg_color=COLOR_PANEL_DERECHO,
            corner_radius=15
        )
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame_principal,
            text="Historial de Alertas del Sistema",
            text_color=COLOR_BOTON_PRIMARIO,
            font=("Helvetica", 22, "bold")
        ).pack(pady=(15, 10))

        frame_filtros = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_filtros.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            frame_filtros,
            text="Filtrar por estado:",
            text_color=COLOR_TEXTO_OSCURO,
            font=("Helvetica", 12, "bold")
        ).pack(side="left", padx=5)

        var_filtro = ctk.StringVar(value="Todas")
        combo_filtro = ctk.CTkComboBox(
            frame_filtros,
            values=["Todas", "Activas", "Resueltas"],
            variable=var_filtro,
            width=150,
            state="readonly"
        )
        combo_filtro.pack(side="left", padx=10)

        frame_scroll = ctk.CTkScrollableFrame(
            frame_principal,
            fg_color="white",
            corner_radius=10,
            height=350
        )
        frame_scroll.pack(fill="both", expand=True, padx=15, pady=10)

        # Diccionario para rastrear estado de alertas
        alertas_estado = {}

        # Datos de ejemplo (reemplazar con consulta a BD)
        alertas_ejemplo = [
            {
                'id': 1,
                'tipo': 'Alta Tensión',
                'valor': 490000,
                'fecha': '2025-10-30 14:30:00',
                'estado': 'Activa',
                'circuito': 1
            },
            {
                'id': 2,
                'tipo': 'Baja Tensión',
                'valor': 200000,
                'fecha': '2025-10-30 12:15:00',
                'estado': 'Resuelta',
                'circuito': 1
            },
            {
                'id': 3,
                'tipo': 'Alta Tensión',
                'valor': 500000,
                'fecha': '2025-10-30 10:45:00',
                'estado': 'Activa',
                'circuito': 2
            }
        ]

        # Inicializar estados
        for alerta in alertas_ejemplo:
            alertas_estado[alerta['id']] = alerta['estado']

        def crear_card_alerta(alerta):
            estado_actual = alertas_estado.get(alerta['id'], alerta['estado'])

            card = ctk.CTkFrame(
                frame_scroll,
                fg_color="#f8f9fa" if estado_actual == 'Resuelta' else "#fff3cd",
                corner_radius=10,
                border_width=2,
                border_color=COLOR_VERDE_PASTEL if estado_actual == 'Resuelta' else COLOR_ALERTA_ALTA
            )
            card.pack(fill="x", pady=8, padx=10)

            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=(10, 5))

            icono = "✅" if estado_actual == 'Resuelta' else "⚠️"
            ctk.CTkLabel(
                header,
                text=f"{icono} {alerta['tipo']}",
                text_color=COLOR_TEXTO_OSCURO,
                font=("Helvetica", 14, "bold")
            ).pack(side="left")

            estado_label = ctk.CTkLabel(
                header,
                text=estado_actual,
                text_color=COLOR_VERDE_PASTEL if estado_actual == 'Resuelta' else COLOR_ALERTA_ALTA,
                font=("Helvetica", 11, "bold")
            )
            estado_label.pack(side="right")

            detalle_text = (
                f"Circuito: #{alerta['circuito']}  |  "
                f"Valor: {alerta['valor']:,.2f}W  |  "
                f"{alerta['fecha']}"
            )
            ctk.CTkLabel(
                card,
                text=detalle_text,
                text_color="#6b7280",
                font=("Consolas", 10)
            ).pack(padx=15, pady=(0, 5))

            if estado_actual == 'Activa':
                btn_resolver = ctk.CTkButton(
                    card,
                    text="Marcar como Resuelta",
                    fg_color=COLOR_VERDE_PASTEL,
                    hover_color="#229954",
                    height=32,
                    corner_radius=8,
                    font=("Helvetica", 10, "bold"),
                    command=lambda a=alerta: resolver_alerta(a['id'])
                )
                btn_resolver.pack(pady=(5, 10), padx=15, anchor="e")

        def resolver_alerta(id_alerta):
            respuesta = messagebox.askyesno(
                "Confirmar",
                f"¿Marcar alerta #{id_alerta} como resuelta?",
                parent=ventana
            )
            if respuesta:
                # Actualizar estado en el diccionario
                alertas_estado[id_alerta] = 'Resuelta'

                # Aquí iría la actualización en BD

                messagebox.showinfo(
                    "Éxito",
                    f"Alerta #{id_alerta} marcada como resuelta",
                    parent=ventana
                )
                aplicar_filtro()

        def aplicar_filtro(*args):
            for widget in frame_scroll.winfo_children():
                widget.destroy()

            filtro = var_filtro.get()
            alertas_filtradas = []

            for alerta in alertas_ejemplo:
                estado_actual = alertas_estado.get(alerta['id'], alerta['estado'])
                if filtro == "Todas":
                    alertas_filtradas.append(alerta)
                elif filtro == "Activas" and estado_actual == "Activa":
                    alertas_filtradas.append(alerta)
                elif filtro == "Resueltas" and estado_actual == "Resuelta":
                    alertas_filtradas.append(alerta)

            if alertas_filtradas:
                for alerta in alertas_filtradas:
                    crear_card_alerta(alerta)
            else:
                ctk.CTkLabel(
                    frame_scroll,
                    text="No hay alertas con este filtro",
                    text_color="#6b7280",
                    font=("Helvetica", 14)
                ).pack(pady=50)

        var_filtro.trace('w', aplicar_filtro)
        aplicar_filtro()

        ctk.CTkButton(
            frame_principal,
            text="Cerrar",
            fg_color="#6b7280",
            hover_color="#4b5563",
            height=45,
            corner_radius=10,
            font=("Helvetica", 12, "bold"),
            command=ventana.destroy
        ).pack(pady=(10, 15), padx=15, fill="x")

    def mostrar_vista_grafico(self):
        """Muestra el gráfico en el panel izquierdo con botón guardar"""
        self.widget_reporte.pack_forget()
        self.btn_volver_grafico.pack_forget()

        if hasattr(self, 'btn_guardar_reporte'):
            self.btn_guardar_reporte.pack_forget()

        self.widget_grafico.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        if not hasattr(self, 'btn_guardar_grafico'):
            self.btn_guardar_grafico = ctk.CTkButton(
                self.panel_izquierdo,
                text="Guardar Gráfico",
                fg_color=COLOR_VERDE_PASTEL,
                hover_color="#229954",
                text_color=COLOR_TEXTO,
                height=45,
                corner_radius=10,
                font=("Helvetica", 13, "bold"),
                command=self.guardar_grafico
            )

        self.btn_guardar_grafico.pack(side="bottom", pady=15, padx=10, fill="x")

    def mostrar_vista_reporte(self):
        """Muestra el reporte en el panel izquierdo con botón guardar PDF"""
        self.widget_grafico.pack_forget()

        if hasattr(self, 'btn_guardar_grafico'):
            self.btn_guardar_grafico.pack_forget()

        self.widget_reporte.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        if not hasattr(self, 'btn_guardar_reporte'):
            self.btn_guardar_reporte = ctk.CTkButton(
                self.panel_izquierdo,
                text="Guardar Reporte PDF",
                fg_color=COLOR_VERDE_PASTEL,
                hover_color="#229954",
                text_color=COLOR_TEXTO,
                height=45,
                corner_radius=10,
                font=("Helvetica", 13, "bold"),
                command=self.guardar_reporte_pdf
            )

        self.btn_guardar_reporte.pack(side="bottom", pady=(5, 15), padx=10, fill="x")
        self.btn_volver_grafico.pack(side="bottom", pady=(0, 5), padx=10, fill="x")

        self.generar_contenido_reporte()

    def mostrar_grafico_torta(self):
        """Abre una ventana con gráfico de torta"""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Gráfico de Consumo por Rangos")
        ventana.geometry("750x650")
        ventana.configure(fg_color=COLOR_FONDO_MAIN)
        ventana.resizable(False, False)
        ventana.grab_set()

        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (750 // 2)
        y = (ventana.winfo_screenheight() // 2) - (650 // 2)
        ventana.geometry(f"750x650+{x}+{y}")

        frame_principal = ctk.CTkFrame(ventana, fg_color=COLOR_PANEL_DERECHO, corner_radius=15)
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame_principal,
            text="Distribución de Consumo Eléctrico",
            text_color=COLOR_BOTON_PRIMARIO,
            font=("Helvetica", 20, "bold")
        ).pack(pady=(15, 10))

        frame_grafico = ctk.CTkFrame(frame_principal, fg_color="white", corner_radius=10)
        frame_grafico.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        figura = Figure(figsize=(7, 5), dpi=100)
        figura.patch.set_facecolor('white')
        ax = figura.add_subplot(111)
        canvas = FigureCanvasTkAgg(figura, master=frame_grafico)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        def generar_grafico():
            try:
                # Corrección: Agregado pylint disable
                fechas, potencias = obtener_lecturas_para_grafico(self.id_circuito, horas=24*30) # pylint: disable=no-value-for-parameter
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{str(e)}")
                return

            if not fechas or not potencias:
                messagebox.showinfo("Sin datos", "No hay lecturas en los últimos 30 días.")
                return

            bajo = sum(1 for p in potencias if 0 < p <= self.UMBRAL_BAJA_TENSION)
            normal = sum(1 for p in potencias if self.UMBRAL_BAJA_TENSION < p < self.UMBRAL_ALTA_TENSION)
            alto = sum(1 for p in potencias if p >= self.UMBRAL_ALTA_TENSION)
            total = bajo + normal + alto

            if total == 0:
                messagebox.showinfo("Sin datos", "No hay lecturas válidas.")
                return

            categorias, valores, colores = [], [], []
            if bajo > 0:
                categorias.append('Consumo Bajo\n(100000–200000W)')
                valores.append(bajo)
                colores.append(COLOR_ALERTA_BAJA)
            if normal > 0:
                categorias.append('Consumo Normal\n(300000–400000W)')
                valores.append(normal)
                colores.append(COLOR_VERDE_PASTEL)
            if alto > 0:
                categorias.append('Consumo Alto\n(>480000kW)')
                valores.append(alto)
                colores.append(COLOR_ALERTA_ALTA)

            ax.clear()
            wedges, texts, autotexts = ax.pie(
                valores,
                labels=categorias,
                colors=colores,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'color': COLOR_TEXTO_OSCURO, 'fontsize': 11, 'weight': 'bold'},
                explode=[0.05] * len(valores)
            )
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(13)
            ax.set_title(
                "Distribución - Últimos 30 días",
                color=COLOR_TEXTO_OSCURO,
                fontsize=15,
                fontweight='bold',
                pad=20
            )
            canvas.draw()

        generar_grafico()

    def generar_contenido_reporte(self):
        """Genera el reporte mejorado con estadísticas"""
        self.widget_reporte.delete("1.0", "end")

        # Corrección: Agregado pylint disable
        fechas, potencias = obtener_lecturas_para_grafico(self.id_circuito, horas=24) # pylint: disable=no-value-for-parameter

        if not fechas:
            self.widget_reporte.insert("1.0", "No hay datos de consumo en las últimas 24 horas.")
            return

        promedio = sum(potencias) / len(potencias)
        maximo = max(potencias)
        minimo = min(potencias)
        total_lecturas = len(potencias)

        self.widget_reporte.tag_config("center", justify="center")
        self.widget_reporte.tag_config("header", justify="center", foreground=COLOR_BOTON_PRIMARIO)
        self.widget_reporte.tag_config("subheader", justify="center", foreground=COLOR_TEXTO_OSCURO)
        self.widget_reporte.tag_config("stats", justify="center", foreground=COLOR_VERDE_PASTEL)
        self.widget_reporte.tag_config("data", justify="center", foreground=COLOR_TEXTO_OSCURO)

        self.widget_reporte.insert("end", "=" * 65 + "\n", "center")
        self.widget_reporte.insert("end", "REPORTE DE CONSUMO ENERGÉTICO\n", "header")
        self.widget_reporte.insert("end", "=" * 65 + "\n\n", "center")

        self.widget_reporte.insert("end", f"Fecha: {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}\n", "data")
        self.widget_reporte.insert("end", f"Circuito: #{self.id_circuito}\n", "data")
        self.widget_reporte.insert("end", f"Período: Últimas 24 horas\n\n", "data")

        self.widget_reporte.insert("end", "=" * 65 + "\n", "center")
        self.widget_reporte.insert("end", "ESTADÍSTICAS GENERALES\n", "header")
        self.widget_reporte.insert("end", "=" * 65 + "\n\n", "center")

        self.widget_reporte.insert("end", f"Promedio:    {promedio:>10.2f} W\n", "stats")
        self.widget_reporte.insert("end", f"Máximo:      {maximo:>10.2f} W\n", "stats")
        self.widget_reporte.insert("end", f"Mínimo:      {minimo:>10.2f} W\n", "stats")
        self.widget_reporte.insert("end", f"Lecturas:    {total_lecturas:>10}\n\n", "stats")

        bajo = sum(1 for p in potencias if 0 < p <= self.UMBRAL_BAJA_TENSION)
        normal = sum(1 for p in potencias if self.UMBRAL_BAJA_TENSION < p < self.UMBRAL_ALTA_TENSION)
        alto = sum(1 for p in potencias if p >= self.UMBRAL_ALTA_TENSION)

        self.widget_reporte.insert("end", "=" * 65 + "\n", "center")
        self.widget_reporte.insert("end", "DISTRIBUCIÓN POR RANGOS\n", "header")
        self.widget_reporte.insert("end", "=" * 65 + "\n\n", "center")

        self.widget_reporte.insert("end", f"Consumo Bajo (100000-200000W):        {bajo:>5} lecturas\n", "data")
        self.widget_reporte.insert("end", f"Consumo Normal (300000-400000W):   {normal:>5} lecturas\n", "data")
        self.widget_reporte.insert("end", f"Consumo Alto (>480000W):         {alto:>5} lecturas\n\n", "data")

        self.widget_reporte.insert("end", "=" * 65 + "\n", "center")
        self.widget_reporte.insert("end", "HISTORIAL DETALLADO\n", "header")
        self.widget_reporte.insert("end", "=" * 65 + "\n\n", "center")

        self.widget_reporte.insert("end", "{:<30} {:>25}\n".format("Fecha y Hora", "Potencia (W)"), "subheader")
        self.widget_reporte.insert("end", "-" * 65 + "\n", "center")

        for fecha, potencia in zip(fechas, potencias):
            linea = "{:<30} {:>25.2f}\n".format(fecha.strftime('%Y-%m-%d %H:%M:%S'), potencia)
            self.widget_reporte.insert("end", linea, "data")

        self.widget_reporte.insert("end", "\n" + "=" * 65 + "\n", "center")
        self.widget_reporte.insert("end", "Fin del Reporte\n", "center")
        self.widget_reporte.insert("end", "=" * 65 + "\n", "center")

    def guardar_grafico(self):
        """Guarda el gráfico actual como imagen PNG"""
        try:
            fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"grafico_consumo_{fecha_actual}.png"

            archivo = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Todos los archivos", "*.*")],
                initialfile=nombre_archivo,
                title="Guardar Gráfico"
            )

            if archivo:
                self.figura.savefig(archivo, dpi=300, bbox_inches='tight', facecolor='white')
                messagebox.showinfo("Éxito", f"Gráfico guardado en:\n{archivo}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el gráfico:\n{str(e)}")

    def guardar_reporte_pdf(self):
        """Guarda el reporte actual como archivo PDF"""
        try:
            fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"reporte_consumo_{fecha_actual}.pdf"

            archivo = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf"), ("Todos los archivos", "*.*")],
                initialfile=nombre_archivo,
                title="Guardar Reporte PDF"
            )

            if archivo:
                # Corrección: Agregado pylint disable
                fechas, potencias = obtener_lecturas_para_grafico(self.id_circuito, horas=24) # pylint: disable=no-value-for-parameter

                if not fechas:
                    messagebox.showerror("Error", "No hay datos para generar el reporte")
                    return

                promedio = sum(potencias) / len(potencias)
                maximo = max(potencias)
                minimo = min(potencias)
                total_lecturas = len(potencias)
                bajo = sum(1 for p in potencias if 0 < p <= self.UMBRAL_BAJA_TENSION)
                normal = sum(1 for p in potencias if self.UMBRAL_BAJA_TENSION < p < self.UMBRAL_ALTA_TENSION)
                alto = sum(1 for p in potencias if p >= self.UMBRAL_ALTA_TENSION)

                doc = SimpleDocTemplate(archivo, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()

                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#8e44ad'),
                    spaceAfter=30,
                    alignment=1
                )

                elements.append(Paragraph("REPORTE DE CONSUMO ENERGÉTICO", title_style))
                elements.append(Spacer(1, 0.3*inch))

                info_data = [
                    ['Fecha:', datetime.now().strftime('%d/%m/%Y - %H:%M:%S')],
                    ['Circuito:', f'#{self.id_circuito}'],
                    ['Período:', 'Últimas 24 horas']
                ]

                info_table = Table(info_data, colWidths=[2*inch, 4*inch])
                info_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
                ]))

                elements.append(info_table)
                elements.append(Spacer(1, 0.4*inch))

                elements.append(Paragraph("ESTADÍSTICAS GENERALES", styles['Heading2']))
                elements.append(Spacer(1, 0.2*inch))

                stats_data = [
                    ['Métrica', 'Valor'],
                    ['Promedio', f'{promedio:.2f} W'],
                    ['Máximo', f'{maximo:.2f} W'],
                    ['Mínimo', f'{minimo:.2f} W'],
                    ['Total Lecturas', f'{total_lecturas}']
                ]

                stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(stats_table)
                elements.append(Spacer(1, 0.4*inch))
                elements.append(Paragraph("DISTRIBUCIÓN POR RANGOS", styles['Heading2']))
                elements.append(Spacer(1, 0.2*inch))
                rangos_data = [
                    ['Rango', 'Lecturas'],
                    ['Consumo Bajo (100000-200000W)', f'{bajo}'],
                    ['Consumo Normal (300000-400000W)', f'{normal}'],
                    ['Consumo Alto (>480000W)', f'{alto}']
                ]

                rangos_table = Table(rangos_data, colWidths=[4*inch, 2*inch])
                rangos_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                elements.append(rangos_table)

                doc.build(elements)

                messagebox.showinfo("Éxito", f"Reporte PDF guardado en:\n{archivo}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el reporte PDF:\n{str(e)}")

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas calculadas en tiempo real"""
        try:
            # Corrección: Agregado pylint disable
            fechas, potencias = obtener_lecturas_para_grafico(self.id_circuito, horas=24) # pylint: disable=no-value-for-parameter

            if fechas and potencias:
                promedio = sum(potencias) / len(potencias)
                maximo = max(potencias)
                minimo = min(potencias)

                texto_stats = (  
                    f"Promedio: {promedio:,.2f} W\n"
                    f"Máximo: {maximo:,.2f} W\n"
                    f"Mínimo: {minimo:,.2f} W\n"
                    f"Lecturas: {len(potencias)}"
                )
                self.label_estadisticas.configure(text=texto_stats)
            else:
                self.label_estadisticas.configure(text="Sin datos disponibles")

        except Exception as e:
            self.label_estadisticas.configure(text=f"Error: {str(e)[:30]}...")

    def actualizar_alertas(self, corriente_watts):
        """Actualiza las alertas con valores realistas"""

        self.caja_alerta_alta.configure(
            fg_color=COLOR_PANEL_DERECHO,
            border_color=COLOR_BORDE
        )
        self.caja_alerta_baja.configure(
            fg_color=COLOR_PANEL_DERECHO,
            border_color=COLOR_BORDE
        )

        if corriente_watts >= self.UMBRAL_ALTA_TENSION:
            self.caja_alerta_alta.configure(
                fg_color=COLOR_ALERTA_ALTA,
                border_color=COLOR_ALERTA_ALTA
            )
            self.label_notificacion.configure(
                text=f"⏫ ALERTA: Alta tensión detectada\nConsumo actual: {corriente_watts:,.2f}W",
                text_color=COLOR_ALERTA_ALTA
            )
        elif 0 < corriente_watts <= self.UMBRAL_BAJA_TENSION:
            self.caja_alerta_baja.configure(
                fg_color=COLOR_ALERTA_BAJA,
                border_color=COLOR_ALERTA_BAJA
            )
            self.label_notificacion.configure(
                text=f"⏬ INFO: Baja tensión detectada\nConsumo actual: {corriente_watts:,.2f}W",
                text_color=COLOR_ALERTA_BAJA
            )
        else:
            self.label_notificacion.configure(
                text=f"Sistema funcionando correctamente\nConsumo: {corriente_watts:,.2f}W (normal)",
                text_color=COLOR_VERDE_PASTEL
            )

    def actualizar_datos(self):
        """Actualiza el consumo, alertas y gráfico con animación"""
        try:
            # Corrección: Agregado pylint disable
            ultima_potencia = obtener_ultima_lectura(self.id_circuito) # pylint: disable=no-value-for-parameter

            self.label_potencia.configure(text=f"{ultima_potencia:,.2f} W")

            self.actualizar_alertas(ultima_potencia)

            # Corrección: Agregado pylint disable
            fechas, potencias = obtener_lecturas_para_grafico(self.id_circuito, horas=1) # pylint: disable=no-value-for-parameter
            self.ax.clear()

            self.ax.set_facecolor(COLOR_PANEL_DERECHO)
            self.ax.tick_params(axis='x', colors=COLOR_TEXTO_OSCURO, labelsize=9)
            self.ax.tick_params(axis='y', colors=COLOR_TEXTO_OSCURO, labelsize=9)
            self.ax.spines['bottom'].set_color(COLOR_BOTON_PRIMARIO)
            self.ax.spines['left'].set_color(COLOR_BOTON_PRIMARIO)
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)

            if fechas:
                self.ax.plot(
                    fechas,
                    potencias,
                    color=COLOR_BOTON_PRIMARIO,
                    linewidth=2.5,
                    marker='o',
                    markersize=5,
                    markerfacecolor=COLOR_BOTON_HOVER,
                    markeredgecolor='white',
                    markeredgewidth=2,
                    label='Consumo'
                )

                self.ax.fill_between(
                    fechas,
                    potencias,
                    color=COLOR_BOTON_PRIMARIO,
                    alpha=0.2
                )

                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                self.figura.autofmt_xdate()

                self.ax.set_title(
                    "Consumo Última Hora",
                    color=COLOR_TEXTO_OSCURO,
                    fontsize=14,
                    fontweight='bold',
                    pad=15
                )
                self.ax.set_ylabel(
                    "Potencia (W)",
                    color=COLOR_TEXTO_OSCURO,
                    fontsize=11,
                    fontweight='bold'
                )

                self.ax.grid(
                    True,
                    linestyle='--',
                    alpha=0.3,
                    color=COLOR_BOTON_PRIMARIO,
                    linewidth=0.5
                )

                self.canvas.draw()

            self.after(1000, self.actualizar_datos)

        except Exception as e:
            print(f"Error al actualizar datos: {e}")
            self.after(1000, self.actualizar_datos)