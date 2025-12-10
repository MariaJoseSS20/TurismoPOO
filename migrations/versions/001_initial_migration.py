"""Initial migration - modelos existentes

Revision ID: 001_initial
Revises: 
Create Date: 2024-12-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Esta migración está vacía porque las tablas ya existen
    # Se creó para marcar el estado inicial de la base de datos
    pass


def downgrade():
    # No hay downgrade porque es la migración inicial
    pass

