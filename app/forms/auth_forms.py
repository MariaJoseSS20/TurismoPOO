"""
Formularios de autenticación usando WTForms
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TelField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from datetime import date
from app.models.usuario import Usuario
from app.utils import validar_rut_chileno


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión"""
    email = StringField('Email', validators=[
        DataRequired(message='El email es obligatorio'),
        Email(message='El email no tiene un formato válido')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria')
    ])


class RegistroForm(FlaskForm):
    """Formulario de registro de usuario"""
    nombre_completo = StringField('Nombre Completo', validators=[
        DataRequired(message='El nombre completo es obligatorio'),
        Length(min=3, max=200, message='El nombre debe tener entre 3 y 200 caracteres')
    ])
    
    rut = StringField('RUT', validators=[
        DataRequired(message='El RUT es obligatorio')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='El email es obligatorio'),
        Email(message='El email no tiene un formato válido')
    ])
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    
    confirmar_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Debes confirmar la contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[
        DataRequired(message='La fecha de nacimiento es obligatoria')
    ], format='%Y-%m-%d')
    
    telefono = TelField('Teléfono', validators=[
        DataRequired(message='El teléfono es obligatorio'),
        Length(max=20, message='El teléfono no puede tener más de 20 caracteres')
    ])
    
    def validate_rut(self, field):
        """Validar formato y unicidad del RUT"""
        rut = field.data.strip() if field.data else ''
        if not validar_rut_chileno(rut):
            raise ValidationError('El RUT no tiene un formato válido')
        
        # Normalizar RUT (quitar puntos y guiones) para comparar en BD
        rut_normalizado = rut.replace('.', '').replace('-', '').strip().upper()
        
        # Verificar unicidad en la base de datos
        if Usuario.query.filter_by(rut=rut_normalizado).first():
            raise ValidationError('El RUT ya está registrado')
    
    def validate_email(self, field):
        """Validar unicidad del email"""
        # Solo validar unicidad si el email tiene valor (DataRequired ya valida que no esté vacío)
        if not field.data or not field.data.strip():
            return  # Dejar que DataRequired maneje el error de campo vacío
        
        email = field.data.strip().lower()
        if Usuario.query.filter_by(email=email).first():
            raise ValidationError('El email ya está registrado')
    
    def validate_fecha_nacimiento(self, field):
        """Validar que la fecha no sea futura y que el usuario sea mayor de 18 años"""
        if not field.data:
            return
        
        fecha_nac = field.data
        hoy = date.today()
        
        if fecha_nac > hoy:
            raise ValidationError('La fecha de nacimiento no puede ser futura')
        
        # Calcular edad mínima (18 años)
        try:
            fecha_minima = date(hoy.year - 18, hoy.month, hoy.day)
        except ValueError:
            # Si hoy es 29 de febrero y hace 18 años no era bisiesto
            fecha_minima = date(hoy.year - 18, hoy.month, hoy.day - 1)
        
        if fecha_nac > fecha_minima:
            raise ValidationError('Debes ser mayor de 18 años para crear una cuenta')


class PerfilForm(FlaskForm):
    """Formulario para actualizar perfil de usuario"""
    nombre_completo = StringField('Nombre Completo', validators=[
        DataRequired(message='El nombre completo es obligatorio'),
        Length(min=2, max=200, message='El nombre debe tener entre 2 y 200 caracteres')
    ])
    
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[
        DataRequired(message='La fecha de nacimiento es obligatoria')
    ], format='%Y-%m-%d')
    
    telefono = TelField('Teléfono', validators=[
        Length(max=20, message='El teléfono no puede tener más de 20 caracteres')
    ])
    
    def validate_nombre_completo(self, field):
        """Validar formato del nombre (solo letras, espacios, guiones y apóstrofes)"""
        if not field.data:
            return
        
        nombre = field.data.strip()
        import re
        # Solo letras (incluyendo acentos y ñ), espacios, guiones y apóstrofes
        nombre_regex = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s\-']{2,200}$")
        if not nombre_regex.match(nombre):
            raise ValidationError('El nombre solo puede contener letras, espacios, guiones y apóstrofes (mínimo 2 caracteres)')
    
    def validate_telefono(self, field):
        """Validar formato del teléfono (obligatorio)"""
        if not field.data or not field.data.strip():
            raise ValidationError('El teléfono es obligatorio')
        
        telefono = field.data.strip()
        import re
        # Formato: +56912345678 o 912345678 (9 dígitos después del código de país, empezando con 9)
        telefono_regex = re.compile(r'^(\+?56)?(9)[0-9]{8}$')
        if not telefono_regex.match(telefono):
            raise ValidationError('El teléfono debe tener un formato válido (ej: +56912345678 o 912345678)')
    
    def validate_fecha_nacimiento(self, field):
        """Validar que la fecha no sea futura y que el usuario sea mayor de 18 años"""
        if not field.data:
            return
        
        fecha_nac = field.data
        hoy = date.today()
        
        if fecha_nac > hoy:
            raise ValidationError('La fecha de nacimiento no puede ser futura')
        
        # Calcular edad mínima (18 años)
        try:
            fecha_minima = date(hoy.year - 18, hoy.month, hoy.day)
        except ValueError:
            # Si hoy es 29 de febrero y hace 18 años no era bisiesto
            fecha_minima = date(hoy.year - 18, hoy.month, hoy.day - 1)
        
        if fecha_nac > fecha_minima:
            raise ValidationError('Debes ser mayor de 18 años')

