
# 🔌 Sistema de Control de Energía FN-MUDAD

Sistema de monitoreo y control de consumo eléctrico en tiempo real con dashboard interactivo, alertas automáticas y generación de reportes.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Stack Tecnológico](#️-stack-tecnológico)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Workflow de Desarrollo](#-workflow-de-desarrollo)
- [Troubleshooting](#-troubleshooting)
- [Contribuir](#-contribuir)

## ✨ Características

- ✅ **Dashboard en tiempo real** – Monitoreo de consumo instantáneo  
- ✅ **Gráficos interactivos** – Visualización de datos con Matplotlib  
- ✅ **Sistema de alertas** – Notificaciones por alta/baja tensión  
- ✅ **Calendario histórico** – Navegación por consumos pasados  
- ✅ **Reportes PDF** – Generación automática de informes  
- ✅ **Gestión de usuarios** – Roles Admin y Empleado  
- ✅ **Recuperación de contraseña** – Vía email con token temporal  
- ✅ **Notificaciones por email** – Alertas automáticas de consumo  

## 🚀 Instalación

### Requisitos previos

- Python 3.11 o superior  
- pip (gestor de paquetes de Python)  
- Git  

### Pasos de instalación

#### 1. Clonar el repositorio

```bash
git clone https://github.com/shori12/Control-de-Energ-a-.git
cd Control-de-Energ-a-
````

#### 2. Crear entorno virtual

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / Mac**

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 4. Configurar variables de entorno

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # Linux / Mac
```

Editar el archivo `.env`:

```env
EMAIL_SENDER=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password_gmail
EMAIL_RECEIVER=destino@gmail.com
```

📧 **Password de aplicación Gmail**

1. [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Activar **Verificación en 2 pasos**
3. [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Generar contraseña para “Otra aplicación”
5. Copiar el código de 16 caracteres al `.env`

#### 5. Crear base de datos

```bash
python crear_db_sqlite.py
```

Salida esperada:

```text
✅ Base de datos SQLite creada exitosamente
📁 Archivo: energia.db
👤 Usuario admin creado: admin / admin123
```

#### 6. Ejecutar la aplicación

```bash
python main.py
```

## 🔐 Configuración

### Credenciales por defecto

* **Usuario:** `admin`
* **Contraseña:** `admin123`

⚠️ **Cambiar la contraseña luego del primer login**

### Roles

* **Admin:** acceso total
* **Empleado:** visualización, carga de datos y reportes

## 🖥️ Uso

### Dashboard principal

* Consumo instantáneo
* Gráficos temporales y de distribución
* Alertas por tensión
* Estadísticas generales

### Funcionalidades

* 📊 Gráfico de torta por rangos
* 📅 Calendario histórico
* 📄 Generación de reportes PDF
* ➕ Carga manual de datos
* ✏️ Edición de datos (Admin)
* 👥 Gestión de usuarios (Admin)

### Simulador de datos

```bash
python -m BackEnd.collector
```

Genera consumos simulados cada 10 segundos entre **150kW y 500kW**.

## 🛠️ Stack Tecnológico

| Tecnología    | Uso                  |
| ------------- | -------------------- |
| Python 3.13   | Lenguaje principal   |
| CustomTkinter | UI                   |
| SQLite        | Base de datos        |
| Matplotlib    | Gráficos             |
| ReportLab     | PDFs                 |
| bcrypt        | Seguridad            |
| python-dotenv | Variables de entorno |

## 📁 Estructura del Proyecto

```
control-energia/
├── BackEnd/
├── Frontend/
├── main.py
├── config.py
├── crear_db_sqlite.py
├── base1.sql
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🔄 Workflow de Desarrollo

```bash
git checkout main
git pull origin main
```

Crear feature:

```bash
git checkout -b feature/nueva-funcionalidad
```

Commit:

```bash
git add .
git commit -m "✨ feature: nueva funcionalidad"
git push origin feature/nueva-funcionalidad
```

## 🐛 Troubleshooting

**Error CustomTkinter**

```bash
pip install customtkinter
```

**Error base de datos**

```bash
python crear_db_sqlite.py
```

**Error dotenv**

```bash
pip install python-dotenv
```

## 🤝 Contribuir

1. Fork
2. Crear rama
3. Commit
4. Push
5. Pull Request

## 📝 Roadmap

* [ ] PostgreSQL
* [ ] Docker
* [ ] API REST
* [ ] Dashboard Web
* [ ] App móvil
* [ ] Integración con sensores

## 📄 Licencia

MIT License

## 👥 Autores

* **@shori12** – Desarrollo principal
* **Tu nombre** – Colaborador

## 📧 Contacto

Abrir un Issue en GitHub para sugerencias o bugs.

⭐ Si te gustó el proyecto, dejá una estrella

````

---

### 📤 Para subirlo a GitHub

```bash
git add README.md
git commit -m "📝 docs: README completo del proyecto"
git push origin main
````

Si querés, en el próximo mensaje puedo:

* Adaptarlo a **tu usuario/repositorio**
* Agregar **badges** (Python, license, visitors)
* Optimizarlo para **LinkedIn / CV / portfolio**
