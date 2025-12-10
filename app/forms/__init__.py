"""
Módulo de formularios WTForms
Centraliza todas las validaciones de formularios
"""
from app.forms.auth_forms import LoginForm, RegistroForm, PerfilForm
from app.forms.admin_forms import (
    DestinoForm, 
    PaqueteForm
)

__all__ = [
    'LoginForm',
    'RegistroForm', 
    'PerfilForm',
    'DestinoForm',
    'PaqueteForm'
]

