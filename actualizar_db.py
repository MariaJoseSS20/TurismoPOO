"""
Script para actualizar la base de datos y agregar columnas faltantes
Ejecutar este script cuando el modelo cambie y la BD no esté sincronizada
"""
from app import create_app, db
from config import Config
from sqlalchemy import text

app = create_app(Config)

with app.app_context():
    try:
        # Verificar y agregar columnas faltantes en la tabla reservas
        with db.engine.connect() as conn:
            # Verificar si existe la columna numero_pasajeros
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = 'turismo' 
                AND TABLE_NAME = 'reservas' 
                AND COLUMN_NAME = 'numero_pasajeros'
            """))
            existe = result.fetchone()[0] > 0
            
            if not existe:
                print("Agregando columna numero_pasajeros a la tabla reservas...")
                conn.execute(text("""
                    ALTER TABLE reservas 
                    ADD COLUMN numero_pasajeros INT NOT NULL DEFAULT 1
                """))
                conn.commit()
                print("✅ Columna numero_pasajeros agregada")
            else:
                print("✅ La columna numero_pasajeros ya existe")
            
            # Verificar si existe la columna telefono_contacto
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = 'turismo' 
                AND TABLE_NAME = 'reservas' 
                AND COLUMN_NAME = 'telefono_contacto'
            """))
            existe = result.fetchone()[0] > 0
            
            if not existe:
                print("Agregando columna telefono_contacto a la tabla reservas...")
                conn.execute(text("""
                    ALTER TABLE reservas 
                    ADD COLUMN telefono_contacto VARCHAR(20) NULL
                """))
                conn.commit()
                print("✅ Columna telefono_contacto agregada")
            else:
                print("✅ La columna telefono_contacto ya existe")
            
            # Verificar si existe la columna comentarios
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = 'turismo' 
                AND TABLE_NAME = 'reservas' 
                AND COLUMN_NAME = 'comentarios'
            """))
            existe = result.fetchone()[0] > 0
            
            if not existe:
                print("Agregando columna comentarios a la tabla reservas...")
                conn.execute(text("""
                    ALTER TABLE reservas 
                    ADD COLUMN comentarios TEXT NULL
                """))
                conn.commit()
                print("✅ Columna comentarios agregada")
            else:
                print("✅ La columna comentarios ya existe")
        
        print("\n✅ Base de datos actualizada correctamente")
        
    except Exception as e:
        print(f"❌ Error al actualizar la base de datos: {e}")
        db.session.rollback()
