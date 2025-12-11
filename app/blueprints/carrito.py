from flask import Blueprint, request, jsonify, session
from app import csrf
import time
import logging
from app.models.paquete import Paquete

bp = Blueprint('carrito', __name__)

def init_carrito():
    """Inicializa el carrito en la sesión si no existe"""
    if 'carrito' not in session:
        session['carrito'] = {'paquetes': []}

@bp.route('', methods=['GET'])
@csrf.exempt
def obtener_carrito():
    """Obtiene el contenido del carrito"""
    init_carrito()
    carrito = session.get('carrito', {'paquetes': []})
    
    # Obtener detalles completos de los items
    items = []
    total = 0
    
    # Paquetes
    for idx, item in enumerate(carrito.get('paquetes', [])):
        try:
            paquete_id = item.get('id')
            if not paquete_id:
                continue
            paquete = Paquete.query.get(paquete_id)
            if paquete:
                cantidad = item.get('cantidad', 1)
                # Agregar índice único para distinguir items duplicados
                items.append({
                    'tipo': 'paquete',
                    'id': paquete.id,
                    'nombre': paquete.nombre,
                    'origen': paquete.origen or None,  # Incluir origen del paquete
                    'precio': float(paquete.precio_total),
                    'cantidad': cantidad,
                    'subtotal': float(paquete.precio_total) * cantidad,
                    'disponibles': paquete.disponibles,
                    'fecha_inicio': paquete.fecha_inicio.isoformat() if paquete.fecha_inicio else None,
                    'fecha_fin': paquete.fecha_fin.isoformat() if paquete.fecha_fin else None,
                    'destinos': [pd.destino.to_dict() if hasattr(pd.destino, 'to_dict') else {
                        'id': pd.destino.id,
                        'nombre': pd.destino.nombre,
                        'descripcion': pd.destino.descripcion or '',
                        'actividades': pd.destino.actividades.split(',') if pd.destino.actividades else []
                    } for pd in paquete.destinos],  # Incluir información de destinos
                    'carrito_index': idx,  # Índice único en el carrito
                    'timestamp': item.get('timestamp', idx)  # Timestamp único si existe
                })
                total += float(paquete.precio_total) * cantidad
        except Exception as e:
            # Si hay un error con un item, continuar con los demás
            logging.error(f"Error procesando item del carrito (índice {idx}): {e}", exc_info=True)
            continue
    
    return jsonify({
        'items': items,
        'total': total,
        'cantidad': len(items)
    })

@bp.route('/agregar', methods=['POST'])
@csrf.exempt
def agregar_al_carrito():
    """Agrega un item al carrito"""
    # Solo clientes pueden agregar al carrito
    if session.get('usuario_rol') == 'admin':
        return jsonify({'error': 'Los administradores no pueden usar el carrito'}), 403
    
    init_carrito()
    data = request.get_json()
    
    tipo = data.get('tipo')  # 'paquete'
    item_id = data.get('id')
    cantidad = data.get('cantidad', 1)
    
    if not tipo or not item_id:
        return jsonify({'error': 'Tipo e ID son requeridos'}), 400
    
    if tipo != 'paquete':
        return jsonify({'error': 'Solo se pueden agregar paquetes al carrito'}), 400
    
    carrito = session.get('carrito', {'paquetes': []})
    
    if cantidad < 1:
        return jsonify({'error': 'La cantidad debe ser al menos 1'}), 400
    
    # Validar que el paquete existe
    paquete = Paquete.query.get(item_id)
    if not paquete:
        return jsonify({'error': 'Paquete no encontrado'}), 404
    if paquete.disponibles < cantidad:
        return jsonify({'error': f'Solo hay {paquete.disponibles} cupos disponibles'}), 400
    
    # Agregar múltiples items al carrito (uno por cada cantidad)
    items_list = carrito.get(tipo + 's', [])
    
    # Verificar cupos disponibles totales
    if tipo == 'paquete':
        cantidad_actual_en_carrito = sum(item.get('cantidad', 1) for item in items_list if item['id'] == item_id)
        if cantidad_actual_en_carrito + cantidad > paquete.disponibles:
            return jsonify({'error': f'No puedes agregar más. Disponibles: {paquete.disponibles}, Ya en carrito: {cantidad_actual_en_carrito}'}), 400
    
    # Agregar la cantidad especificada como items separados con índice único
    for i in range(cantidad):
        # Agregar timestamp único para distinguir items duplicados
        items_list.append({
            'id': item_id, 
            'cantidad': 1,
            'timestamp': time.time() + i  # Índice único para cada item
        })
    
    carrito[tipo + 's'] = items_list
    session['carrito'] = carrito
    session.modified = True
    
    # Calcular cantidad total de items
    cantidad_total = sum(item.get('cantidad', 1) for item in carrito.get('paquetes', []))
    
    mensaje = f'{cantidad} Paquete{"s" if cantidad > 1 else ""} agregado{"s" if cantidad > 1 else ""} al carrito'
    
    return jsonify({
        'success': True,
        'message': mensaje,
        'cantidad': cantidad_total
    })

@bp.route('/actualizar', methods=['POST'])
@csrf.exempt
def actualizar_cantidad():
    """Actualiza la cantidad de un item en el carrito"""
    init_carrito()
    data = request.get_json()
    
    tipo = data.get('tipo')
    item_id = data.get('id')
    nueva_cantidad = data.get('cantidad')
    
    if not tipo or not item_id or nueva_cantidad is None:
        return jsonify({'error': 'Tipo, ID y cantidad son requeridos'}), 400
    
    if nueva_cantidad < 1:
        return jsonify({'error': 'La cantidad debe ser al menos 1'}), 400
    
    if tipo != 'paquete':
        return jsonify({'error': 'Solo se pueden actualizar paquetes'}), 400
    
    carrito = session.get('carrito', {'paquetes': []})
    items_list = carrito.get(tipo + 's', [])
    item_existente = next((item for item in items_list if item['id'] == item_id), None)
    
    if not item_existente:
        return jsonify({'error': 'Item no encontrado en el carrito'}), 404
    
    # Validar disponibilidad para paquetes
    if tipo == 'paquete':
        paquete = Paquete.query.get(item_id)
        if not paquete:
            return jsonify({'error': 'Paquete no encontrado'}), 404
        if nueva_cantidad > paquete.disponibles:
            return jsonify({'error': f'Solo hay {paquete.disponibles} cupos disponibles'}), 400
    
    # Actualizar cantidad
    item_existente['cantidad'] = nueva_cantidad
    carrito[tipo + 's'] = items_list
    session['carrito'] = carrito
    session.modified = True
    
    # Calcular cantidad total de items
    cantidad_total = sum(item.get('cantidad', 1) for item in carrito.get('paquetes', []))
    
    return jsonify({
        'success': True,
        'message': 'Cantidad actualizada',
        'cantidad': cantidad_total
    })

@bp.route('/eliminar', methods=['POST'])
@csrf.exempt
def eliminar_del_carrito():
    """Elimina un item del carrito usando timestamp o índice"""
    init_carrito()
    data = request.get_json()
    
    tipo = data.get('tipo')
    item_id = data.get('id')
    timestamp = data.get('timestamp')  # Timestamp único del item
    carrito_index = data.get('carrito_index')  # Índice alternativo
    
    if not tipo or not item_id:
        return jsonify({'error': 'Tipo e ID son requeridos'}), 400
    
    if tipo != 'paquete':
        return jsonify({'error': 'Solo se pueden eliminar paquetes'}), 400
    
    carrito = session.get('carrito', {'paquetes': []})
    items_list = carrito.get(tipo + 's', [])
    
    # Eliminar el item específico usando timestamp o índice
    item_eliminado = False
    nueva_lista = []
    for idx, item in enumerate(items_list):
        if item['id'] == item_id:
            # Si hay timestamp, usar ese para identificar el item exacto
            if timestamp is not None and item.get('timestamp') == timestamp:
                item_eliminado = True
                continue
            # Si hay carrito_index, usar ese
            elif carrito_index is not None and idx == carrito_index:
                item_eliminado = True
                continue
            # Si no hay identificadores únicos, eliminar el primero encontrado
            elif timestamp is None and carrito_index is None and not item_eliminado:
                item_eliminado = True
                continue
        nueva_lista.append(item)
    
    if not item_eliminado:
        return jsonify({'error': 'Item no encontrado en el carrito'}), 404
    
    carrito[tipo + 's'] = nueva_lista
    session['carrito'] = carrito
    session.modified = True
    
    # Calcular cantidad total de items
    cantidad_total = sum(item.get('cantidad', 1) for item in carrito.get('paquetes', []))
    
    return jsonify({
        'success': True,
        'message': 'Paquete eliminado del carrito',
        'cantidad': cantidad_total
    })

@bp.route('/limpiar', methods=['POST'])
@csrf.exempt
def limpiar_carrito():
    """Limpia todo el carrito"""
    session['carrito'] = {'paquetes': []}
    session.modified = True
    return jsonify({'success': True, 'message': 'Carrito limpiado'})

@bp.route('/cantidad', methods=['GET'])
@csrf.exempt
def cantidad_carrito():
    """Obtiene la cantidad de items en el carrito"""
    init_carrito()
    carrito = session.get('carrito', {'paquetes': []})
    cantidad = sum(item.get('cantidad', 1) for item in carrito.get('paquetes', []))
    return jsonify({'cantidad': cantidad})
