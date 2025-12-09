from flask import Blueprint, request, jsonify, session
from app import db
from app.models.reserva import Reserva
from app.models.paquete import Paquete
from app.models.viajero import Viajero
from datetime import datetime

bp = Blueprint('reservas', __name__)

@bp.route('', methods=['GET'])
def listar():
    return jsonify([r.to_dict() for r in Reserva.query.all()])

@bp.route('/<int:id>', methods=['GET'])
def obtener(id):
    return jsonify(Reserva.query.get_or_404(id).to_dict())

@bp.route('', methods=['POST'])
def crear():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Debes iniciar sesión'}), 401
    
    data = request.get_json()
    if not data or not data.get('paquete_id'):
        return jsonify({'error': 'paquete_id requerido'}), 400
    
    usuario_id = session['usuario_id']
    
    paquete = Paquete.query.get_or_404(data['paquete_id'])
    numero_pasajeros = data.get('numero_pasajeros', 1)
    
    if numero_pasajeros < 1:
        return jsonify({'error': 'El número de pasajeros debe ser al menos 1'}), 400
    
    if paquete.disponibles < numero_pasajeros:
        return jsonify({'error': f'No hay suficientes cupos disponibles. Disponibles: {paquete.disponibles}, Solicitados: {numero_pasajeros}'}), 400
    
    reserva = Reserva(
        usuario_id=usuario_id,
        paquete_id=data['paquete_id'],
        estado=data.get('estado', 'confirmada'),
        numero_pasajeros=numero_pasajeros,
        telefono_contacto=data.get('telefono_contacto'),
        comentarios=data.get('comentarios')
    )
    paquete.disponibles -= numero_pasajeros
    db.session.add(reserva)
    db.session.flush()  # Para obtener el ID de la reserva
    
    # Guardar datos de viajeros si se proporcionan
    viajeros_data = data.get('viajeros', [])
    if viajeros_data and len(viajeros_data) > 0:
        for viajero_data in viajeros_data:
            fecha_nacimiento = None
            if viajero_data.get('fecha_nacimiento'):
                try:
                    fecha_nacimiento = datetime.strptime(viajero_data['fecha_nacimiento'], '%Y-%m-%d').date()
                except:
                    pass
            
            viajero = Viajero(
                reserva_id=reserva.id,
                nombre_completo=viajero_data.get('nombre_completo', ''),
                rut=viajero_data.get('rut', ''),
                fecha_nacimiento=fecha_nacimiento,
                telefono=viajero_data.get('telefono'),
                email=viajero_data.get('email')
            )
            db.session.add(viajero)
    
    db.session.commit()
    return jsonify(reserva.to_dict()), 201

@bp.route('/<int:id>', methods=['PUT'])
def actualizar(id):
    reserva = Reserva.query.get_or_404(id)
    data = request.get_json()
    estado_anterior = reserva.estado
    
    if 'estado' in data:
        reserva.estado = data['estado']
        if estado_anterior == 'confirmada' and data['estado'] == 'cancelada':
            reserva.paquete.disponibles += reserva.numero_pasajeros
        elif estado_anterior == 'cancelada' and data['estado'] == 'confirmada':
            if reserva.paquete.disponibles >= reserva.numero_pasajeros:
                reserva.paquete.disponibles -= reserva.numero_pasajeros
            else:
                return jsonify({'error': 'Sin cupos suficientes'}), 400
    db.session.commit()
    return jsonify(reserva.to_dict())

@bp.route('/<int:id>', methods=['DELETE'])
def eliminar(id):
    reserva = Reserva.query.get_or_404(id)
    if reserva.estado == 'confirmada':
        reserva.paquete.disponibles += reserva.numero_pasajeros
    db.session.delete(reserva)
    db.session.commit()
    return jsonify({'mensaje': 'Eliminado'}), 200

@bp.route('/usuario/<int:usuario_id>', methods=['GET'])
def por_usuario(usuario_id):
    return jsonify([r.to_dict() for r in Reserva.query.filter_by(usuario_id=usuario_id).all()])

