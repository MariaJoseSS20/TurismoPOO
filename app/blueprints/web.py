from flask import Blueprint, render_template, redirect, url_for, flash, session

bp = Blueprint('web', __name__)

@bp.route('/')
def index():
    return render_template('web/index.html')

@bp.route('/destinos')
def destinos():
    # Solo administradores pueden acceder a la página de destinos
    if session.get('usuario_rol') != 'admin':
        flash('Acceso denegado. Solo administradores pueden acceder a esta página.', 'warning')
        return redirect(url_for('web.index'))
    return render_template('web/destinos.html')

@bp.route('/paquetes')
def paquetes():
    # Pasar información de sesión al template para JavaScript
    usuario_rol = session.get('usuario_rol', '')
    return render_template('web/paquetes.html', usuario_rol=usuario_rol)

@bp.route('/carrito')
def carrito():
    # Solo clientes pueden acceder al carrito
    if session.get('usuario_rol') == 'admin':
        flash('Los administradores no pueden acceder al carrito', 'warning')
        return redirect(url_for('web.index'))
    
    # Obtener datos del usuario si está logueado
    usuario_data = None
    if 'usuario_id' in session:
        from app.models.usuario import Usuario
        usuario = Usuario.query.get(session['usuario_id'])
        if usuario:
            usuario_data = {
                'nombre_completo': usuario.nombre_completo,
                'rut': usuario.rut,
                'email': usuario.email
            }
    
    return render_template('web/carrito.html', session=session, usuario_data=usuario_data)

@bp.route('/mis-reservas')
def mis_reservas():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para ver tus reservas', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('web/mis_reservas.html', session=session)
