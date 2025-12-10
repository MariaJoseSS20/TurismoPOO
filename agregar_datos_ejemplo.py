"""
Script para agregar datos de ejemplo SIN eliminar los datos existentes
Útil cuando ya tienes datos y solo quieres agregar más
"""
from app import create_app, db
from config import Config
from app.models.usuario import Usuario
from app.models.destino import Destino
from app.models.paquete import Paquete, PaqueteDestino
from app.models.reserva import Reserva
from datetime import date, timedelta

app = create_app(Config)

with app.app_context():
    # Verificar si ya existen datos
    usuarios_existentes = Usuario.query.count()
    destinos_existentes = Destino.query.count()
    paquetes_existentes = Paquete.query.count()
    
    print(f"📊 Estado actual de la base de datos:")
    print(f"   - Usuarios: {usuarios_existentes}")
    print(f"   - Destinos: {destinos_existentes}")
    print(f"   - Paquetes: {paquetes_existentes}")
    print()
    
    # Solo crear usuarios si no existen
    if usuarios_existentes == 0:
        print("👤 Creando usuarios de ejemplo...")
        u1 = Usuario(
            nombre_completo="María José", 
            rut="12.345.678-9", 
            email="maria@administrador.com", 
            fecha_nacimiento=date(1990, 5, 15),
            rol="cliente"
        )
        u1.set_password("123456")
        
        u2 = Usuario(
            nombre_completo="Administrador Sistema", 
            rut="19.769.702-4",
            email="admin@viajesaventura.com",
            fecha_nacimiento=date(1985, 3, 20),
            rol="admin"
        )
        u2.set_password("admin123")
        
        db.session.add_all([u1, u2])
        db.session.flush()
        print("   ✅ 2 usuarios creados")
    else:
        print("   ⏭️  Ya existen usuarios, omitiendo creación")
        # Obtener usuarios existentes para usar en reservas
        u1 = Usuario.query.filter_by(email="maria@administrador.com").first()
        u2 = Usuario.query.filter_by(email="admin@viajesaventura.com").first()
    
    # Crear destinos adicionales si no existen
    destinos_creados = []
    if Destino.query.filter_by(nombre="Playa del Carmen").first() is None:
        d1 = Destino(nombre="Playa del Carmen", origen="Cancún", 
                     descripcion="Hermosa playa en México con aguas cristalinas", 
                     actividades="Snorkel,Buceo,Relax", costo_base=1500.00)
        db.session.add(d1)
        destinos_creados.append(d1)
    
    if Destino.query.filter_by(nombre="Machu Picchu").first() is None:
        d2 = Destino(nombre="Machu Picchu", origen="Cusco", 
                     descripcion="Ruinas incas en Perú, una de las maravillas del mundo", 
                     actividades="Trekking,Cultura,Historia", costo_base=2000.00)
        db.session.add(d2)
        destinos_creados.append(d2)
    
    if Destino.query.filter_by(nombre="París").first() is None:
        d3 = Destino(nombre="París", origen="Madrid", 
                     descripcion="Ciudad del amor, capital de Francia", 
                     actividades="Museos,Gastronomía,Arquitectura", costo_base=3000.00)
        db.session.add(d3)
        destinos_creados.append(d3)
    
    if destinos_creados:
        db.session.flush()
        print(f"   ✅ {len(destinos_creados)} destinos creados")
    else:
        print("   ⏭️  Los destinos de ejemplo ya existen")
        # Obtener destinos existentes
        d1 = Destino.query.filter_by(nombre="Playa del Carmen").first()
        d2 = Destino.query.filter_by(nombre="Machu Picchu").first()
        d3 = Destino.query.filter_by(nombre="París").first()
    
    # Crear paquetes adicionales (siempre se crean nuevos con fechas futuras)
    print("📦 Creando paquetes adicionales...")
    hoy = date.today()
    
    # Verificar si ya existen paquetes con estos nombres
    nombres_paquetes = ["Verano en el Sur", "Aventura Andina", "Europa Clásica", "Caribe Tropical"]
    paquetes_creados = []
    
    if not Paquete.query.filter_by(nombre="Verano en el Sur").first():
        p1 = Paquete(nombre="Verano en el Sur", origen="Santiago", 
                     fecha_inicio=hoy + timedelta(days=30), 
                     fecha_fin=hoy + timedelta(days=44), precio_total=5000.00, disponibles=20)
        db.session.add(p1)
        paquetes_creados.append(('p1', p1))
    
    if not Paquete.query.filter_by(nombre="Aventura Andina").first():
        p2 = Paquete(nombre="Aventura Andina", origen="Lima", 
                     fecha_inicio=hoy + timedelta(days=60), 
                     fecha_fin=hoy + timedelta(days=69), precio_total=3500.00, disponibles=15)
        db.session.add(p2)
        paquetes_creados.append(('p2', p2))
    
    if not Paquete.query.filter_by(nombre="Europa Clásica").first():
        p3 = Paquete(nombre="Europa Clásica", origen="Punta Arenas", 
                     fecha_inicio=hoy + timedelta(days=90), 
                     fecha_fin=hoy + timedelta(days=104), precio_total=8000.00, disponibles=25)
        db.session.add(p3)
        paquetes_creados.append(('p3', p3))
    
    if not Paquete.query.filter_by(nombre="Caribe Tropical").first():
        p4 = Paquete(nombre="Caribe Tropical", origen="Santiago", 
                     fecha_inicio=hoy + timedelta(days=45), 
                     fecha_fin=hoy + timedelta(days=59), precio_total=6000.00, disponibles=18)
        db.session.add(p4)
        paquetes_creados.append(('p4', p4))
    
    if paquetes_creados:
        db.session.flush()
        print(f"   ✅ {len(paquetes_creados)} paquetes creados")
        
        # Relacionar destinos con paquetes nuevos
        relaciones_creadas = 0
        for nombre_var, paquete in paquetes_creados:
            if nombre_var == 'p1' and d1 and d2:
                if not PaqueteDestino.query.filter_by(paquete_id=paquete.id, destino_id=d1.id).first():
                    db.session.add(PaqueteDestino(paquete_id=paquete.id, destino_id=d1.id))
                    relaciones_creadas += 1
                if not PaqueteDestino.query.filter_by(paquete_id=paquete.id, destino_id=d2.id).first():
                    db.session.add(PaqueteDestino(paquete_id=paquete.id, destino_id=d2.id))
                    relaciones_creadas += 1
            elif nombre_var == 'p2' and d2 and d3:
                if not PaqueteDestino.query.filter_by(paquete_id=paquete.id, destino_id=d2.id).first():
                    db.session.add(PaqueteDestino(paquete_id=paquete.id, destino_id=d2.id))
                    relaciones_creadas += 1
                if not PaqueteDestino.query.filter_by(paquete_id=paquete.id, destino_id=d3.id).first():
                    db.session.add(PaqueteDestino(paquete_id=paquete.id, destino_id=d3.id))
                    relaciones_creadas += 1
            elif nombre_var == 'p3' and d3:
                if not PaqueteDestino.query.filter_by(paquete_id=paquete.id, destino_id=d3.id).first():
                    db.session.add(PaqueteDestino(paquete_id=paquete.id, destino_id=d3.id))
                    relaciones_creadas += 1
            elif nombre_var == 'p4' and d1:
                if not PaqueteDestino.query.filter_by(paquete_id=paquete.id, destino_id=d1.id).first():
                    db.session.add(PaqueteDestino(paquete_id=paquete.id, destino_id=d1.id))
                    relaciones_creadas += 1
        
        if relaciones_creadas > 0:
            print(f"   ✅ {relaciones_creadas} relaciones paquete-destino creadas")
    else:
        print("   ⏭️  Los paquetes de ejemplo ya existen")
    
    # Crear una reserva de ejemplo solo si no existe
    if u1 and not Reserva.query.filter_by(usuario_id=u1.id).first():
        p1 = Paquete.query.filter_by(nombre="Verano en el Sur").first()
        if p1 and p1.disponibles > 0:
            r1 = Reserva(usuario_id=u1.id, paquete_id=p1.id, estado="confirmada", numero_pasajeros=1)
            p1.disponibles -= 1
            db.session.add(r1)
            print("   ✅ 1 reserva de ejemplo creada")
    
    db.session.commit()
    
    print("\n" + "="*60)
    print("✅ PROCESO COMPLETADO")
    print("="*60)
    print(f"📊 Estado final de la base de datos:")
    print(f"   - Usuarios: {Usuario.query.count()}")
    print(f"   - Destinos: {Destino.query.count()}")
    print(f"   - Paquetes: {Paquete.query.count()}")
    print(f"   - Reservas: {Reserva.query.count()}")
    print("\n💡 Este script NO elimina datos existentes")
    print("   Si quieres empezar desde cero, usa: crear_datos_ejemplo.py")

