from flask import Blueprint, request, jsonify
from app import db, csrf
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
@csrf.exempt
def crear():
    """API pública para crear destino (usa servicio)"""
    try:
        data = request.get_json()
        if not data or not data.get('nombre') or not data.get('costo_base'):
            return jsonify({'error': 'Nombre y costo_base requeridos'}), 400
        
        actividades = ','.join(data.get('actividades', [])) if isinstance(data.get('actividades'), list) else data.get('actividades')
        
        from app.services.destino_service import DestinoService
        datos = {
            'nombre': data['nombre'],
            'origen': data.get('origen'),
            'descripcion': data.get('descripcion'),
            'actividades': actividades,
            'costo_base': data['costo_base']
        }
        destino = DestinoService.crear_destino(datos)
        return jsonify(destino.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['PUT'])
@csrf.exempt
def actualizar(id):
    """API pública para actualizar destino (usa servicio)"""
    try:
        from app.services.destino_service import DestinoService
        from app.models.destino import Destino
        data = request.get_json()
        
        # Obtener destino existente para validar campos obligatorios
        destino_existente = Destino.query.get_or_404(id)
        
        actividades = data.get('actividades')
        if actividades and isinstance(actividades, list):
            actividades = ','.join(actividades)
        
        # Validar que descripción y actividades no estén vacíos
        descripcion = data.get('descripcion', destino_existente.descripcion)
        if descripcion:
            descripcion = descripcion.strip()
        if not descripcion:
            return jsonify({'error': 'La descripción es obligatoria'}), 400
        
        if actividades is not None:
            actividades = actividades.strip() if actividades else ''
        else:
            actividades = destino_existente.actividades or ''
        if not actividades:
            return jsonify({'error': 'Las actividades son obligatorias'}), 400
        
        datos = {}
        if 'nombre' in data:
            datos['nombre'] = data['nombre']
        if 'origen' in data:
            datos['origen'] = data['origen']
        datos['descripcion'] = descripcion
        datos['actividades'] = actividades
        if 'costo_base' in data:
            datos['costo_base'] = data['costo_base']
        
        destino = DestinoService.actualizar_destino(id, datos)
        return jsonify(destino.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@csrf.exempt
def eliminar(id):
    """API pública para eliminar destino (usa servicio)"""
    try:
        from app.services.destino_service import DestinoService
        DestinoService.eliminar_destino(id)
        return jsonify({'mensaje': 'Eliminado'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

