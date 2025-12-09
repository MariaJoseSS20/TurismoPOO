from app import db
from datetime import datetime

class Reserva(db.Model):
    __tablename__ = 'reservas'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    paquete_id = db.Column(db.Integer, db.ForeignKey('paquetes.id'), nullable=False)
    fecha_reserva = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='confirmada')
    numero_pasajeros = db.Column(db.Integer, default=1, nullable=False)
    telefono_contacto = db.Column(db.String(20))
    comentarios = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'paquete_id': self.paquete_id,
            'fecha_reserva': self.fecha_reserva.isoformat() if self.fecha_reserva else None,
            'estado': self.estado,
            'numero_pasajeros': self.numero_pasajeros,
            'telefono_contacto': self.telefono_contacto,
            'comentarios': self.comentarios,
            'usuario': self.usuario.to_dict() if self.usuario else None,
            'paquete': self.paquete.to_dict() if self.paquete else None,
            'viajeros': [v.to_dict() for v in self.viajeros] if hasattr(self, 'viajeros') else []
        }
    
    def __repr__(self):
        return f'<Reserva {self.id}>'

