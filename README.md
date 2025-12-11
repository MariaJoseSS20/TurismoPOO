# Sistema de Gestión de Viajes

Sistema web desarrollado con Flask para la gestión de destinos turísticos, paquetes de viaje y reservas.

## Requisitos del Sistema

- Python 3.8 o superior
- MySQL (recomendado XAMPP con phpMyAdmin)
- Navegador web moderno

## Instalación

### 1. Clonar o descargar el proyecto

Descargar el proyecto y extraerlo en una carpeta.

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar base de datos

1. Iniciar XAMPP y asegurarse de que MySQL esté corriendo
2. Crear una base de datos llamada `turismo` en phpMyAdmin
3. Verificar la configuración en `config.py` (usuario y contraseña de MySQL)

### 6. Inicializar base de datos

```bash
python init_db.py
```

Esto creará todas las tablas necesarias en la base de datos.

### 7. (Opcional) Crear datos de ejemplo

```bash
python crear_datos_ejemplo.py
```

Esto insertará datos de prueba en la base de datos.

## Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://127.0.0.1:5001`

## Credenciales de ejemplo

Si ejecutaste `crear_datos_ejemplo.py`, puedes usar:

**Administrador:**
- Email: `admin@viajesaventura.com`
- Contraseña: `admin123`

**Cliente:**
- Email: `maria@administrador.com`
- Contraseña: `123456`

## Estructura del Proyecto

```
POO/
├── app/
│   ├── __init__.py          # Application Factory
│   ├── blueprints/           # Módulos de rutas
│   │   ├── auth.py          # Autenticación
│   │   ├── admin.py         # Panel administrador
│   │   ├── web.py           # Rutas públicas
│   │   ├── destinos.py      # API destinos
│   │   ├── paquetes.py      # API paquetes
│   │   ├── reservas.py      # API reservas
│   │   └── carrito.py       # API carrito
│   ├── models/              # Modelos de base de datos
│   │   ├── usuario.py
│   │   ├── destino.py
│   │   ├── paquete.py
│   │   ├── reserva.py
│   │   └── viajero.py
│   └── templates/           # Plantillas HTML
│       └── web/
├── config.py                # Configuración
├── app.py                   # Punto de entrada
├── init_db.py              # Script inicialización BD
├── crear_datos_ejemplo.py  # Script datos de prueba
└── requirements.txt        # Dependencias Python
```

## Funcionalidades

- Sistema de autenticación (registro, login, logout)
- Gestión de destinos turísticos
- Gestión de paquetes de viaje
- Carrito de compras
- Sistema de reservas con múltiples viajeros
- Panel de administración
- Búsqueda en tiempo real

## Tecnologías Utilizadas

- **Backend**: Flask 3.0.0
- **Base de Datos**: MySQL con SQLAlchemy
- **Frontend**: Bootstrap 5, JavaScript (Vanilla)
- **Autenticación**: Werkzeug Security

## Notas

- Asegúrate de tener MySQL corriendo antes de ejecutar la aplicación
- El archivo `config.py` contiene la configuración de conexión a la base de datos
- Para producción, cambiar `SECRET_KEY` en `config.py`


