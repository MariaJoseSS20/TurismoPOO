from flask import Blueprint, request, jsonify
from app.models.paquete import Paquete, PaqueteDestino
from app.models.destino import Destino
from datetime import datetime

bp = Blueprint('buscar', __name__)

@bp.route('', methods=['GET'])
def buscar():
    origen = request.args.get('origen', '').strip()
    destino = request.args.get('destino', '').strip()
    fecha_inicio = request.args.get('fecha_inicio', '').strip()
    fecha_fin = request.args.get('fecha_fin', '').strip()
    precio_min = request.args.get('precio_min', '').strip()
    precio_max = request.args.get('precio_max', '').strip()
    
    query = Paquete.query
    
    if origen:
        query = query.filter(Paquete.origen.ilike(f'%{origen}%'))
    
    if destino:
        query = query.join(PaqueteDestino).join(Destino).filter(
            Destino.nombre.ilike(f'%{destino}%')
        )
    
    if fecha_inicio:
        try:
            fecha_ini = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            query = query.filter(Paquete.fecha_inicio >= fecha_ini)
        except:
            pass
    
    if fecha_fin:
        try:
            fecha_f = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            query = query.filter(Paquete.fecha_fin <= fecha_f)
        except:
            pass
    
    if precio_min:
        try:
            query = query.filter(Paquete.precio_total >= float(precio_min))
        except:
            pass
    
    if precio_max:
        try:
            query = query.filter(Paquete.precio_total <= float(precio_max))
        except:
            pass
    
    paquetes = query.distinct().all()
    return jsonify([p.to_dict() for p in paquetes])

