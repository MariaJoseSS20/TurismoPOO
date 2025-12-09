from app import create_app, db
from config import Config
from app.models.usuario import Usuario
from app.models.destino import Destino
from app.models.paquete import Paquete, PaqueteDestino
from app.models.reserva import Reserva
from datetime import date

app = create_app(Config)

with app.app_context():
    # Limpiar datos existentes
    db.session.query(Reserva).delete()
    db.session.query(PaqueteDestino).delete()
    db.session.query(Paquete).delete()
    db.session.query(Destino).delete()
    db.session.query(Usuario).delete()
    
    # Crear usuarios
    u1 = Usuario(nombre_completo="María José", rut="12.345.678-9", email="maria@administrador.com", rol="cliente")
    u1.set_password("123456")
    
    # Usuario administrador con RUT válido chileno y datos realistas
    u2 = Usuario(
        nombre_completo="Administrador Sistema", 
        rut="19.769.702-4",  # RUT válido chileno
        email="admin@viajesaventura.com", 
        rol="admin"
    )
    u2.set_password("admin123")  # Contraseña hasheada con werkzeug
    
    db.session.add_all([u1, u2])
    db.session.flush()
    
    # Crear destinos con origen
    d1 = Destino(nombre="Playa del Carmen", origen="Cancún", 
                 descripcion="Hermosa playa en México con aguas cristalinas", 
                 actividades="Snorkel,Buceo,Relax", costo_base=1500.00)
    d2 = Destino(nombre="Machu Picchu", origen="Cusco", 
                 descripcion="Ruinas incas en Perú, una de las maravillas del mundo", 
                 actividades="Trekking,Cultura,Historia", costo_base=2000.00)
    d3 = Destino(nombre="París", origen="Madrid", 
                 descripcion="Ciudad del amor, capital de Francia", 
                 actividades="Museos,Gastronomía,Arquitectura", costo_base=3000.00)
    
    db.session.add_all([d1, d2, d3])
    db.session.flush()
    
    # Crear paquetes con origen
    p1 = Paquete(nombre="Verano en el Sur", origen="Santiago", 
                 fecha_inicio=date(2024, 7, 1), 
                 fecha_fin=date(2024, 7, 15), precio_total=5000.00, disponibles=20)
    p2 = Paquete(nombre="Aventura Andina", origen="Lima", 
                 fecha_inicio=date(2024, 8, 1), 
                 fecha_fin=date(2024, 8, 10), precio_total=3500.00, disponibles=15)
    
    db.session.add_all([p1, p2])
    db.session.flush()
    
    # Relacionar destinos con paquetes
    db.session.add(PaqueteDestino(paquete_id=p1.id, destino_id=d1.id))
    db.session.add(PaqueteDestino(paquete_id=p1.id, destino_id=d2.id))
    db.session.add(PaqueteDestino(paquete_id=p2.id, destino_id=d2.id))
    db.session.add(PaqueteDestino(paquete_id=p2.id, destino_id=d3.id))
    
    # Crear reservas
    r1 = Reserva(usuario_id=u1.id, paquete_id=p1.id, estado="confirmada")
    p1.disponibles -= 1
    
    db.session.add(r1)
    db.session.commit()
    
    print("✅ Datos de ejemplo creados:")
    print(f"   - 2 usuarios")
    print(f"   - 3 destinos")
    print(f"   - 2 paquetes")
    print(f"   - 1 reserva")
    print("\n📋 Credenciales de Administrador:")
        print(f"   Email: admin@viajesaventura.com")
    print(f"   Contraseña: admin123")
    print(f"   RUT: 19.769.702-4")
    print(f"   Nombre: Administrador Sistema")
    print(f"\n💡 La contraseña está hasheada con werkzeug.security")
    print(f"   El RUT es válido según el algoritmo chileno")
    print(f"\n📋 Credenciales de Cliente de Prueba:")
    print(f"   Email: maria@administrador.com")
    print(f"   Contraseña: 123456")

