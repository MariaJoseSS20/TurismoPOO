from flask import Blueprint, render_template, request, redirect, url_for, flash, session
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
        usuario = Usuario(
            nombre_completo=form.nombre_completo.data,
            rut=form.rut.data.strip(),
            email=form.email.data,
            fecha_nacimiento=form.fecha_nacimiento.data,
            telefono=form.telefono.data.strip() if form.telefono.data else None,
            rol='cliente'
        )
        usuario.set_password(form.password.data)
        
        db.session.add(usuario)
        db.session.commit()
        
        flash('¡Registro exitoso! Inicia sesión', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('web/auth/registro.html', 
                         form=form, 
                         fecha_maxima=fecha_maxima, 
                         fecha_minima=fecha_minima_str)

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
    
    if form.validate_on_submit():
        usuario.nombre_completo = form.nombre_completo.data
        usuario.fecha_nacimiento = form.fecha_nacimiento.data
        usuario.telefono = form.telefono.data.strip() if form.telefono.data else None
        
        db.session.commit()
        
        # Actualizar sesión si cambió el nombre
        session['usuario_nombre'] = usuario.nombre_completo
        
        flash('Perfil actualizado exitosamente', 'success')
        return redirect(url_for('auth.perfil_detalle'))
    
    fecha_maxima = date.today().isoformat()
    template = 'web/admin/perfil.html' if usuario.rol == 'admin' else 'web/auth/perfil.html'
    return render_template(template, usuario=usuario, form=form, fecha_maxima=fecha_maxima)

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
    return render_template(template, usuario=usuario, reservas=reservas)

