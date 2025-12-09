from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.usuario import Usuario
from app.utils import validar_rut_chileno

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(password):
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
            error = 'Email o contraseña incorrectos'
    
    return render_template('web/auth/login.html', error=error)

@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    # Calcular fecha máxima (hoy) y fecha mínima (hace 18 años) para el input de fecha de nacimiento
    from datetime import date
    hoy = date.today()
    fecha_maxima = hoy.isoformat()
    
    # Calcular fecha mínima (hace exactamente 18 años)
    try:
        fecha_minima = date(hoy.year - 18, hoy.month, hoy.day)
    except ValueError:
        # Si hoy es 29 de febrero y hace 18 años no era bisiesto, usar 28 de febrero
        fecha_minima = date(hoy.year - 18, hoy.month, hoy.day - 1)
    
    fecha_minima_str = fecha_minima.isoformat()
    
    if request.method == 'POST':
        nombre_completo = request.form.get('nombre_completo')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmar_password = request.form.get('confirmar_password')
        fecha_nacimiento_str = request.form.get('fecha_nacimiento')
        telefono = request.form.get('telefono', '').strip()
        
        if password != confirmar_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('web/auth/registro.html', fecha_maxima=fecha_maxima, fecha_minima=fecha_minima_str)
        
        rut = request.form.get('rut', '').strip()
        
        if not rut:
            flash('El RUT es obligatorio', 'danger')
            return render_template('web/auth/registro.html', fecha_maxima=fecha_maxima, fecha_minima=fecha_minima_str)

        if not validar_rut_chileno(rut):
            flash('El RUT no tiene un formato válido', 'danger')
            return render_template('web/auth/registro.html', fecha_maxima=fecha_maxima, fecha_minima=fecha_minima_str)

        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'danger')
            return render_template('web/auth/registro.html', fecha_maxima=fecha_maxima, fecha_minima=fecha_minima_str)

        if Usuario.query.filter_by(rut=rut).first():
            flash('El RUT ya está registrado', 'danger')
            return render_template('web/auth/registro.html', fecha_maxima=fecha_maxima, fecha_minima=fecha_minima_str)
        
        # Validar y convertir fecha de nacimiento (obligatoria)
        if not fecha_nacimiento_str:
            flash('La fecha de nacimiento es obligatoria', 'danger')
            return render_template('web/auth/registro.html', fecha_maxima=fecha_maxima, fecha_minima=fecha_minima_str)
        
        try:
            from datetime import datetime
            # Intentar parsear el formato dd/mm/yyyy (formato de Flatpickr con barras)
            try:
                fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%d/%m/%Y').date()
            except ValueError:
                # Si falla, intentar el formato dd-mm-yyyy (con guiones)
                try:
                    fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%d-%m-%Y').date()
                except ValueError:
                    # Si falla, intentar el formato yyyy-mm-dd (formato HTML5 nativo)
                    fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
            
            # Validar que la fecha no sea futura
            if fecha_nacimiento > date.today():
                flash('La fecha de nacimiento no puede ser futura', 'danger')
                return render_template('web/auth/registro.html', fecha_maxima=fecha_maxima, fecha_minima=fecha_minima_str)
            
            # Validar que el usuario sea mayor de 18 años
            # Si la fecha de nacimiento es posterior a la fecha mínima, el usuario es menor de 18
            if fecha_nacimiento > fecha_minima:
                flash('Debes ser mayor de 18 años para crear una cuenta', 'danger')
                return render_template('web/auth/registro.html', fecha_maxima=fecha_maxima, fecha_minima=fecha_minima_str)
        except ValueError:
            flash('La fecha de nacimiento no tiene un formato válido', 'danger')
            return render_template('web/auth/registro.html', fecha_maxima=fecha_maxima, fecha_minima=fecha_minima_str)
        
        usuario = Usuario(
            nombre_completo=nombre_completo,
            rut=rut,
            email=email,
            fecha_nacimiento=fecha_nacimiento,
            telefono=telefono if telefono else None,
            rol='cliente'
        )
        usuario.set_password(password)
        
        db.session.add(usuario)
        db.session.commit()
        
        flash('¡Registro exitoso! Inicia sesión', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('web/auth/registro.html', fecha_maxima=fecha_maxima, fecha_minima=fecha_minima_str)

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
    
    if request.method == 'POST':
        nombre_completo = request.form.get('nombre_completo', '').strip()
        fecha_nacimiento_str = request.form.get('fecha_nacimiento', '').strip()
        telefono = request.form.get('telefono', '').strip()
        
        if not nombre_completo:
            flash('El nombre completo es obligatorio', 'danger')
            from datetime import date
            fecha_maxima = date.today().isoformat()
            template = 'web/admin/perfil.html' if usuario.rol == 'admin' else 'web/auth/perfil.html'
            return render_template(template, usuario=usuario, fecha_maxima=fecha_maxima)
        
        # Validar y convertir fecha de nacimiento
        if fecha_nacimiento_str:
            try:
                from datetime import datetime, date
                # Intentar parsear diferentes formatos
                try:
                    fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%d/%m/%Y').date()
                    except ValueError:
                        fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%d-%m-%Y').date()
                
                # Validar que la fecha no sea futura
                if fecha_nacimiento > date.today():
                    flash('La fecha de nacimiento no puede ser futura', 'danger')
                    from datetime import date
                    fecha_maxima = date.today().isoformat()
                    template = 'web/admin/perfil.html' if usuario.rol == 'admin' else 'web/auth/perfil.html'
                    return render_template(template, usuario=usuario, fecha_maxima=fecha_maxima)
            except ValueError:
                flash('La fecha de nacimiento no tiene un formato válido', 'danger')
                from datetime import date
                fecha_maxima = date.today().isoformat()
                template = 'web/admin/perfil.html' if usuario.rol == 'admin' else 'web/auth/perfil.html'
                return render_template(template, usuario=usuario, fecha_maxima=fecha_maxima)
        else:
            fecha_nacimiento = usuario.fecha_nacimiento
        
        # Actualizar datos
        usuario.nombre_completo = nombre_completo
        usuario.fecha_nacimiento = fecha_nacimiento
        usuario.telefono = telefono if telefono else None
        
        db.session.commit()
        
        # Actualizar sesión si cambió el nombre
        session['usuario_nombre'] = usuario.nombre_completo
        
        flash('Perfil actualizado exitosamente', 'success')
        return redirect(url_for('auth.perfil'))
    
    from datetime import date
    fecha_maxima = date.today().isoformat()
    template = 'web/admin/perfil.html' if usuario.rol == 'admin' else 'web/auth/perfil.html'
    return render_template(template, usuario=usuario, fecha_maxima=fecha_maxima)

