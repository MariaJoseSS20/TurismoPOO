"""
Punto de entrada de la aplicación Flask
Usa Application Factory Pattern para crear la app
"""
from app import create_app
from config import Config

# Crear la aplicación usando el factory
app = create_app(Config)

if __name__ == '__main__':
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )
