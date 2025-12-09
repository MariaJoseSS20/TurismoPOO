from app import db

class Paquete(db.Model):
    __tablename__ = 'paquetes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    origen = db.Column(db.String(200), nullable=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    precio_total = db.Column(db.Numeric(10, 2), nullable=False)
    disponibles = db.Column(db.Integer, default=20, nullable=False)
    
    destinos = db.relationship('PaqueteDestino', back_populates='paquete', cascade='all, delete-orphan')
    reservas = db.relationship('Reserva', backref='paquete', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        # Cargar destinos de forma segura
        destinos_list = []
        for pd in self.destinos:
            if pd and pd.destino:
                destinos_list.append(pd.destino.to_dict())
        
        return {
            'id': self.id,
            'nombre': self.nombre,
            'origen': getattr(self, 'origen', None),
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'precio_total': float(self.precio_total) if self.precio_total else 0.0,
            'disponibles': self.disponibles,
            'destinos': destinos_list
        }
    
    def __repr__(self):
        return f'<Paquete {self.nombre}>'


class PaqueteDestino(db.Model):
    __tablename__ = 'paquete_destinos'
    
    paquete_id = db.Column(db.Integer, db.ForeignKey('paquetes.id', ondelete='CASCADE'), primary_key=True)
    destino_id = db.Column(db.Integer, db.ForeignKey('destinos.id', ondelete='CASCADE'), primary_key=True)
    
    paquete = db.relationship('Paquete', back_populates='destinos')
    destino = db.relationship('Destino', back_populates='paquetes')

