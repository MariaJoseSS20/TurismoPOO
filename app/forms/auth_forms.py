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
        Length(max=20, message='El teléfono no puede tener más de 20 caracteres')
    ])
    
    def validate_rut(self, field):
        """Validar formato y unicidad del RUT"""
        rut = field.data.strip() if field.data else ''
        if not validar_rut_chileno(rut):
            raise ValidationError('El RUT no tiene un formato válido')
        
        if Usuario.query.filter_by(rut=rut).first():
            raise ValidationError('El RUT ya está registrado')
    
    def validate_email(self, field):
        """Validar unicidad del email"""
        if Usuario.query.filter_by(email=field.data).first():
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
        Length(min=3, max=200, message='El nombre debe tener entre 3 y 200 caracteres')
    ])
    
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[
        DataRequired(message='La fecha de nacimiento es obligatoria')
    ], format='%Y-%m-%d')
    
    telefono = TelField('Teléfono', validators=[
        Length(max=20, message='El teléfono no puede tener más de 20 caracteres')
    ])
    
    def validate_fecha_nacimiento(self, field):
        """Validar que la fecha no sea futura"""
        if not field.data:
            return
        
        if field.data > date.today():
            raise ValidationError('La fecha de nacimiento no puede ser futura')

