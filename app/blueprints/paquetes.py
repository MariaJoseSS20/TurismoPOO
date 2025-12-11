from flask import Blueprint, request, jsonify
from app import db, csrf
from app.models.paquete import Paquete, PaqueteDestino
from app.models.destino import Destino
from sqlalchemy.orm import joinedload
from datetime import datetime, date

bp = Blueprint('paquetes', __name__)

@bp.route('', methods=['GET'])
def listar():
    try:
        destacados = request.args.get('destacados', '').lower() == 'true'
        
        if destacados:
            # Retornar solo paquetes destacados con criterios automáticos
            # Mostrar paquetes con cupos disponibles, priorizando fechas futuras
            hoy = date.today()
            paquetes = Paquete.query.options(
                joinedload(Paquete.destinos).joinedload(PaqueteDestino.destino)
            ).filter(
                Paquete.disponibles > 0  # Con cupos disponibles
            ).order_by(
                Paquete.fecha_inicio.desc(),  # Fechas más recientes primero (futuras o pasadas)
                Paquete.disponibles.desc()    # Más cupos primero
            ).limit(6).all()  # Máximo 6 paquetes
        else:
            # Retornar todos los paquetes
            paquetes = Paquete.query.options(
                joinedload(Paquete.destinos).joinedload(PaqueteDestino.destino)
            ).all()
        
        return jsonify([p.to_dict() for p in paquetes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['GET'])
def obtener(id):
    return jsonify(Paquete.query.get_or_404(id).to_dict())

@bp.route('', methods=['POST'])
@csrf.exempt
def crear():
    """API pública para crear paquete (usa servicio)"""
    try:
        from app.services.paquete_service import PaqueteService
        data = request.get_json()
        if not data or not data.get('nombre') or not data.get('fecha_inicio') or not data.get('fecha_fin'):
            return jsonify({'error': 'Nombre, fecha_inicio y fecha_fin requeridos'}), 400
        
        datos = {
            'nombre': data['nombre'],
            'origen': data.get('origen'),
            'fecha_inicio': datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date(),
            'fecha_fin': datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date(),
            'precio_total': data.get('precio_total', 0),
            'disponibles': data.get('disponibles', 20),
            'destinos': data.get('destinos', [])
        }
        paquete = PaqueteService.crear_paquete(datos)
        return jsonify(paquete.to_dict()), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['PUT'])
@csrf.exempt
def actualizar(id):
    """API pública para actualizar paquete (usa servicio)"""
    try:
        from app.services.paquete_service import PaqueteService
        data = request.get_json()
        
        datos = {}
        if 'nombre' in data:
            datos['nombre'] = data['nombre']
        if 'origen' in data:
            datos['origen'] = data['origen']
        if 'fecha_inicio' in data:
            datos['fecha_inicio'] = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
        if 'fecha_fin' in data:
            datos['fecha_fin'] = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
        if 'precio_total' in data:
            datos['precio_total'] = data['precio_total']
        if 'disponibles' in data:
            datos['disponibles'] = data['disponibles']
        if 'destinos' in data:
            datos['destinos'] = data['destinos']
        
        paquete = PaqueteService.actualizar_paquete(id, datos)
        return jsonify(paquete.to_dict())
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@csrf.exempt
def eliminar(id):
    """API pública para eliminar paquete (usa servicio)"""
    try:
        from app.services.paquete_service import PaqueteService
        PaqueteService.eliminar_paquete(id)
        return jsonify({'mensaje': 'Eliminado'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

