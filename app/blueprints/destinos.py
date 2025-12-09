from flask import Blueprint, request, jsonify
from app import db
from app.models.destino import Destino

bp = Blueprint('destinos', __name__)

@bp.route('', methods=['GET'])
def listar():
    try:
        destacados = request.args.get('destacados', '').lower() == 'true'
        
        if destacados:
            # Retornar solo destinos destacados (los más usados en paquetes o los primeros)
            from app.models.paquete import PaqueteDestino
            from sqlalchemy import func
            
            destinos = []
            
            # Intentar obtener destinos que están en más paquetes (más populares)
            try:
                destinos = Destino.query.join(PaqueteDestino).group_by(Destino.id).order_by(
                    func.count(PaqueteDestino.paquete_id).desc()
                ).limit(6).all()
            except:
                pass
            
            # Si hay menos de 6 con paquetes, completar con los primeros destinos
            if len(destinos) < 6:
                todos_destinos = Destino.query.limit(6).all()
                ids_existentes = {d.id for d in destinos}
                for destino in todos_destinos:
                    if destino.id not in ids_existentes and len(destinos) < 6:
                        destinos.append(destino)
        else:
            # Retornar todos los destinos
            destinos = Destino.query.all()
        
        return jsonify([d.to_dict() for d in destinos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['GET'])
def obtener(id):
    return jsonify(Destino.query.get_or_404(id).to_dict())

@bp.route('', methods=['POST'])
def crear():
    data = request.get_json()
    if not data or not data.get('nombre') or not data.get('costo_base'):
        return jsonify({'error': 'Nombre y costo_base requeridos'}), 400
    
    actividades = ','.join(data.get('actividades', [])) if isinstance(data.get('actividades'), list) else data.get('actividades')
    destino = Destino(
        nombre=data['nombre'],
        origen=data.get('origen'),
        descripcion=data.get('descripcion'),
        actividades=actividades,
        costo_base=data['costo_base']
    )
    db.session.add(destino)
    db.session.commit()
    return jsonify(destino.to_dict()), 201

@bp.route('/<int:id>', methods=['PUT'])
def actualizar(id):
    destino = Destino.query.get_or_404(id)
    data = request.get_json()
    if 'nombre' in data:
        destino.nombre = data['nombre']
    if 'origen' in data:
        destino.origen = data['origen']
    if 'descripcion' in data:
        destino.descripcion = data['descripcion']
    if 'actividades' in data:
        destino.actividades = ','.join(data['actividades']) if isinstance(data['actividades'], list) else data['actividades']
    if 'costo_base' in data:
        destino.costo_base = data['costo_base']
    db.session.commit()
    return jsonify(destino.to_dict())

@bp.route('/<int:id>', methods=['DELETE'])
def eliminar(id):
    db.session.delete(Destino.query.get_or_404(id))
    db.session.commit()
    return jsonify({'mensaje': 'Eliminado'}), 200

