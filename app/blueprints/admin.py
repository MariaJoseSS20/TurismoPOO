from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import db
from sqlalchemy import or_, func
from app.models.usuario import Usuario
from app.models.destino import Destino
from app.models.paquete import Paquete, PaqueteDestino
from app.models.reserva import Reserva
from functools import wraps
from datetime import datetime

bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorador para proteger rutas de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión', 'warning')
            return redirect(url_for('auth.login'))
        
        # Verificar rol en la base de datos (más seguro que solo la sesión)
        usuario = Usuario.query.get(session.get('usuario_id'))
        if not usuario or usuario.rol != 'admin':
            flash('Acceso denegado. Solo administradores pueden acceder.', 'danger')
            return redirect(url_for('web.index'))
        
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@admin_required
def dashboard():
    """Dashboard principal del administrador"""
    total_destinos = Destino.query.count()
    total_paquetes = Paquete.query.count()
    total_reservas = Reserva.query.count()
    reservas_confirmadas = Reserva.query.filter_by(estado='confirmada').count()
    
    # Últimas reservas
    ultimas_reservas = Reserva.query.order_by(Reserva.fecha_reserva.desc()).limit(5).all()
    
    # Paquetes más reservados
    paquetes_reservados = db.session.query(
        Paquete.nombre,
        func.count(Reserva.id).label('total')
    ).join(Reserva).group_by(Paquete.id).order_by(func.count(Reserva.id).desc()).limit(5).all()
    
    # Ingresos totales (suma de precios de reservas confirmadas)
    ingresos_totales = db.session.query(
        func.sum(Paquete.precio_total)
    ).join(Reserva).filter(Reserva.estado == 'confirmada').scalar() or 0
    
    # Reservas por estado
    reservas_pendientes = Reserva.query.filter_by(estado='pendiente').count()
    reservas_canceladas = Reserva.query.filter_by(estado='cancelada').count()
    
    # Paquetes agotados
    paquetes_agotados = Paquete.query.filter_by(disponibles=0).count()
    
    return render_template('web/admin/dashboard.html',
                         total_destinos=total_destinos,
                         total_paquetes=total_paquetes,
                         total_reservas=total_reservas,
                         reservas_confirmadas=reservas_confirmadas,
                         reservas_pendientes=reservas_pendientes,
                         reservas_canceladas=reservas_canceladas,
                         ingresos_totales=float(ingresos_totales),
                         paquetes_agotados=paquetes_agotados,
                         ultimas_reservas=ultimas_reservas,
                         paquetes_reservados=paquetes_reservados)

@bp.route('/reservas')
@admin_required
def reservas():
    """Gestión de reservas"""
    busqueda = request.args.get('buscar', '').strip()
    estado_filtro = request.args.get('estado', '').strip()
    
    query = Reserva.query
    
    if busqueda:
        query = query.join(Usuario).join(Paquete).filter(
            or_(
                Usuario.nombre_completo.ilike(f'%{busqueda}%'),
                Usuario.email.ilike(f'%{busqueda}%'),
                Paquete.nombre.ilike(f'%{busqueda}%')
            )
        )
    
    if estado_filtro:
        query = query.filter(Reserva.estado == estado_filtro)
    
    reservas_list = query.order_by(Reserva.fecha_reserva.desc()).all()
    return render_template('web/admin/reservas.html', 
                         reservas=reservas_list,
                         busqueda=busqueda,
                         estado_filtro=estado_filtro)

# ========== CRUD DESTINOS ==========
@bp.route('/destinos/crear', methods=['GET', 'POST'])
@admin_required
def crear_destino():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        costo_base = request.form.get('costo_base', '').strip()
        
        if not nombre:
            flash('El nombre es obligatorio', 'danger')
            return render_template('web/admin/form_destino.html')
        
        try:
            costo = float(costo_base)
            if costo < 0:
                raise ValueError
        except (ValueError, TypeError):
            flash('El costo base debe ser un número válido mayor o igual a 0', 'danger')
            return render_template('web/admin/form_destino.html')
        
        destino = Destino(
            nombre=nombre,
            origen=request.form.get('origen', '').strip() or None,
            descripcion=request.form.get('descripcion', '').strip() or None,
            actividades=request.form.get('actividades', '').strip() or None,
            costo_base=costo
        )
        db.session.add(destino)
        db.session.commit()
        flash('Destino creado exitosamente', 'success')
        return redirect('/destinos')
    return render_template('web/admin/form_destino.html')

@bp.route('/destinos/crear/api', methods=['POST'])
@admin_required
def crear_destino_api():
    """API para crear destino desde modal"""
    try:
        data = request.get_json()
        
        nombre = data.get('nombre', '').strip()
        origen = data.get('origen', '').strip() or None
        descripcion = data.get('descripcion', '').strip() or None
        actividades = data.get('actividades', '').strip() or None
        costo_base_str = data.get('costo_base', '').strip()
        
        if not nombre:
            return jsonify({'error': 'El nombre es obligatorio'}), 400
        
        if not actividades:
            return jsonify({'error': 'Las actividades son obligatorias. Deben estar separadas por comas.'}), 400
        
        if not costo_base_str:
            return jsonify({'error': 'El costo base es obligatorio'}), 400
        
        try:
            costo_base = float(costo_base_str)
            if costo_base < 0:
                return jsonify({'error': 'El costo base debe ser mayor o igual a 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'El costo base debe ser un número válido'}), 400
        
        destino = Destino(
            nombre=nombre,
            origen=origen,
            descripcion=descripcion,
            actividades=actividades,
            costo_base=costo_base
        )
        db.session.add(destino)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Destino creado exitosamente', 'destino': destino.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear destino: {str(e)}'}), 500

@bp.route('/destinos/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_destino(id):
    destino = Destino.query.get_or_404(id)
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        costo_base = request.form.get('costo_base', '').strip()
        
        if not nombre:
            flash('El nombre es obligatorio', 'danger')
            return render_template('web/admin/form_destino.html', destino=destino)
        
        try:
            costo = float(costo_base)
            if costo < 0:
                raise ValueError
        except (ValueError, TypeError):
            flash('El costo base debe ser un número válido mayor o igual a 0', 'danger')
            return render_template('web/admin/form_destino.html', destino=destino)
        
        destino.nombre = nombre
        destino.origen = request.form.get('origen', '').strip() or None
        destino.descripcion = request.form.get('descripcion', '').strip() or None
        destino.actividades = request.form.get('actividades', '').strip() or None
        destino.costo_base = costo
        db.session.commit()
        flash('Destino actualizado exitosamente', 'success')
        return redirect('/destinos')
    return render_template('web/admin/form_destino.html', destino=destino)

@bp.route('/destinos/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_destino(id):
    destino = Destino.query.get_or_404(id)
    db.session.delete(destino)
    db.session.commit()
    flash('Destino eliminado exitosamente', 'success')
    return redirect('/destinos')

# ========== CRUD PAQUETES ==========
@bp.route('/paquetes/crear', methods=['GET', 'POST'])
@admin_required
def crear_paquete():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        fecha_inicio_str = request.form.get('fecha_inicio', '').strip()
        fecha_fin_str = request.form.get('fecha_fin', '').strip()
        precio_total_str = request.form.get('precio_total', '').strip()
        disponibles_str = request.form.get('disponibles', '20').strip()
        
        if not nombre:
            flash('El nombre es obligatorio', 'danger')
            destinos_list = Destino.query.all()
            return render_template('web/admin/form_paquete.html', destinos=destinos_list)
        
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            if fecha_fin < fecha_inicio:
                raise ValueError('La fecha fin debe ser posterior a la fecha inicio')
        except ValueError as e:
            flash(f'Error en fechas: {str(e)}', 'danger')
            destinos_list = Destino.query.all()
            return render_template('web/admin/form_paquete.html', destinos=destinos_list)
        
        try:
            precio_total = float(precio_total_str)
            disponibles = int(disponibles_str)
            if precio_total < 0 or disponibles < 0:
                raise ValueError
        except (ValueError, TypeError):
            flash('El precio y disponibles deben ser números válidos mayores o iguales a 0', 'danger')
            destinos_list = Destino.query.all()
            return render_template('web/admin/form_paquete.html', destinos=destinos_list)
        
        paquete = Paquete(
            nombre=nombre,
            origen=request.form.get('origen', '').strip() or None,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            precio_total=precio_total,
            disponibles=disponibles
        )
        db.session.add(paquete)
        db.session.flush()
        
        destinos_ids = request.form.getlist('destinos')
        for destino_id in destinos_ids:
            if Destino.query.get(destino_id):
                db.session.add(PaqueteDestino(paquete_id=paquete.id, destino_id=int(destino_id)))
        
        db.session.commit()
        flash('Paquete creado exitosamente', 'success')
        return redirect('/paquetes')
    
    destinos_list = Destino.query.all()
    return render_template('web/admin/form_paquete.html', destinos=destinos_list)

@bp.route('/api/destinos', methods=['GET'])
@admin_required
def api_destinos():
    """API para obtener destinos (para el modal)"""
    destinos = Destino.query.all()
    return jsonify([{'id': d.id, 'nombre': d.nombre, 'costo_base': float(d.costo_base)} for d in destinos])

@bp.route('/paquetes/crear/api', methods=['POST'])
@admin_required
def crear_paquete_api():
    """API para crear paquete desde modal"""
    try:
        data = request.get_json()
        
        nombre = data.get('nombre', '').strip()
        origen = data.get('origen', '').strip()
        fecha_inicio_str = data.get('fecha_inicio', '').strip()
        fecha_fin_str = data.get('fecha_fin', '').strip()
        precio_total_str = data.get('precio_total', '').strip()
        disponibles_str = data.get('disponibles', '20').strip()
        destinos_ids = data.get('destinos', [])
        
        if not nombre:
            return jsonify({'error': 'El nombre es obligatorio'}), 400
        
        if not origen:
            return jsonify({'error': 'El origen es obligatorio'}), 400
        
        if not fecha_inicio_str:
            return jsonify({'error': 'La fecha de inicio es obligatoria'}), 400
        
        if not fecha_fin_str:
            return jsonify({'error': 'La fecha de fin es obligatoria'}), 400
        
        if not precio_total_str:
            return jsonify({'error': 'El precio total es obligatorio'}), 400
        
        if not disponibles_str:
            return jsonify({'error': 'Los cupos disponibles son obligatorios'}), 400
        
        if not destinos_ids or len(destinos_ids) == 0:
            return jsonify({'error': 'Debes seleccionar al menos un destino'}), 400
        
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            if fecha_fin < fecha_inicio:
                return jsonify({'error': 'La fecha fin debe ser posterior a la fecha inicio'}), 400
        except ValueError as e:
            return jsonify({'error': f'Error en fechas: {str(e)}'}), 400
        
        try:
            precio_total = float(precio_total_str)
            disponibles = int(disponibles_str)
            if precio_total < 0 or disponibles < 0:
                return jsonify({'error': 'El precio y disponibles deben ser números válidos mayores o iguales a 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'El precio y disponibles deben ser números válidos'}), 400
        
        paquete = Paquete(
            nombre=nombre,
            origen=origen,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            precio_total=precio_total,
            disponibles=disponibles
        )
        db.session.add(paquete)
        db.session.flush()
        
        for destino_id in destinos_ids:
            if Destino.query.get(destino_id):
                db.session.add(PaqueteDestino(paquete_id=paquete.id, destino_id=int(destino_id)))
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Paquete creado exitosamente', 'paquete': paquete.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear paquete: {str(e)}'}), 500

@bp.route('/paquetes/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_paquete(id):
    paquete = Paquete.query.get_or_404(id)
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        fecha_inicio_str = request.form.get('fecha_inicio', '').strip()
        fecha_fin_str = request.form.get('fecha_fin', '').strip()
        precio_total_str = request.form.get('precio_total', '').strip()
        disponibles_str = request.form.get('disponibles', '20').strip()
        
        if not nombre:
            flash('El nombre es obligatorio', 'danger')
            destinos_list = Destino.query.all()
            destinos_seleccionados = [pd.destino_id for pd in paquete.destinos]
            return render_template('web/admin/form_paquete.html', paquete=paquete, destinos=destinos_list, destinos_seleccionados=destinos_seleccionados)
        
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            if fecha_fin < fecha_inicio:
                raise ValueError('La fecha fin debe ser posterior a la fecha inicio')
        except ValueError as e:
            flash(f'Error en fechas: {str(e)}', 'danger')
            destinos_list = Destino.query.all()
            destinos_seleccionados = [pd.destino_id for pd in paquete.destinos]
            return render_template('web/admin/form_paquete.html', paquete=paquete, destinos=destinos_list, destinos_seleccionados=destinos_seleccionados)
        
        try:
            precio_total = float(precio_total_str)
            disponibles = int(disponibles_str)
            if precio_total < 0 or disponibles < 0:
                raise ValueError
        except (ValueError, TypeError):
            flash('El precio y disponibles deben ser números válidos mayores o iguales a 0', 'danger')
            destinos_list = Destino.query.all()
            destinos_seleccionados = [pd.destino_id for pd in paquete.destinos]
            return render_template('web/admin/form_paquete.html', paquete=paquete, destinos=destinos_list, destinos_seleccionados=destinos_seleccionados)
        
        paquete.nombre = nombre
        paquete.origen = request.form.get('origen', '').strip() or None
        paquete.fecha_inicio = fecha_inicio
        paquete.fecha_fin = fecha_fin
        paquete.precio_total = precio_total
        paquete.disponibles = disponibles
        
        # Actualizar destinos
        PaqueteDestino.query.filter_by(paquete_id=paquete.id).delete()
        destinos_ids = request.form.getlist('destinos')
        for destino_id in destinos_ids:
            if Destino.query.get(destino_id):
                db.session.add(PaqueteDestino(paquete_id=paquete.id, destino_id=int(destino_id)))
        
        db.session.commit()
        flash('Paquete actualizado exitosamente', 'success')
        return redirect('/paquetes')
    
    destinos_list = Destino.query.all()
    destinos_seleccionados = [pd.destino_id for pd in paquete.destinos]
    return render_template('web/admin/form_paquete.html', paquete=paquete, destinos=destinos_list, destinos_seleccionados=destinos_seleccionados)

@bp.route('/paquetes/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_paquete(id):
    paquete = Paquete.query.get_or_404(id)
    db.session.delete(paquete)
    db.session.commit()
    flash('Paquete eliminado exitosamente', 'success')
    return redirect(url_for('admin.paquetes'))

@bp.route('/paquetes/editar/<int:id>/api', methods=['PUT'])
@admin_required
def editar_paquete_api(id):
    """API para editar paquete desde modal"""
    try:
        paquete = Paquete.query.get_or_404(id)
        data = request.get_json()
        
        nombre = data.get('nombre', '').strip()
        fecha_inicio_str = data.get('fecha_inicio', '').strip()
        fecha_fin_str = data.get('fecha_fin', '').strip()
        precio_total_str = data.get('precio_total', '').strip()
        disponibles_str = data.get('disponibles', '').strip()
        
        if not nombre:
            return jsonify({'error': 'El nombre es obligatorio'}), 400
        
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            if fecha_fin < fecha_inicio:
                return jsonify({'error': 'La fecha fin debe ser posterior a la fecha inicio'}), 400
        except ValueError as e:
            return jsonify({'error': f'Error en fechas: {str(e)}'}), 400
        
        try:
            precio_total = float(precio_total_str)
            disponibles = int(disponibles_str)
            if precio_total < 0 or disponibles < 0:
                return jsonify({'error': 'El precio y disponibles deben ser números válidos mayores o iguales a 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'El precio y disponibles deben ser números válidos'}), 400
        
        paquete.nombre = nombre
        paquete.origen = data.get('origen', '').strip() or None
        paquete.fecha_inicio = fecha_inicio
        paquete.fecha_fin = fecha_fin
        paquete.precio_total = precio_total
        paquete.disponibles = disponibles
        
        # Actualizar destinos
        PaqueteDestino.query.filter_by(paquete_id=paquete.id).delete()
        destinos_ids = data.get('destinos', [])
        for destino_id in destinos_ids:
            if Destino.query.get(destino_id):
                db.session.add(PaqueteDestino(paquete_id=paquete.id, destino_id=int(destino_id)))
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Paquete actualizado exitosamente', 'paquete': paquete.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar paquete: {str(e)}'}), 500

@bp.route('/paquetes/eliminar/<int:id>/api', methods=['DELETE'])
@admin_required
def eliminar_paquete_api(id):
    """API para eliminar paquete desde la página pública"""
    try:
        paquete = Paquete.query.get_or_404(id)
        nombre_paquete = paquete.nombre
        db.session.delete(paquete)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Paquete "{nombre_paquete}" eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar paquete: {str(e)}'}), 500

# ========== CRUD RESERVAS ==========
@bp.route('/reservas/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    if request.method == 'POST':
        reserva.estado = request.form.get('estado')
        db.session.commit()
        flash('Reserva actualizada exitosamente', 'success')
        return redirect(url_for('admin.reservas'))
    paquetes = Paquete.query.all()
    return render_template('web/admin/form_reserva.html', reserva=reserva, paquetes=paquetes)

@bp.route('/reservas/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    # Restaurar cupo del paquete
    reserva.paquete.disponibles += 1
    db.session.delete(reserva)
    db.session.commit()
    flash('Reserva eliminada exitosamente', 'success')
    return redirect(url_for('admin.reservas'))

