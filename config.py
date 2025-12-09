import os

class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cambiar-en-produccion'
    HOST = '0.0.0.0'
    PORT = 5001
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Para desarrollo con MySQL/XAMPP (phpMyAdmin)
    # Ajusta usuario/contraseña si no usas root/"".
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+mysqlconnector://root:@localhost/turismo'
    
    # Si quisieras volver a SQLite en el futuro, podrías usar:
    # 'sqlite:///' + os.path.join(basedir, 'turismo.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
