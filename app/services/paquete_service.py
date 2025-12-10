"""
Servicio para gestión de paquetes
Contiene la lógica de negocio para crear, editar y eliminar paquetes
"""
from app import db
from app.models.paquete import Paquete, PaqueteDestino
from app.models.destino import Destino
from datetime import date


class PaqueteService:
    """Servicio para operaciones con paquetes"""
    
    @staticmethod
    def crear_paquete(datos):
        """
        Crear un nuevo paquete
        
        Args:
            datos: dict con los datos del paquete:
                - nombre: str
                - origen: str (opcional)
                - fecha_inicio: date
                - fecha_fin: date
                - precio_total: float
                - disponibles: int
                - destinos: list[int] (IDs de destinos)
        
        Returns:
            Paquete: El paquete creado
        
        Raises:
            ValueError: Si los datos son inválidos
        """
        # Validar fechas
        if datos['fecha_fin'] < datos['fecha_inicio']:
            raise ValueError('La fecha fin debe ser posterior a la fecha inicio')
        
        # Crear paquete
        paquete = Paquete(
            nombre=datos['nombre'],
            origen=datos.get('origen'),
            fecha_inicio=datos['fecha_inicio'],
            fecha_fin=datos['fecha_fin'],
            precio_total=datos['precio_total'],
            disponibles=datos.get('disponibles', 20)
        )
        db.session.add(paquete)
        db.session.flush()
        
        # Agregar destinos
        destinos_ids = datos.get('destinos', [])
        for destino_id in destinos_ids:
            destino = Destino.query.get(destino_id)
            if destino:
                db.session.add(PaqueteDestino(
                    paquete_id=paquete.id,
                    destino_id=destino_id
                ))
        
        db.session.commit()
        return paquete
    
    @staticmethod
    def actualizar_paquete(paquete_id, datos):
        """
        Actualizar un paquete existente
        
        Args:
            paquete_id: int - ID del paquete
            datos: dict con los datos a actualizar
        
        Returns:
            Paquete: El paquete actualizado
        
        Raises:
            ValueError: Si los datos son inválidos
        """
        paquete = Paquete.query.get_or_404(paquete_id)
        
        # Validar fechas si se proporcionan
        if 'fecha_inicio' in datos and 'fecha_fin' in datos:
            if datos['fecha_fin'] < datos['fecha_inicio']:
                raise ValueError('La fecha fin debe ser posterior a la fecha inicio')
        
        # Actualizar campos
        if 'nombre' in datos:
            paquete.nombre = datos['nombre']
        if 'origen' in datos:
            paquete.origen = datos['origen']
        if 'fecha_inicio' in datos:
            paquete.fecha_inicio = datos['fecha_inicio']
        if 'fecha_fin' in datos:
            paquete.fecha_fin = datos['fecha_fin']
        if 'precio_total' in datos:
            paquete.precio_total = datos['precio_total']
        if 'disponibles' in datos:
            paquete.disponibles = datos['disponibles']
        
        # Actualizar destinos si se proporcionan
        if 'destinos' in datos:
            # Eliminar destinos existentes
            PaqueteDestino.query.filter_by(paquete_id=paquete.id).delete()
            # Agregar nuevos destinos
            for destino_id in datos['destinos']:
                destino = Destino.query.get(destino_id)
                if destino:
                    db.session.add(PaqueteDestino(
                        paquete_id=paquete.id,
                        destino_id=destino_id
                    ))
        
        db.session.commit()
        return paquete
    
    @staticmethod
    def eliminar_paquete(paquete_id):
        """
        Eliminar un paquete
        
        Args:
            paquete_id: int - ID del paquete
        
        Returns:
            str: Nombre del paquete eliminado
        """
        paquete = Paquete.query.get_or_404(paquete_id)
        nombre = paquete.nombre
        db.session.delete(paquete)
        db.session.commit()
        return nombre

