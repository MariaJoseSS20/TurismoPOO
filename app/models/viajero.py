from app import db

class Viajero(db.Model):
    __tablename__ = 'pasajeros'
    
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    nombre_completo = db.Column(db.String(200), nullable=False)
    rut = db.Column(db.String(20), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    reserva = db.relationship('Reserva', backref='viajeros', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'reserva_id': self.reserva_id,
            'nombre_completo': self.nombre_completo,
            'rut': self.rut,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'telefono': self.telefono,
            'email': self.email
        }
    
    def __repr__(self):
        return f'<Viajero {self.nombre_completo}>'
