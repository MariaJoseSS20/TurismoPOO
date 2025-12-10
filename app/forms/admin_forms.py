"""
Formularios de administración usando WTForms
"""
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional, Length, ValidationError
from datetime import date
from app.models.destino import Destino
from app.models.usuario import Usuario


class DestinoForm(FlaskForm):
    """Formulario para crear/editar destinos"""
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(max=200, message='El nombre no puede tener más de 200 caracteres')
    ])
    
    origen = StringField('Origen', validators=[
        Optional(),
        Length(max=200, message='El origen no puede tener más de 200 caracteres')
    ])
    
    descripcion = TextAreaField('Descripción', validators=[
        Optional()
    ])
    
    actividades = TextAreaField('Actividades', validators=[
        Optional()
    ])
    
    costo_base = DecimalField('Costo Base', validators=[
        DataRequired(message='El costo base es obligatorio'),
        NumberRange(min=0, message='El costo base debe ser mayor o igual a 0')
    ], places=2)


class PaqueteForm(FlaskForm):
    """Formulario para crear/editar paquetes"""
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(max=200, message='El nombre no puede tener más de 200 caracteres')
    ])
    
    origen = StringField('Origen', validators=[
        Optional(),
        Length(max=200, message='El origen no puede tener más de 200 caracteres')
    ])
    
    fecha_inicio = DateField('Fecha Inicio', validators=[
        DataRequired(message='La fecha de inicio es obligatoria')
    ], format='%Y-%m-%d')
    
    fecha_fin = DateField('Fecha Fin', validators=[
        DataRequired(message='La fecha fin es obligatoria')
    ], format='%Y-%m-%d')
    
    precio_total = DecimalField('Precio Total', validators=[
        DataRequired(message='El precio total es obligatorio'),
        NumberRange(min=0, message='El precio debe ser mayor o igual a 0')
    ], places=2)
    
    disponibles = IntegerField('Disponibles', validators=[
        DataRequired(message='El número de disponibles es obligatorio'),
        NumberRange(min=0, message='El número de disponibles debe ser mayor o igual a 0')
    ], default=20)
    
    def validate_fecha_fin(self, field):
        """Validar que la fecha fin sea posterior a la fecha inicio"""
        if self.fecha_inicio.data and field.data:
            if field.data < self.fecha_inicio.data:
                raise ValidationError('La fecha fin debe ser posterior a la fecha inicio')


# ReservaForm y UsuarioForm eliminados - no se usan
# Las reservas son de solo lectura y no hay gestión de usuarios desde admin

