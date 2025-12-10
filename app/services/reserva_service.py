"""
Servicio para gestión de reservas
Contiene la lógica de negocio para crear, editar y eliminar reservas
"""
from app import db
from app.models.reserva import Reserva
from app.models.paquete import Paquete
from app.models.viajero import Viajero
from datetime import datetime


class ReservaService:
    """Servicio para operaciones con reservas"""
    
    @staticmethod
    def crear_reserva(usuario_id, datos):
        """
        Crear una nueva reserva
        
        Args:
            usuario_id: int - ID del usuario que hace la reserva
            datos: dict con los datos de la reserva:
                - paquete_id: int
                - estado: str (opcional, default 'confirmada')
                - numero_pasajeros: int
                - telefono_contacto: str (opcional)
                - comentarios: str (opcional)
                - viajeros: list[dict] (opcional) - Datos de los viajeros
        
        Returns:
            Reserva: La reserva creada
        
        Raises:
            ValueError: Si los datos son inválidos o no hay cupos disponibles
        """
        paquete = Paquete.query.get_or_404(datos['paquete_id'])
        numero_pasajeros = datos.get('numero_pasajeros', 1)
        
        if numero_pasajeros < 1:
            raise ValueError('El número de pasajeros debe ser al menos 1')
        
        if paquete.disponibles < numero_pasajeros:
            raise ValueError(
                f'No hay suficientes cupos disponibles. '
                f'Disponibles: {paquete.disponibles}, Solicitados: {numero_pasajeros}'
            )
        
        # Crear reserva
        reserva = Reserva(
            usuario_id=usuario_id,
            paquete_id=datos['paquete_id'],
            estado=datos.get('estado', 'confirmada'),
            numero_pasajeros=numero_pasajeros,
            telefono_contacto=datos.get('telefono_contacto'),
            comentarios=datos.get('comentarios')
        )
        
        # Reducir cupos disponibles
        paquete.disponibles -= numero_pasajeros
        
        db.session.add(reserva)
        db.session.flush()  # Para obtener el ID de la reserva
        
        # Guardar datos de viajeros si se proporcionan
        viajeros_data = datos.get('viajeros', [])
        if viajeros_data:
            for viajero_data in viajeros_data:
                fecha_nacimiento = None
                if viajero_data.get('fecha_nacimiento'):
                    try:
                        fecha_nacimiento = datetime.strptime(
                            viajero_data['fecha_nacimiento'], 
                            '%Y-%m-%d'
                        ).date()
                    except (ValueError, TypeError):
                        pass
                
                # Validar que el teléfono esté presente (obligatorio)
                telefono = viajero_data.get('telefono', '').strip()
                if not telefono:
                    raise ValueError('El teléfono del viajero es obligatorio')
                
                viajero = Viajero(
                    reserva_id=reserva.id,
                    nombre_completo=viajero_data.get('nombre_completo', ''),
                    rut=viajero_data.get('rut', ''),
                    fecha_nacimiento=fecha_nacimiento,
                    telefono=telefono,
                    email=viajero_data.get('email')
                )
                db.session.add(viajero)
        
        db.session.commit()
        return reserva
    
    @staticmethod
    def actualizar_estado_reserva(reserva_id, nuevo_estado):
        """
        Actualizar el estado de una reserva
        
        Args:
            reserva_id: int - ID de la reserva
            nuevo_estado: str - Nuevo estado ('confirmada', 'cancelada')
        
        Returns:
            Reserva: La reserva actualizada
        
        Raises:
            ValueError: Si no hay cupos suficientes al reconfirmar
        """
        reserva = Reserva.query.get_or_404(reserva_id)
        estado_anterior = reserva.estado
        
        reserva.estado = nuevo_estado
        
        # Manejar cambios de estado que afectan cupos
        if estado_anterior == 'confirmada' and nuevo_estado == 'cancelada':
            # Devolver cupos al paquete
            reserva.paquete.disponibles += reserva.numero_pasajeros
        elif estado_anterior == 'cancelada' and nuevo_estado == 'confirmada':
            # Verificar que haya cupos disponibles
            if reserva.paquete.disponibles < reserva.numero_pasajeros:
                raise ValueError('No hay cupos suficientes para reconfirmar esta reserva')
            reserva.paquete.disponibles -= reserva.numero_pasajeros
        
        db.session.commit()
        return reserva
    
    @staticmethod
    def eliminar_reserva(reserva_id):
        """
        Eliminar una reserva
        
        Args:
            reserva_id: int - ID de la reserva
        
        Returns:
            str: Mensaje de confirmación
        """
        reserva = Reserva.query.get_or_404(reserva_id)
        
        # Si estaba confirmada, devolver cupos
        if reserva.estado == 'confirmada':
            reserva.paquete.disponibles += reserva.numero_pasajeros
        
        db.session.delete(reserva)
        db.session.commit()
        return 'Reserva eliminada exitosamente'

