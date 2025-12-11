"""
Servicio para gestión de destinos
Contiene la lógica de negocio para crear, editar y eliminar destinos
"""
from app import db
from app.models.destino import Destino
from app.models.paquete import PaqueteDestino


class DestinoService:
    """Servicio para operaciones con destinos"""
    
    @staticmethod
    def crear_destino(datos):
        """
        Crear un nuevo destino
        
        Args:
            datos: dict con los datos del destino:
                - nombre: str
                - origen: str (opcional)
                - descripcion: str (opcional)
                - actividades: str (opcional)
                - costo_base: float
        
        Returns:
            Destino: El destino creado
        """
        destino = Destino(
            nombre=datos['nombre'],
            origen=datos.get('origen'),
            descripcion=datos.get('descripcion'),
            actividades=datos.get('actividades'),
            costo_base=datos['costo_base']
        )
        db.session.add(destino)
        db.session.commit()
        return destino
    
    @staticmethod
    def actualizar_destino(destino_id, datos):
        """
        Actualizar un destino existente
        
        Args:
            destino_id: int - ID del destino
            datos: dict con los datos a actualizar
        
        Returns:
            Destino: El destino actualizado
        """
        destino = Destino.query.get_or_404(destino_id)
        
        if 'nombre' in datos:
            destino.nombre = datos['nombre']
        if 'origen' in datos:
            destino.origen = datos['origen']
        if 'descripcion' in datos:
            destino.descripcion = datos['descripcion']
        if 'actividades' in datos:
            destino.actividades = datos['actividades']
        if 'costo_base' in datos:
            destino.costo_base = datos['costo_base']
        
        db.session.commit()
        return destino
    
    @staticmethod
    def eliminar_destino(destino_id):
        """
        Eliminar un destino
        
        Args:
            destino_id: int - ID del destino
        
        Returns:
            str: Nombre del destino eliminado
        
        Raises:
            ValueError: Si el destino está incluido en algún paquete
        """
        destino = Destino.query.get_or_404(destino_id)
        nombre = destino.nombre
        
        # Verificar si el destino está incluido en algún paquete
        paquetes_con_destino = PaqueteDestino.query.filter_by(destino_id=destino_id).all()
        
        if paquetes_con_destino:
            raise ValueError(
                'No se puede eliminar un destino que está incluido en algún paquete. '
            )
        
        db.session.delete(destino)
        db.session.commit()
        return nombre

