#!/usr/bin/env python3
"""
Script de verificación rápida para probar que la aplicación funciona correctamente
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Verificar que todos los módulos se importan correctamente"""
    print("🔍 Verificando imports...")
    try:
        from app import create_app, db
        from config import Config
        from app.services import PaqueteService, DestinoService, ReservaService
        from app.forms.admin_forms import DestinoForm, PaqueteForm
        from app.forms.auth_forms import LoginForm, RegistroForm
        print("✅ Todos los imports son correctos")
        return True
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False

def test_app_creation():
    """Verificar que la aplicación se crea correctamente"""
    print("\n🔍 Verificando creación de aplicación...")
    try:
        from app import create_app
        from config import Config
        app = create_app(Config)
        print(f"✅ Aplicación creada correctamente")
        print(f"   - Debug: {app.config['DEBUG']}")
        print(f"   - Host: {app.config['HOST']}")
        print(f"   - Port: {app.config['PORT']}")
        print(f"   - Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        return True
    except Exception as e:
        print(f"❌ Error al crear aplicación: {e}")
        return False

def test_services():
    """Verificar que los servicios están disponibles"""
    print("\n🔍 Verificando servicios...")
    try:
        from app.services import PaqueteService, DestinoService, ReservaService
        print("✅ Servicios disponibles:")
        print("   - PaqueteService")
        print("   - DestinoService")
        print("   - ReservaService")
        return True
    except Exception as e:
        print(f"❌ Error en servicios: {e}")
        return False

def test_forms():
    """Verificar que los formularios están disponibles"""
    print("\n🔍 Verificando formularios...")
    try:
        from app.forms.admin_forms import DestinoForm, PaqueteForm
        from app.forms.auth_forms import LoginForm, RegistroForm, PerfilForm
        print("✅ Formularios disponibles:")
        print("   - DestinoForm, PaqueteForm")
        print("   - LoginForm, RegistroForm, PerfilForm")
        return True
    except Exception as e:
        print(f"❌ Error en formularios: {e}")
        return False

def test_static_files():
    """Verificar que los archivos estáticos existen"""
    print("\n🔍 Verificando archivos estáticos...")
    static_files = [
        'app/static/js/paquetes.js',
        'app/static/js/carrito.js',
        'app/static/css/custom.css'
    ]
    all_exist = True
    for file_path in static_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} no encontrado")
            all_exist = False
    return all_exist

def main():
    print("=" * 60)
    print("🧪 VERIFICACIÓN DE LA APLICACIÓN FLASK")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Creación de App", test_app_creation()))
    results.append(("Servicios", test_services()))
    results.append(("Formularios", test_forms()))
    results.append(("Archivos Estáticos", test_static_files()))
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{'✅' if passed == total else '⚠️ '} {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("\n🎉 ¡Todo está listo! Puedes ejecutar la aplicación con:")
        print("   python app.py")
        return 0
    else:
        print("\n⚠️  Hay algunos problemas. Revisa los errores arriba.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

