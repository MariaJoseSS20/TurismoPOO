# 🧪 Guía de Pruebas - Proyecto Flask

## 📋 Pre-requisitos

1. **Activar el entorno virtual:**
   ```bash
   source venv/bin/activate
   ```

2. **Verificar que todo esté correcto:**
   ```bash
   python test_app.py
   ```

## 🚀 Ejecutar la Aplicación

### Opción 1: Ejecutar directamente
```bash
python app.py
```

### Opción 2: Usar Flask CLI
```bash
flask run --host=0.0.0.0 --port=5001
```

La aplicación estará disponible en: **http://localhost:5001**

## ✅ Checklist de Pruebas

### 1. **Página Principal** (`/`)
- [ ] La página carga correctamente
- [ ] Se muestran los paquetes destacados
- [ ] El menú de navegación funciona
- [ ] El contador del carrito se actualiza

### 2. **Autenticación** (`/auth`)
- [ ] **Registro** (`/auth/registro`):
  - [ ] Formulario valida campos requeridos
  - [ ] Valida formato de RUT chileno
  - [ ] Valida formato de email
  - [ ] Crea usuario correctamente
  
- [ ] **Login** (`/auth/login`):
  - [ ] Valida credenciales
  - [ ] Redirige según rol (admin/cliente)
  - [ ] Muestra mensajes de error apropiados
  
- [ ] **Perfil** (`/auth/perfil`):
  - [ ] Muestra datos del usuario
  - [ ] Permite actualizar información
  - [ ] Valida cambios antes de guardar

### 3. **Paquetes** (`/paquetes`)
- [ ] Lista todos los paquetes disponibles
- [ ] Filtros funcionan (origen, destino, fechas, precio)
- [ ] Slider de precios funciona correctamente
- [ ] Agregar al carrito funciona
- [ ] **Como Admin:**
  - [ ] Botón "Crear Paquete" visible
  - [ ] Modal de creación funciona
  - [ ] Validación de fechas (fin > inicio)
  - [ ] Cálculo automático de precio
  - [ ] Editar paquete funciona
  - [ ] Eliminar paquete funciona

### 4. **Carrito** (`/carrito`)
- [ ] Muestra items del carrito
- [ ] Permite cambiar número de pasajeros
- [ ] Genera formularios de viajeros dinámicamente
- [ ] Botón "Usar mis datos" funciona (si está logueado)
- [ ] Actualiza totales correctamente
- [ ] Eliminar items funciona
- [ ] Limpiar carrito funciona
- [ ] **Proceder a Reservar:**
  - [ ] Valida que el usuario esté logueado
  - [ ] Valida datos de viajeros
  - [ ] Valida cupos disponibles
  - [ ] Crea reservas correctamente
  - [ ] Limpia el carrito después de reservar

### 5. **Destinos** (`/destinos`)
- [ ] Lista todos los destinos
- [ ] Muestra información completa de cada destino
- [ ] Filtros funcionan correctamente

### 6. **Panel de Administración** (`/admin`)
- [ ] Requiere autenticación de admin
- [ ] Dashboard muestra estadísticas
- [ ] **Gestión de Destinos:**
  - [ ] Crear destino (formulario y API)
  - [ ] Editar destino
  - [ ] Eliminar destino
  - [ ] Validaciones funcionan
  
- [ ] **Gestión de Paquetes:**
  - [ ] Crear paquete (formulario y API)
  - [ ] Editar paquete
  - [ ] Eliminar paquete
  - [ ] Asociar destinos a paquetes
  
- [ ] **Gestión de Reservas:**
  - [ ] Lista todas las reservas
  - [ ] Cambiar estado de reservas
  - [ ] Ver detalles de reservas
  - [ ] Cupos se actualizan correctamente
  
- [ ] **Gestión de Usuarios:**
  - [ ] Lista todos los usuarios
  - [ ] Editar usuarios
  - [ ] Cambiar roles

### 7. **Mis Reservas** (`/mis-reservas`)
- [ ] Muestra solo las reservas del usuario logueado
- [ ] Muestra estado de cada reserva
- [ ] Muestra información de viajeros
- [ ] Filtros funcionan

### 8. **APIs REST**
Probar con herramientas como Postman o curl:

- [ ] `GET /api/paquetes` - Lista paquetes
- [ ] `GET /api/destinos` - Lista destinos
- [ ] `GET /api/carrito` - Obtiene carrito
- [ ] `POST /api/carrito/agregar` - Agrega al carrito
- [ ] `POST /api/reservas` - Crea reserva
- [ ] `GET /api/reservas` - Lista reservas

## 🔍 Verificaciones Técnicas

### JavaScript Separado
- [ ] `paquetes.js` se carga correctamente
- [ ] `carrito.js` se carga correctamente
- [ ] No hay errores en la consola del navegador
- [ ] Funcionalidad JavaScript funciona igual que antes

### Servicios
- [ ] `PaqueteService` maneja lógica de negocio
- [ ] `DestinoService` maneja lógica de negocio
- [ ] `ReservaService` maneja lógica de negocio y cupos
- [ ] Controladores usan servicios (no lógica directa)

### Formularios WTForms
- [ ] Validación del lado del servidor funciona
- [ ] Mensajes de error se muestran correctamente
- [ ] CSRF protection está activo

### Base de Datos
- [ ] Migraciones están aplicadas: `flask db current`
- [ ] Tablas existen y tienen datos
- [ ] Relaciones funcionan correctamente

## 🐛 Problemas Comunes

### Error: "Module not found"
```bash
# Asegúrate de estar en el directorio correcto
cd /Users/mariajose/Desktop/POO
source venv/bin/activate
```

### Error: "Database locked"
- Cierra otras conexiones a la base de datos
- Reinicia la aplicación

### Error: "CSRF token missing"
- Verifica que los formularios incluyan `{{ csrf_token() }}`
- Verifica que `WTF_CSRF_ENABLED = True` en config

### JavaScript no funciona
- Abre la consola del navegador (F12)
- Verifica que los archivos JS se carguen (pestaña Network)
- Verifica que no haya errores de sintaxis

## 📝 Notas

- La aplicación usa MySQL por defecto (configurado en `.env`)
- SQLite está disponible como fallback si no hay `.env` configurado
- El modo debug está activado (muestra errores detallados)
- El puerto por defecto es 5001

## 🎯 Pruebas Recomendadas por Rol

### Como Usuario No Registrado:
1. Navegar paquetes
2. Agregar al carrito
3. Intentar reservar (debe pedir login)
4. Registrarse
5. Completar reserva

### Como Usuario Registrado:
1. Ver perfil
2. Hacer reservas
3. Ver mis reservas
4. Usar datos personales en formularios de viajeros

### Como Administrador:
1. Crear/editar/eliminar destinos
2. Crear/editar/eliminar paquetes
3. Gestionar reservas
4. Ver dashboard con estadísticas
5. Gestionar usuarios

