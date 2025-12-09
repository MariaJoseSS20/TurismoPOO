from flask import Blueprint, request, jsonify
from app import db
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
            hoy = date.today()
            paquetes = Paquete.query.options(
                joinedload(Paquete.destinos).joinedload(PaqueteDestino.destino)
            ).filter(
                Paquete.disponibles > 0,  # Con cupos disponibles
                Paquete.fecha_inicio >= hoy  # Fechas futuras o de hoy
            ).order_by(
                Paquete.disponibles.desc(),  # Más cupos primero
                Paquete.fecha_inicio.asc()   # Fechas más cercanas primero
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
def crear():
    data = request.get_json()
    if not data or not data.get('nombre') or not data.get('fecha_inicio') or not data.get('fecha_fin'):
        return jsonify({'error': 'Nombre, fecha_inicio y fecha_fin requeridos'}), 400
    
    paquete = Paquete(
        nombre=data['nombre'],
        origen=data.get('origen'),
        fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date(),
        fecha_fin=datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date(),
        precio_total=data.get('precio_total', 0),
        disponibles=data.get('disponibles', 20)
    )
    db.session.add(paquete)
    db.session.flush()
    
    if 'destinos' in data:
        for destino_id in data['destinos']:
            if Destino.query.get(destino_id):
                db.session.add(PaqueteDestino(paquete_id=paquete.id, destino_id=destino_id))
    
    db.session.commit()
    return jsonify(paquete.to_dict()), 201

@bp.route('/<int:id>', methods=['PUT'])
def actualizar(id):
    paquete = Paquete.query.get_or_404(id)
    data = request.get_json()
    if 'nombre' in data:
        paquete.nombre = data['nombre']
    if 'origen' in data:
        paquete.origen = data['origen']
    if 'fecha_inicio' in data:
        paquete.fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
    if 'fecha_fin' in data:
        paquete.fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
    if 'precio_total' in data:
        paquete.precio_total = data['precio_total']
    if 'disponibles' in data:
        paquete.disponibles = data['disponibles']
    db.session.commit()
    return jsonify(paquete.to_dict())

@bp.route('/<int:id>', methods=['DELETE'])
def eliminar(id):
    db.session.delete(Paquete.query.get_or_404(id))
    db.session.commit()
    return jsonify({'mensaje': 'Eliminado'}), 200

