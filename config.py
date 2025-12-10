import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    # SECRET_KEY: usar variable de entorno o valor por defecto solo para desarrollo
    _secret_key = os.environ.get('SECRET_KEY')
    if not _secret_key and os.environ.get('FLASK_ENV') != 'production':
        _secret_key = 'dev-secret-key-cambiar-en-produccion'
    SECRET_KEY = _secret_key
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5001))
    
    # Base de datos - usa .env o fallback a SQLite para desarrollo
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "turismo.db")}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CSRF Protection para WTForms
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('CSRF_SECRET_KEY') or SECRET_KEY
    # Excluir rutas de API de CSRF automáticamente
    WTF_CSRF_EXEMPT_LIST = ['api.carrito', 'api.destinos', 'api.paquetes', 'api.reservas', 'api.buscar']
    
    @staticmethod
    def init_app(app):
        """Validar que las variables críticas estén configuradas en producción"""
        # Solo validar en producción
        if os.environ.get('FLASK_ENV') == 'production' and not Config.SECRET_KEY:
            raise ValueError(
                "SECRET_KEY no está configurada. En producción DEBES crear un archivo .env con SECRET_KEY=tu-clave-secreta-segura"
            )
        elif not Config.SECRET_KEY:
            # En desarrollo, advertir pero permitir
            import warnings
            warnings.warn(
                "⚠️  SECRET_KEY no configurada. Usando valor por defecto (solo para desarrollo). "
                "Crea un archivo .env con SECRET_KEY=tu-clave-secreta para mayor seguridad."
            )
