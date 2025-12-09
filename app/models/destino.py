from app import db

class Destino(db.Model):
    __tablename__ = 'destinos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    origen = db.Column(db.String(200), nullable=True)
    descripcion = db.Column(db.Text)
    actividades = db.Column(db.Text)
    costo_base = db.Column(db.Numeric(10, 2), nullable=False)
    
    paquetes = db.relationship('PaqueteDestino', back_populates='destino', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'origen': getattr(self, 'origen', None),
            'descripcion': self.descripcion,
            'actividades': self.actividades.split(',') if self.actividades else [],
            'costo_base': float(self.costo_base) if self.costo_base else 0.0
        }
    
    def __repr__(self):
        return f'<Destino {self.nombre}>'

