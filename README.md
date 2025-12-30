# 🔌 Sistema de Control de Energía

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
```

#### 2. Crear entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

**Si `pip` no funciona, usar:**
```bash
python -m pip install -r requirements.txt
```

**Verificar instalación:**
```bash
python -m pip list
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

📧 **Obtener password de aplicación Gmail:**

1. Ir a: https://myaccount.google.com/security
2. Activar **Verificación en 2 pasos**
3. Ir a: https://myaccount.google.com/apppasswords
4. Generar contraseña para "Otra aplicación"
5. Copiar el código de 16 caracteres al `.env`

#### 5. Crear base de datos
```bash
python crear_db_sqlite.py
```

**Salida esperada:**
```text
✅ Base de datos SQLite creada exitosamente!
📁 Archivo: energia.db
👤 Usuario admin creado: admin / admin123
```

#### 6. Ejecutar la aplicación
```bash
python main.py
```

## 🔐 Configuración

### Credenciales por defecto

- **Usuario:** `admin`
- **Contraseña:** `admin123`

⚠️ **IMPORTANTE:** Cambiar la contraseña después del primer login por seguridad.

### Roles de usuario

- **Admin:** Acceso completo (gestión de usuarios, modificación de datos, todas las funcionalidades)
- **Empleado:** Visualización, agregar datos, generar reportes (sin gestión de usuarios ni modificación)

## 🖥️ Uso

### Dashboard principal

- Consumo instantáneo en tiempo real
- Gráficos temporales y de distribución
- Sistema de alertas por tensión
- Estadísticas generales (promedios, máximos, mínimos)

### Funcionalidades principales

- 📊 **Gráfico de torta** - Distribución por rangos de consumo
- 📅 **Calendario histórico** - Navegación por fechas pasadas
- 📄 **Reportes PDF** - Generación automática de informes
- ➕ **Carga manual** - Ingreso de datos manualmente
- ✏️ **Edición de datos** - Corrección de lecturas (solo Admin)
- 👥 **Gestión de usuarios** - Crear/editar/activar usuarios (solo Admin)

### Simulador de datos

Para generar lecturas automáticas cada 10 segundos:
```bash
python -m BackEnd.collector
```

Esto simulará consumos entre **150kW y 500kW**.

## 🛠️ Stack Tecnológico

| Tecnología | Uso |
|------------|-----|
| **Python 3.13** | Lenguaje principal |
| **CustomTkinter** | Interfaz gráfica |
| **SQLite** | Base de datos |
| **Matplotlib** | Gráficos |
| **ReportLab** | Generación de PDFs |
| **bcrypt** | Encriptación de contraseñas |
| **python-dotenv** | Variables de entorno |

## 📁 Estructura del Proyecto
```
control-energia/
├── BackEnd/
│   ├── conexion.py              # Conexión a BD
│   ├── consulta.py              # Lógica de negocio
│   ├── collector.py             # Simulador de datos
│   └── notification_service.py  # Notificaciones email
├── Frontend/
│   ├── login_view.py            # Pantalla login
│   ├── registro.py              # Registro usuarios
│   ├── password_reset_view.py   # Recuperar contraseña
│   ├── app.py                   # Dashboard principal
│   └── assets/                  # Recursos (imágenes)
├── main.py                      # Punto de entrada
├── config.py                    # Configuración
├── crear_db_sqlite.py           # Script BD inicial
├── requirements.txt             # Dependencias
├── .env.example                 # Plantilla config
├── .gitignore                   # Archivos ignorados
└── README.md                    # Este archivo
```

## 🔄 Workflow de Desarrollo

### Setup inicial para colaboradores
```bash
# 1. Clonar repositorio
git clone https://github.com/shori12/Control-de-Energ-a-.git
cd Control-de-Energ-a-

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
python -m pip install -r requirements.txt

# 4. Configurar .env
copy .env.example .env
# Editar .env con tus credenciales

# 5. Crear base de datos
python crear_db_sqlite.py

# 6. Ejecutar
python main.py
```

### Trabajo diario

#### Antes de empezar cada día:
```bash
git checkout main
git pull origin main
```

#### Crear nueva funcionalidad:
```bash
# 1. Crear rama descriptiva
git checkout -b feature/nombre-funcionalidad

# Ejemplos de nombres:
# feature/exportar-excel
# feature/mejorar-alertas
# bugfix/corregir-login

# 2. Desarrollar y probar

# 3. Guardar cambios
git add .
git commit -m "✨ Descripción clara de cambios"

# 4. Subir rama
git push origin feature/nombre-funcionalidad

# 5. Crear Pull Request en GitHub

# 6. Esperar code review

# 7. Después del merge:
git checkout main
git pull origin main
git branch -d feature/nombre-funcionalidad
```

### Convenciones de commits
```
✨ feature: Nueva funcionalidad
🐛 fix: Corrección de bug
📝 docs: Documentación
🎨 style: Formato/estilo
♻️ refactor: Refactorización
⚡ perf: Mejora de rendimiento
✅ test: Tests
🔧 chore: Mantenimiento
🔒 security: Seguridad
```

### Manejo de conflictos

Si aparece conflicto al hacer `git pull`:
```bash
# 1. Git mostrará los archivos en conflicto
git status

# 2. Abrir archivo conflictivo
# Buscar las marcas:
<<<<<<< HEAD
tu código
=======
código del otro
>>>>>>> origin/main

# 3. Decidir qué mantener y borrar marcas

# 4. Guardar archivo

# 5. Marcar como resuelto
git add archivo_resuelto.py

# 6. Completar merge
git commit -m "🔧 Resuelvo conflicto en archivo.py"

# 7. Subir
git push origin main
```

## 🐛 Troubleshooting

### Error: `pip` no se reconoce como comando

**Problema:** Windows no encuentra el comando `pip`

**Soluciones:**

1. **Usar python -m pip (RECOMENDADO):**
```bash
python -m pip install -r requirements.txt
```

2. **Verificar Python en PATH:**
```bash
# Ver dónde está Python
where python

# Debería mostrar algo como:
# C:\Users\TuUsuario\AppData\Local\Programs\Python\Python313\python.exe
```

3. **Reinstalar Python con PATH:**
   - Descargar: https://www.python.org/downloads/
   - Al instalar: ✅ **Marcar "Add Python to PATH"**

### Error: `No module named 'customtkinter'`
```bash
python -m pip install customtkinter
```

### Error: `Can't open database` o `energia.db not found`
```bash
# Regenerar base de datos
python crear_db_sqlite.py
```

### Error: `ModuleNotFoundError: No module named 'dotenv'`
```bash
python -m pip install python-dotenv
```

### La interfaz no se ve correctamente
```bash
# Reinstalar customtkinter
python -m pip uninstall customtkinter
python -m pip install customtkinter
```

### Error: Variables de entorno no cargadas

1. Verificar que existe `.env` en la raíz del proyecto
2. Verificar que `.env` tiene el formato correcto:
```env
EMAIL_SENDER=tu@email.com
EMAIL_PASSWORD=password
EMAIL_RECEIVER=destino@email.com
```
3. Verificar que `python-dotenv` está instalado:
```bash
python -m pip install python-dotenv
```

### Error al hacer `git pull`: conflictos

Ver sección [Manejo de conflictos](#manejo-de-conflictos) en Workflow.

## 🤝 Contribuir

### Cómo contribuir

1. **Fork** el proyecto
2. Crear rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m '✨ Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir **Pull Request**

### Guidelines

- ✅ Código limpio y comentado
- ✅ Seguir PEP 8 (Python)
- ✅ Actualizar documentación si es necesario
- ✅ Probar funcionalidad antes de PR
- ✅ Mensajes de commit descriptivos

## 📝 Roadmap

- [ ] Migración a PostgreSQL para producción
- [ ] Deployment en Railway/Render
- [ ] Tests unitarios (pytest)
- [ ] Docker containerization
- [ ] API REST (FastAPI)
- [ ] Dashboard web (React)
- [ ] App móvil (React Native)
- [ ] Integración con sensores reales
- [ ] Sistema de backup automático
- [ ] Multi-idioma (i18n)

## 📄 Licencia

MIT License

## 👥 Autores

- **[@shori12](https://github.com/shori12)** - Desarrollo principal
- **[@Vladimir-Bulan](https://github.com/Vladimir-Bulan)** - Colaborador

## 📧 Contacto

Para bugs o sugerencias, abrir un [Issue](https://github.com/shori12/Control-de-Energ-a-/issues) en GitHub.

---

⭐ Si te gustó el proyecto, dejá una estrella en GitHub!

**Made with ❤️ by the FN-MUDAD Team**