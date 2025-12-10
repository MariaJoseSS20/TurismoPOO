#!/usr/bin/env python3
"""
Script interactivo para configurar la conexión a MySQL
"""
import os
import sys

def crear_archivo_env():
    """Crear archivo .env con configuración MySQL"""
    
    print("=" * 60)
    print("🔧 CONFIGURACIÓN DE MYSQL")
    print("=" * 60)
    print()
    
    # Verificar si ya existe .env
    if os.path.exists('.env'):
        respuesta = input("⚠️  El archivo .env ya existe. ¿Deseas sobrescribirlo? (s/n): ")
        if respuesta.lower() != 's':
            print("❌ Operación cancelada.")
            return
    
    print("Por favor, proporciona la siguiente información:")
    print()
    
    # Solicitar datos de conexión
    usuario = input("Usuario MySQL (típicamente 'root'): ").strip() or 'root'
    contraseña = input("Contraseña MySQL (presiona Enter si no tienes): ").strip()
    host = input("Host MySQL (presiona Enter para 'localhost'): ").strip() or 'localhost'
    puerto = input("Puerto MySQL (presiona Enter para '3306'): ").strip() or '3306'
    nombre_bd = input("Nombre de la base de datos (presiona Enter para 'turismo'): ").strip() or 'turismo'
    
    # Construir URL de conexión
    if contraseña:
        database_url = f"mysql+mysqlconnector://{usuario}:{contraseña}@{host}:{puerto}/{nombre_bd}"
    else:
        database_url = f"mysql+mysqlconnector://{usuario}@{host}:{puerto}/{nombre_bd}"
    
    # Generar SECRET_KEY
    import secrets
    secret_key = secrets.token_urlsafe(32)
    csrf_secret = secrets.token_urlsafe(32)
    
    # Crear contenido del archivo .env
    contenido = f"""# Configuración de Base de Datos MySQL
DATABASE_URL={database_url}

# Configuración de Flask
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

# Seguridad (claves generadas automáticamente)
SECRET_KEY={secret_key}
CSRF_SECRET_KEY={csrf_secret}
"""
    
    # Escribir archivo
    try:
        with open('.env', 'w') as f:
            f.write(contenido)
        
        print()
        print("=" * 60)
        print("✅ ARCHIVO .env CREADO EXITOSAMENTE")
        print("=" * 60)
        print()
        print("📋 Configuración guardada:")
        print(f"   Base de datos: {nombre_bd}")
        print(f"   Usuario: {usuario}")
        print(f"   Host: {host}:{puerto}")
        print()
        print("📝 PRÓXIMOS PASOS:")
        print()
        print("1. Asegúrate de que MySQL esté corriendo")
        print("2. Crea la base de datos en phpMyAdmin:")
        print(f"   - Nombre: {nombre_bd}")
        print("   - Codificación: utf8mb4_unicode_ci")
        print()
        print("3. Aplica las migraciones:")
        print("   flask db upgrade")
        print()
        print("4. Crea datos de ejemplo:")
        print("   python agregar_datos_ejemplo.py")
        print()
        
    except Exception as e:
        print(f"❌ Error al crear archivo .env: {e}")
        sys.exit(1)

if __name__ == '__main__':
    crear_archivo_env()

