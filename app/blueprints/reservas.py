from flask import Blueprint, request, jsonify, session
from app import db, csrf
from app.models.reserva import Reserva
from app.models.paquete import Paquete
from app.models.viajero import Viajero
from app.services.reserva_service import ReservaService
from datetime import datetime

bp = Blueprint('reservas', __name__)

@bp.route('', methods=['GET'])
def listar():
    return jsonify([r.to_dict() for r in Reserva.query.all()])

@bp.route('/<int:id>', methods=['GET'])
def obtener(id):
    return jsonify(Reserva.query.get_or_404(id).to_dict())

@bp.route('', methods=['POST'])
@csrf.exempt
def crear():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Debes iniciar sesión'}), 401
    
    data = request.get_json()
    if not data or not data.get('paquete_id'):
        return jsonify({'error': 'paquete_id requerido'}), 400
    
    try:
        usuario_id = session['usuario_id']
        reserva = ReservaService.crear_reserva(usuario_id, data)
        return jsonify(reserva.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear reserva: {str(e)}'}), 500

@bp.route('/<int:id>', methods=['PUT'])
@csrf.exempt
def actualizar(id):
    data = request.get_json()
    
    if 'estado' not in data:
        return jsonify({'error': 'El campo estado es requerido'}), 400
    
    try:
        reserva = ReservaService.actualizar_estado_reserva(id, data['estado'])
        return jsonify(reserva.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar reserva: {str(e)}'}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@csrf.exempt
def eliminar(id):
    try:
        mensaje = ReservaService.eliminar_reserva(id)
        return jsonify({'mensaje': mensaje}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar reserva: {str(e)}'}), 500

@bp.route('/usuario/<int:usuario_id>', methods=['GET'])
def por_usuario(usuario_id):
    return jsonify([r.to_dict() for r in Reserva.query.filter_by(usuario_id=usuario_id).all()])

