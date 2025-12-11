from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import db
from app.models.usuario import Usuario
from app.forms.auth_forms import LoginForm, RegistroForm, PerfilForm
from datetime import date

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        
        if usuario and usuario.check_password(form.password.data):
            session['usuario_id'] = usuario.id
            session['usuario_nombre'] = usuario.nombre_completo
            session['usuario_email'] = usuario.email
            session['usuario_rol'] = usuario.rol
            
            # Redirigir a la página que intentaba acceder
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('web.index'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('web/auth/login.html', form=form)

@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistroForm()
    
    # Calcular fechas para el frontend (validación de edad mínima)
    hoy = date.today()
    fecha_maxima = hoy.isoformat()
    try:
        fecha_minima = date(hoy.year - 18, hoy.month, hoy.day)
    except ValueError:
        fecha_minima = date(hoy.year - 18, hoy.month, hoy.day - 1)
    fecha_minima_str = fecha_minima.isoformat()
    
    if form.validate_on_submit():
        # Normalizar RUT antes de guardar (quitar puntos y guiones)
        rut_normalizado = form.rut.data.strip().replace('.', '').replace('-', '').upper()
        
        # Manejar formato de fecha dd/mm/yyyy si viene del frontend
        fecha_nac = form.fecha_nacimiento.data
        if isinstance(fecha_nac, str) and '/' in fecha_nac:
            # Formato dd/mm/yyyy
            try:
                from datetime import datetime
                fecha_nac = datetime.strptime(fecha_nac, '%d/%m/%Y').date()
            except ValueError:
                pass  # Dejar que el validador del formulario maneje el error
        
        usuario = Usuario(
            nombre_completo=form.nombre_completo.data,
            rut=rut_normalizado,
            email=form.email.data.strip().lower(),
            fecha_nacimiento=fecha_nac,
            telefono=form.telefono.data.strip() if form.telefono.data else None,
            rol='cliente'
        )
        usuario.set_password(form.password.data)
        
        # Verificar unicidad de email una vez más antes de guardar (doble verificación)
        email_normalizado = form.email.data.strip().lower()
        if Usuario.query.filter_by(email=email_normalizado).first():
            flash('El email ya está registrado', 'danger')
            return render_template('web/auth/registro.html', 
                                 form=form, 
                                 fecha_maxima=fecha_maxima, 
                                 fecha_minima=fecha_minima_str)
        
        db.session.add(usuario)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # Si hay un error de unicidad (por ejemplo, constraint de base de datos)
            if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
                flash('El email ya está registrado', 'danger')
            else:
                flash(f'Error al crear la cuenta: {str(e)}', 'danger')
            return render_template('web/auth/registro.html', 
                                 form=form, 
                                 fecha_maxima=fecha_maxima, 
                                 fecha_minima=fecha_minima_str)
        
        # Iniciar sesión automáticamente después del registro
        session['usuario_id'] = usuario.id
        session['usuario_nombre'] = usuario.nombre_completo
        session['usuario_email'] = usuario.email
        session['usuario_rol'] = usuario.rol
        
        flash('¡Registro exitoso! Bienvenido a Viajes Aventura', 'success')
        return redirect(url_for('web.index'))
    
    return render_template('web/auth/registro.html', 
                         form=form, 
                         fecha_maxima=fecha_maxima, 
                         fecha_minima=fecha_minima_str)

@bp.route('/verificar-rut')
def verificar_rut():
    """API para verificar si un RUT ya está registrado"""
    rut = request.args.get('rut', '').strip()
    if not rut:
        return jsonify({'existe': False})
    
    # Normalizar RUT (quitar puntos y guiones, mantener formato estándar)
    rut_normalizado = rut.replace('.', '').replace('-', '').strip().upper()
    
    # Buscar en la base de datos (el RUT se almacena normalizado)
    usuario = Usuario.query.filter_by(rut=rut_normalizado).first()
    return jsonify({'existe': usuario is not None})

@bp.route('/verificar-email')
def verificar_email():
    """API para verificar si un email ya está registrado"""
    email = request.args.get('email', '').strip()
    if not email:
        return jsonify({'existe': False})
    
    # Normalizar email a minúsculas para comparar (igual que en el registro)
    email_normalizado = email.lower()
    usuario = Usuario.query.filter_by(email=email_normalizado).first()
    return jsonify({'existe': usuario is not None})

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('web.index'))

@bp.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión', 'warning')
        return redirect(url_for('auth.login'))
    
    usuario = Usuario.query.get(session['usuario_id'])
    form = PerfilForm(obj=usuario)  # Pre-llenar formulario con datos del usuario
    
    if request.method == 'POST':
        # Manejar formato de fecha dd/mm/yyyy si viene del frontend
        fecha_str = request.form.get('fecha_nacimiento', '')
        if fecha_str and '/' in fecha_str:
            # Formato dd/mm/yyyy
            try:
                from datetime import datetime
                fecha_nac = datetime.strptime(fecha_str, '%d/%m/%Y').date()
                form.fecha_nacimiento.data = fecha_nac
            except ValueError:
                pass  # Dejar que el validador del formulario maneje el error
    
    if form.validate_on_submit():
        usuario.nombre_completo = form.nombre_completo.data
        usuario.fecha_nacimiento = form.fecha_nacimiento.data
        usuario.telefono = form.telefono.data.strip() if form.telefono.data else None
        
        db.session.commit()
        
        # Actualizar sesión si cambió el nombre
        session['usuario_nombre'] = usuario.nombre_completo
        
        flash('Perfil actualizado exitosamente', 'success')
        return redirect(url_for('auth.perfil_detalle'))
    
    # Calcular fecha mínima (hace 18 años) para el template
    hoy = date.today()
    try:
        fecha_minima = date(hoy.year - 18, hoy.month, hoy.day)
    except ValueError:
        # Si hoy es 29 de febrero y hace 18 años no era bisiesto
        fecha_minima = date(hoy.year - 18, hoy.month, hoy.day - 1)
    
    fecha_maxima = date.today().isoformat()
    template = 'web/admin/perfil.html' if usuario.rol == 'admin' else 'web/auth/perfil.html'
    return render_template(template, usuario=usuario, form=form, fecha_maxima=fecha_maxima, fecha_minima=fecha_minima.isoformat())

@bp.route('/perfil/detalle')
def perfil_detalle():
    """Mostrar detalles del perfil del usuario (solo lectura) y sus reservas si es cliente"""
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión', 'warning')
        return redirect(url_for('auth.login'))
    
    usuario = Usuario.query.get(session['usuario_id'])
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('auth.login'))
    
    # Si es cliente, obtener sus reservas
    reservas = []
    if usuario.rol == 'cliente':
        from app.models.reserva import Reserva
        reservas = Reserva.query.filter_by(usuario_id=usuario.id).order_by(Reserva.fecha_reserva.desc()).all()
    
    template = 'web/admin/perfil_detalle.html' if usuario.rol == 'admin' else 'web/auth/perfil_detalle.html'
    return render_template(template, usuario=usuario)

@bp.route('/reservas')
def mis_reservas():
    """Mostrar las reservas del cliente"""
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión', 'warning')
        return redirect(url_for('auth.login'))
    
    usuario = Usuario.query.get(session['usuario_id'])
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('auth.login'))
    
    # Solo clientes pueden ver sus reservas
    if usuario.rol != 'cliente':
        flash('Solo los clientes pueden ver sus reservas', 'warning')
        return redirect(url_for('web.index'))
    
    from app.models.reserva import Reserva
    reservas_confirmadas = Reserva.query.filter_by(usuario_id=usuario.id, estado='confirmada').order_by(Reserva.fecha_reserva.desc()).all()
    reservas_canceladas = Reserva.query.filter_by(usuario_id=usuario.id, estado='cancelada').order_by(Reserva.fecha_reserva.desc()).all()
    
    return render_template('web/auth/mis_reservas.html', 
                         reservas_confirmadas=reservas_confirmadas, 
                         reservas_canceladas=reservas_canceladas, 
                         usuario=usuario)

@bp.route('/reservas/canceladas')
def reservas_canceladas():
    """Mostrar solo las reservas canceladas del cliente"""
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión', 'warning')
        return redirect(url_for('auth.login'))
    
    usuario = Usuario.query.get(session['usuario_id'])
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('auth.login'))
    
    # Solo clientes pueden ver sus reservas
    if usuario.rol != 'cliente':
        flash('Solo los clientes pueden ver sus reservas', 'warning')
        return redirect(url_for('web.index'))
    
    from app.models.reserva import Reserva
    reservas_canceladas = Reserva.query.filter_by(usuario_id=usuario.id, estado='cancelada').order_by(Reserva.fecha_reserva.desc()).all()
    
    return render_template('web/auth/reservas_canceladas.html', reservas_canceladas=reservas_canceladas, usuario=usuario)

