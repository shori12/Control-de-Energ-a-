import customtkinter as ctk
from Frontend.login_view import LoginView
from Frontend.app import DashboardApp
from Frontend.registro import RegistroView
from Frontend.password_reset_view import PasswordResetView

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FN-MUDAD | Sistema de Control de Energía")
        self.geometry("800x600")

        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginView, RegistroView, DashboardApp, PasswordResetView):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.mostrar_frame("LoginView")

    def mostrar_frame(self, page_name, rol=None):
        """Muestra un frame específico y gestiona la configuración"""
        if page_name == "DashboardApp":
            self.geometry("1100x700")
        else:
            self.geometry("800x600")      
        frame = self.frames[page_name]      
        if page_name == "LoginView":
            if hasattr(frame, 'limpiar_campos'):
                frame.limpiar_campos()
        

        if page_name == "DashboardApp" and rol:
            frame.configurar_dashboard_por_rol(rol)           
        frame.tkraise()

    def mostrar_login(self):
        """Muestra la pantalla de login al cerrar sesión"""
        self.geometry("800x600")
        self.mostrar_frame("LoginView")

    def login_exitoso(self, rol):
        self.mostrar_frame("DashboardApp", rol=rol)


if __name__ == '__main__':
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    app = MainApplication()
    app.mainloop()
