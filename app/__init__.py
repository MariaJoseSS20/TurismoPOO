from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    
    # Agregar headers CORS para todas las respuestas
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    from app.blueprints.web import bp as web_bp
    app.register_blueprint(web_bp)
    
    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.blueprints.destinos import bp as destinos_bp
    app.register_blueprint(destinos_bp, url_prefix='/api/destinos')
    
    from app.blueprints.paquetes import bp as paquetes_bp
    app.register_blueprint(paquetes_bp, url_prefix='/api/paquetes')
    
    from app.blueprints.reservas import bp as reservas_bp
    app.register_blueprint(reservas_bp, url_prefix='/api/reservas')
    
    from app.blueprints.buscar import bp as buscar_bp
    app.register_blueprint(buscar_bp, url_prefix='/api/buscar')
    
    from app.blueprints.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.blueprints.carrito import bp as carrito_bp
    app.register_blueprint(carrito_bp, url_prefix='/api/carrito')
    
    from app.models import Usuario, Destino, Paquete, Reserva, Viajero
    
    # Handlers de error
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('web/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('web/500.html'), 500
    
    with app.app_context():
        db.create_all()
    
    return app

