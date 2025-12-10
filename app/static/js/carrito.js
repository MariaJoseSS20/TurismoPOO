/**
 * JavaScript para la página de carrito
 * Maneja la visualización, actualización y reserva de items del carrito
 */

// Variables globales
let carritoItems = [];
let carritoTotal = 0;
let usuarioData = null;
let tieneUsuario = false;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    // Obtener datos del usuario desde data attributes
    const carritoPage = document.getElementById('carrito-page');
    if (carritoPage) {
        const usuarioDataJson = carritoPage.dataset.usuarioData;
        console.log('Usuario data JSON raw:', usuarioDataJson);
        if (usuarioDataJson && usuarioDataJson !== 'null' && usuarioDataJson.trim() !== '') {
            try {
                // Limpiar el JSON si tiene caracteres problemáticos de HTML
                let cleanedJson = usuarioDataJson
                    .replace(/&quot;/g, '"')
                    .replace(/&#39;/g, "'")
                    .replace(/&amp;/g, '&')
                    .replace(/&lt;/g, '<')
                    .replace(/&gt;/g, '>');
                usuarioData = JSON.parse(cleanedJson);
                console.log('Usuario data cargado:', usuarioData);
            } catch (e) {
                console.error('Error parsing usuario data:', e);
                console.error('Raw data:', usuarioDataJson);
                usuarioData = null; // Asegurar que sea null si hay error
            }
        } else {
            console.log('No hay datos de usuario o es null');
            usuarioData = null;
        }
        tieneUsuario = carritoPage.dataset.tieneUsuario === 'true';
        console.log('Tiene usuario:', tieneUsuario, 'Usuario data:', usuarioData);
    }
    
    cargarCarrito();
});

/**
 * Cargar carrito desde la API
 */
async function cargarCarrito() {
    try {
        const response = await fetch('/api/carrito');
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error al cargar carrito:', response.status, errorText);
            throw new Error(`Error ${response.status}: ${errorText}`);
        }
        const data = await response.json();
        carritoItems = data.items || [];
        carritoTotal = data.total || 0;
        mostrarCarrito();
        actualizarContadorCarrito();
    } catch (error) {
        console.error('Error en cargarCarrito:', error);
        const container = document.getElementById('carrito-container');
        if (container) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle-fill"></i> Error al cargar el carrito: ${error.message}
                        <br><small>Abre la consola (F12) para más detalles</small>
                    </div>
                </div>
            `;
        }
    }
}

/**
 * Mostrar el carrito en el contenedor
 */
function mostrarCarrito() {
    const container = document.getElementById('carrito-container');
    if (!container) return;
    
    if (!carritoItems || carritoItems.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="card">
                    <div class="card-body p-5 text-center">
                        <i class="bi bi-cart-x text-muted" style="font-size: 4rem;"></i>
                        <h3 class="mt-3 text-muted">Tu carrito está vacío</h3>
                        <p class="text-muted">Agrega paquetes para comenzar</p>
                        <a href="/paquetes" class="btn btn-primary">
                            <i class="bi bi-box-seam me-2"></i>Ver Paquetes
                        </a>
                    </div>
                </div>
            </div>
        `;
        return;
    }
    
    const total = carritoTotal || carritoItems.reduce((sum, item) => sum + (item.subtotal || (item.precio || 0) * (item.cantidad || 1)), 0);
    
    let html = '<div class="col-lg-8 mb-4">';
    
    carritoItems.forEach((item, index) => {
        const cantidad = item.cantidad || 1;
        const precioUnitario = item.precio || 0;
        const subtotal = item.subtotal || (precioUnitario * cantidad);
        
        if (item.tipo === 'paquete') {
            const fechaInicio = item.fecha_inicio ? new Date(item.fecha_inicio).toLocaleDateString('es-ES') : 'N/A';
            const fechaFin = item.fecha_fin ? new Date(item.fecha_fin).toLocaleDateString('es-ES') : 'N/A';
            const paqueteId = item.id;
            // Usar timestamp o carrito_index como identificador único para este item específico
            // Convertir a string para evitar problemas con números decimales
            const itemUniqueId = String(item.timestamp || item.carrito_index || index);
            const maxCupos = item.disponibles || 1;
            html += `
                <div class="card mb-3 border-primary" data-paquete-id="${paqueteId}" data-item-id="${itemUniqueId}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h5 class="card-title text-dark fw-bold mb-2">
                                    <i class="bi bi-box-seam me-2"></i>${item.nombre}
                                </h5>
                                <p class="text-muted small mb-1">
                                    <i class="bi bi-calendar3 me-1"></i>${fechaInicio} - ${fechaFin}
                                </p>
                                ${item.disponibles !== undefined ? `
                                    <div class="mb-2">
                                        <span class="badge ${item.disponibles > 0 ? 'badge-cupos' : 'bg-danger'}">
                                            ${item.disponibles > 0 ? `${item.disponibles} cupos disponibles` : 'Agotado'}
                                        </span>
                                    </div>
                                ` : ''}
                                <div class="mt-2">
                                    <small class="text-muted">
                                        Precio unitario: <strong>${formatCLP(precioUnitario)}</strong>
                                    </small>
                                </div>
                            </div>
                            <div class="text-end ms-3">
                                <div class="mb-2">
                                    <small class="text-muted d-block">Subtotal</small>
                                    <h4 class="text-primary mb-0">${formatCLP(subtotal)}</h4>
                                </div>
                                <button class="btn btn-sm btn-outline-danger" onclick="eliminarDelCarrito('${item.tipo}', ${item.id}, ${item.timestamp ? item.timestamp : (item.carrito_index !== undefined ? item.carrito_index : 'null')}, ${item.carrito_index !== undefined ? item.carrito_index : 'null'})">
                                    <i class="bi bi-trash me-1"></i>Eliminar
                                </button>
                            </div>
                        </div>
                        
                        ${item.destinos && item.destinos.length > 0 ? `
                            <div class="mb-3">
                                ${item.destinos.map(destino => `
                                    <div class="mb-2 p-2 rounded border-start border-primary border-3 bg-light">
                                        <h6 class="text-dark fw-bold mb-1">
                                            <i class="bi bi-geo-alt-fill text-danger me-1"></i>${destino.nombre}
                                        </h6>
                                        ${destino.descripcion ? `
                                            <p class="small text-muted mb-2 text-center">${destino.descripcion}</p>
                                        ` : ''}
                                        ${destino.actividades && destino.actividades.length > 0 ? `
                                            <div class="d-flex flex-wrap gap-1 justify-content-center">
                                                ${destino.actividades.map(actividad => `
                                                    <span class="badge bg-purple-pastel text-purple-dark fw-bold">${actividad.trim()}</span>
                                                `).join('')}
                                            </div>
                                        ` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                        
                        <hr class="my-3">
                        
                        <div class="datos-viajero-paquete" data-paquete-id="${paqueteId}" data-item-id="${itemUniqueId}">
                            <div class="mb-3">
                                <label class="form-label fw-bold">Número de Pasajeros <span class="text-danger">*</span></label>
                                <input type="number" class="form-control numero-pasajeros-paquete" 
                                       data-paquete-id="${paqueteId}" 
                                       data-item-id="${itemUniqueId}"
                                       data-precio="${precioUnitario}"
                                       min="1" 
                                       max="${maxCupos}" 
                                       value="1" 
                                       required>
                                <small class="text-muted">Máximo ${maxCupos} pasajero(s)</small>
                                <div class="error-cupos-paquete text-danger small mt-1" data-item-id="${itemUniqueId}" style="display: none;"></div>
                            </div>
                            <div class="mb-3">
                                <div class="d-flex justify-content-between align-items-center p-2 bg-light rounded">
                                    <span class="fw-bold">Total del Paquete:</span>
                                    <span class="h5 mb-0 text-primary total-paquete" data-item-id="${itemUniqueId}">${formatCLP(precioUnitario)}</span>
                                </div>
                                <small class="text-muted">Precio unitario: ${formatCLP(precioUnitario)} × <span class="cantidad-pasajeros-display" data-item-id="${itemUniqueId}">1</span> pasajero(s)</small>
                            </div>
                            <div class="viajeros-container-paquete" data-item-id="${itemUniqueId}">
                                <!-- Se llenará dinámicamente con formularios para cada viajero -->
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    });
    
    html += '</div>';
    
    function calcularTotalCarrito() {
        let total = 0;
        carritoItems.forEach((item, index) => {
            if (item.tipo === 'paquete') {
                const itemId = String(item.timestamp || item.carrito_index || index);
                const numeroPasajerosInput = document.querySelector(`.numero-pasajeros-paquete[data-item-id="${itemId}"]`);
                const numPasajeros = numeroPasajerosInput ? parseInt(numeroPasajerosInput.value) || 1 : 1;
                total += (item.precio || 0) * numPasajeros;
            }
        });
        return total;
    }
    
    const cantidadTotalItems = carritoItems.reduce((sum, item) => sum + (item.cantidad || 1), 0);
    let subtotalCalculado = calcularTotalCarrito();
    
    html += `
        <div class="col-lg-4">
            <div class="card sticky-top" style="top: 20px;">
                <div class="card-body">
                    <h5 class="card-title mb-4">Resumen de Compra</h5>
                    
                    ${carritoItems.map((item, index) => {
                        const cantidad = item.cantidad || 1;
                        const precioUnitario = item.precio || 0;
                        const itemId = String(item.timestamp || item.carrito_index || index);
                        let subtotal = item.subtotal || (precioUnitario * cantidad);
                        let descripcion = `${cantidad} × ${formatCLP(precioUnitario)}`;
                        
                        if (item.tipo === 'paquete') {
                            descripcion = `1 paquete × ${formatCLP(precioUnitario)}`;
                            subtotal = precioUnitario;
                        }
                        
                        return `
                            <div class="mb-3 pb-3 border-bottom resumen-item" data-item-id="${itemId}" data-item-tipo="${item.tipo}">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <span class="small text-muted">${item.nombre}</span>
                                </div>
                                <div class="d-flex justify-content-between small mb-1">
                                    <span class="text-muted resumen-descripcion" data-item-id="${itemId}">${descripcion}</span>
                                    <strong class="resumen-subtotal" data-item-id="${itemId}">${formatCLP(subtotal)}</strong>
                                </div>
                            </div>
                        `;
                    }).join('')}
                    
                    <hr>
                    <div class="d-flex justify-content-between align-items-center mb-2 small text-muted">
                        <span>${carritoItems.length} ${carritoItems.length === 1 ? 'producto' : 'productos'} (${cantidadTotalItems} ${cantidadTotalItems === 1 ? 'unidad' : 'unidades'})</span>
                    </div>
                    <div class="d-flex justify-content-between mb-4 p-3 bg-light rounded">
                        <h5 class="mb-0 fw-bold">Total:</h5>
                        <h4 class="text-primary mb-0 fw-bold" id="carrito-total-final">${formatCLP(subtotalCalculado)}</h4>
                    </div>
                    <button class="btn btn-primary w-100 mb-2" onclick="procederReserva()">
                        <i class="bi bi-check-circle-fill me-2"></i>Proceder a Reservar
                    </button>
                    <button class="btn btn-outline-secondary w-100" onclick="limpiarCarrito()">
                        <i class="bi bi-trash me-2"></i>Limpiar Carrito
                    </button>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Agregar listeners a los inputs de número de pasajeros
    document.querySelectorAll('.numero-pasajeros-paquete').forEach(input => {
        input.addEventListener('input', function() {
            const itemId = this.getAttribute('data-item-id');
            const paqueteId = this.getAttribute('data-paquete-id');
            const numPasajeros = parseInt(this.value) || 0;
            const maxCupos = parseInt(this.getAttribute('max')) || 1;
            const precioUnitario = parseFloat(this.getAttribute('data-precio')) || 0;
            const errorDiv = document.querySelector(`.error-cupos-paquete[data-item-id="${itemId}"]`);
            const viajerosContainer = document.querySelector(`.viajeros-container-paquete[data-item-id="${itemId}"]`);
            const totalDiv = document.querySelector(`.total-paquete[data-item-id="${itemId}"]`);
            const cantidadDisplay = document.querySelector(`.cantidad-pasajeros-display[data-item-id="${itemId}"]`);
            
            if (!viajerosContainer) {
                console.error('No se encontró el contenedor de viajeros para itemId:', itemId);
                return;
            }
            
            if (numPasajeros > maxCupos) {
                if (errorDiv) {
                    errorDiv.textContent = `Máximo ${maxCupos} pasajero(s) disponible(s)`;
                    errorDiv.style.display = 'block';
                }
                this.setCustomValidity(`Máximo ${maxCupos} pasajero(s)`);
                viajerosContainer.innerHTML = '';
            } else {
                if (errorDiv) {
                    errorDiv.style.display = 'none';
                }
                this.setCustomValidity('');
                generarFormulariosViajerosPaquete(paqueteId, itemId, numPasajeros, viajerosContainer);
                
                const total = precioUnitario * numPasajeros;
                if (totalDiv) {
                    totalDiv.textContent = formatCLP(total);
                }
                if (cantidadDisplay) {
                    cantidadDisplay.textContent = numPasajeros;
                }
                
                actualizarResumenCompra();
            }
        });
        
        // Inicializar formularios de viajeros al cargar
        const itemId = input.getAttribute('data-item-id');
        const paqueteId = input.getAttribute('data-paquete-id');
        const numPasajeros = parseInt(input.value) || 1;
        const viajerosContainer = document.querySelector(`.viajeros-container-paquete[data-item-id="${itemId}"]`);
        if (viajerosContainer && itemId && paqueteId) {
            generarFormulariosViajerosPaquete(paqueteId, itemId, numPasajeros, viajerosContainer);
        }
    });
}

/**
 * Actualizar el resumen de compra
 */
function actualizarResumenCompra() {
    let total = 0;
    
    carritoItems.forEach((item, index) => {
        if (item.tipo === 'paquete') {
            const itemId = String(item.timestamp || item.carrito_index || index);
            const numeroPasajerosInput = document.querySelector(`.numero-pasajeros-paquete[data-item-id="${itemId}"]`);
            const numPasajeros = numeroPasajerosInput ? parseInt(numeroPasajerosInput.value) || 1 : 1;
            const precioUnitario = item.precio || 0;
            const subtotalPaquete = precioUnitario * numPasajeros;
            total += subtotalPaquete;
            
            const subtotalDiv = document.querySelector(`.resumen-subtotal[data-item-id="${itemId}"]`);
            const descripcionDiv = document.querySelector(`.resumen-descripcion[data-item-id="${itemId}"]`);
            if (subtotalDiv) {
                subtotalDiv.textContent = formatCLP(subtotalPaquete);
            }
            if (descripcionDiv) {
                descripcionDiv.textContent = `${numPasajeros} pasajero(s) × ${formatCLP(precioUnitario)}`;
            }
        } else {
            const subtotal = item.subtotal || (item.precio || 0) * (item.cantidad || 1);
            total += subtotal;
        }
    });
    
    const totalFinalDiv = document.getElementById('carrito-total-final');
    if (totalFinalDiv) {
        totalFinalDiv.textContent = formatCLP(total);
    }
}

/**
 * Generar formularios de viajeros para un paquete
 */
function generarFormulariosViajerosPaquete(paqueteId, itemId, numViajeros, container) {
    if (!container) {
        console.error('Container no encontrado para generar formularios de viajeros', {
            paqueteId,
            itemId,
            numViajeros
        });
        return;
    }
    
    if (!paqueteId || !itemId) {
        console.error('Faltan parámetros requeridos:', { paqueteId, itemId });
        return;
    }
    
    container.innerHTML = '';
    
    container.innerHTML = '<h6 class="fw-bold mb-3 text-secondary"><i class="bi bi-people-fill me-2"></i>Datos del Viajero</h6>';
    
    for (let i = 1; i <= numViajeros; i++) {
        const tieneUsuarioData = usuarioData !== null && usuarioData !== undefined;
        const botonUsarDatos = tieneUsuarioData ? `
            <button type="button" class="btn btn-sm btn-light" onclick="usarDatosUsuario(${paqueteId}, '${itemId}', ${i})" title="Rellenar con mis datos personales">
                <i class="bi bi-person-check me-1"></i>Usar mis datos
            </button>
        ` : '';
        container.innerHTML += `
            <div class="card mb-3 border-secondary">
                <div class="card-header bg-secondary text-white d-flex justify-content-between align-items-center">
                    <strong>Viajero ${i} ${i === 1 ? '(Titular)' : ''}</strong>
                    ${botonUsarDatos}
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label fw-bold">Nombre Completo <span class="text-danger">*</span></label>
                            <input type="text" class="form-control viajero-nombre" data-paquete-id="${paqueteId}" data-item-id="${itemId}" data-viajero="${i}" 
                                   placeholder="Ej: Juan Pérez" required
                                   pattern="[A-Za-zÁÉÍÓÚáéíóúÑñ\\s]{2,200}"
                                   title="Solo letras y espacios, mínimo 2 caracteres">
                            <div class="invalid-feedback viajero-nombre-error" data-item-id="${itemId}" data-viajero="${i}" style="display: none;">
                                El nombre solo puede contener letras y espacios (mínimo 2 caracteres)
                            </div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label fw-bold">RUT <span class="text-danger">*</span></label>
                            <input type="text" class="form-control viajero-rut" data-paquete-id="${paqueteId}" data-item-id="${itemId}" data-viajero="${i}" 
                                   placeholder="12.345.678-9" required
                                   maxlength="12">
                            <div class="invalid-feedback viajero-rut-error" data-item-id="${itemId}" data-viajero="${i}" style="display: none;">
                                El RUT no es válido. Verifica el formato (ej: 12.345.678-9) y el dígito verificador
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label class="form-label fw-bold">Fecha de Nacimiento</label>
                            <input type="text" class="form-control viajero-fecha" data-paquete-id="${paqueteId}" data-item-id="${itemId}" data-viajero="${i}" placeholder="dd/mm/yyyy">
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label fw-bold">Teléfono <span class="text-danger">*</span></label>
                            <input type="tel" class="form-control viajero-telefono" data-paquete-id="${paqueteId}" data-item-id="${itemId}" data-viajero="${i}" 
                                   placeholder="+56 9 1234 5678" 
                                   pattern="[\\+]?[0-9\\s\\-\\(\\)]{8,20}" 
                                   title="Formato: +56 9 1234 5678 o 912345678"
                                   required>
                            <div class="invalid-feedback viajero-telefono-error" data-item-id="${itemId}" data-viajero="${i}" style="display: none;">
                                El teléfono es requerido y debe tener un formato válido
                            </div>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label fw-bold">Email</label>
                            <input type="email" class="form-control viajero-email" data-paquete-id="${paqueteId}" data-item-id="${itemId}" data-viajero="${i}" 
                                   placeholder="email@ejemplo.com">
                            <div class="invalid-feedback viajero-email-error" data-item-id="${itemId}" data-viajero="${i}" style="display: none;">
                                El email no tiene un formato válido
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Inicializar Flatpickr para fechas
    if (typeof flatpickr !== 'undefined') {
        const fechaInputs = container.querySelectorAll('.viajero-fecha');
        fechaInputs.forEach(input => {
            flatpickr(input, {
                locale: 'es',
                dateFormat: 'd/m/Y',
                maxDate: 'today',
                allowInput: true,
                clickOpens: true,
                theme: 'default',
                appendTo: document.body,
                monthSelectorType: 'static',
                animate: true,
                altInput: false,
                disableMobile: false,
                parseDate: function(datestr, format) {
                    if (datestr && datestr.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
                        const parts = datestr.split('/');
                        return new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));
                    }
                    return null;
                }
            });
        });
    }
    
    // Agregar validaciones en tiempo real
    agregarValidacionesViajero(container, itemId);
}

/**
 * Validar RUT chileno
 */
function validarRutChileno(rutRaw) {
    if (!rutRaw) return false;
    
    const rut = rutRaw.replace(/\./g, '').replace(/-/g, '').trim().toUpperCase();
    if (rut.length < 2) return false;
    
    const cuerpo = rut.slice(0, -1);
    const dv = rut.slice(-1);
    
    if (!/^\d+$/.test(cuerpo)) return false;
    
    // Calcular dígito verificador
    let suma = 0;
    let multiplicador = 2;
    for (let i = cuerpo.length - 1; i >= 0; i--) {
        suma += parseInt(cuerpo[i]) * multiplicador;
        multiplicador++;
        if (multiplicador > 7) multiplicador = 2;
    }
    
    const resto = suma % 11;
    let dvCalc = 11 - resto;
    if (dvCalc === 11) dvCalc = '0';
    else if (dvCalc === 10) dvCalc = 'K';
    else dvCalc = String(dvCalc);
    
    return dv === dvCalc;
}

/**
 * Validar nombre (solo letras y espacios)
 */
function validarNombre(nombre) {
    if (!nombre || nombre.trim().length < 2) return false;
    // Solo letras (incluyendo acentos y ñ), espacios, guiones y apóstrofes
    // Mínimo 2 caracteres, máximo 200
    const nombreRegex = /^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s\-']{2,200}$/;
    return nombreRegex.test(nombre.trim());
}

/**
 * Validar email
 */
function validarEmail(email) {
    if (!email) return true; // Email es opcional
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email.trim());
}

/**
 * Validar teléfono (formato chileno o internacional)
 */
function validarTelefono(telefono) {
    if (!telefono) return true; // Teléfono es opcional
    // Permitir formato: +56 9 1234 5678, 912345678, +56912345678, etc.
    const telefonoRegex = /^[\+]?[0-9\s\-\(\)]{8,20}$/;
    return telefonoRegex.test(telefono.trim());
}

/**
 * Validar fecha de nacimiento
 */
function validarFechaNacimiento(fecha) {
    if (!fecha) return true; // Fecha es opcional
    // Verificar formato dd/mm/yyyy
    if (!/^\d{2}\/\d{2}\/\d{4}$/.test(fecha)) return false;
    
    const parts = fecha.split('/');
    const dia = parseInt(parts[0]);
    const mes = parseInt(parts[1]);
    const anio = parseInt(parts[2]);
    
    // Verificar que la fecha sea válida
    const fechaObj = new Date(anio, mes - 1, dia);
    if (fechaObj.getDate() !== dia || fechaObj.getMonth() !== mes - 1 || fechaObj.getFullYear() !== anio) {
        return false;
    }
    
    // Verificar que no sea futura
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    return fechaObj <= hoy;
}

/**
 * Agregar validaciones en tiempo real a los campos del viajero
 */
function agregarValidacionesViajero(container, itemId) {
    // Validar nombre
    container.querySelectorAll('.viajero-nombre').forEach(input => {
        input.addEventListener('blur', function() {
            const viajeroNum = this.getAttribute('data-viajero');
            const errorDiv = document.querySelector(`.viajero-nombre-error[data-item-id="${itemId}"][data-viajero="${viajeroNum}"]`);
            if (!validarNombre(this.value)) {
                this.classList.add('is-invalid');
                if (errorDiv) errorDiv.style.display = 'block';
            } else {
                this.classList.remove('is-invalid');
                if (errorDiv) errorDiv.style.display = 'none';
            }
        });
    });
    
    // Validar RUT
    container.querySelectorAll('.viajero-rut').forEach(input => {
        input.addEventListener('blur', function() {
            const viajeroNum = this.getAttribute('data-viajero');
            const errorDiv = document.querySelector(`.viajero-rut-error[data-item-id="${itemId}"][data-viajero="${viajeroNum}"]`);
            if (!validarRutChileno(this.value)) {
                this.classList.add('is-invalid');
                if (errorDiv) errorDiv.style.display = 'block';
            } else {
                this.classList.remove('is-invalid');
                if (errorDiv) errorDiv.style.display = 'none';
            }
        });
    });
    
    // Validar email
    container.querySelectorAll('.viajero-email').forEach(input => {
        input.addEventListener('blur', function() {
            const viajeroNum = this.getAttribute('data-viajero');
            const errorDiv = document.querySelector(`.viajero-email-error[data-item-id="${itemId}"][data-viajero="${viajeroNum}"]`);
            if (this.value && !validarEmail(this.value)) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                if (errorDiv) errorDiv.style.display = 'block';
            } else {
                this.classList.remove('is-invalid');
                if (this.value) this.classList.add('is-valid');
                if (errorDiv) errorDiv.style.display = 'none';
            }
        });
    });
    
    // Validar teléfono (obligatorio)
    container.querySelectorAll('.viajero-telefono').forEach(input => {
        input.addEventListener('blur', function() {
            const viajeroNum = this.getAttribute('data-viajero');
            const errorDiv = document.querySelector(`.viajero-telefono-error[data-item-id="${itemId}"][data-viajero="${viajeroNum}"]`);
            if (!this.value) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                if (errorDiv) {
                    errorDiv.textContent = 'El teléfono es requerido';
                    errorDiv.style.display = 'block';
                }
            } else if (!validarTelefono(this.value)) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                if (errorDiv) {
                    errorDiv.textContent = 'El teléfono no tiene un formato válido';
                    errorDiv.style.display = 'block';
                }
            } else {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                if (errorDiv) errorDiv.style.display = 'none';
            }
        });
    });
    
    // Validar fecha
    container.querySelectorAll('.viajero-fecha').forEach(input => {
        input.addEventListener('blur', function() {
            const viajeroNum = this.getAttribute('data-viajero');
            if (this.value && !validarFechaNacimiento(this.value)) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                mostrarToast('La fecha de nacimiento no es válida o es futura', 'error', 'Error');
            } else {
                this.classList.remove('is-invalid');
                if (this.value) this.classList.add('is-valid');
            }
        });
    });
}

/**
 * Usar datos del usuario logueado para rellenar el formulario del viajero
 * Hacerla global para que pueda ser llamada desde onclick
 */
window.usarDatosUsuario = function(paqueteId, itemId, viajeroNum) {
    if (!usuarioData) {
        mostrarToast('No hay datos de usuario disponibles', 'error', 'Error');
        return;
    }
    
    // Obtener todos los campos del formulario del viajero
    const nombreInput = document.querySelector(`.viajero-nombre[data-item-id="${itemId}"][data-viajero="${viajeroNum}"]`);
    const rutInput = document.querySelector(`.viajero-rut[data-item-id="${itemId}"][data-viajero="${viajeroNum}"]`);
    const emailInput = document.querySelector(`.viajero-email[data-item-id="${itemId}"][data-viajero="${viajeroNum}"]`);
    const telefonoInput = document.querySelector(`.viajero-telefono[data-item-id="${itemId}"][data-viajero="${viajeroNum}"]`);
    const fechaInput = document.querySelector(`.viajero-fecha[data-item-id="${itemId}"][data-viajero="${viajeroNum}"]`);
    
    // Rellenar los campos con los datos del usuario
    if (nombreInput) nombreInput.value = usuarioData.nombre_completo || '';
    if (rutInput) rutInput.value = usuarioData.rut || '';
    if (emailInput) emailInput.value = usuarioData.email || '';
    if (telefonoInput && usuarioData.telefono) telefonoInput.value = usuarioData.telefono || '';
    if (fechaInput && usuarioData.fecha_nacimiento) {
        fechaInput.value = usuarioData.fecha_nacimiento;
        // Si está usando Flatpickr, actualizar el calendario
        if (fechaInput._flatpickr) {
            fechaInput._flatpickr.setDate(usuarioData.fecha_nacimiento, false);
        }
    }
    
    mostrarToast('Datos personales cargados correctamente', 'success', '¡Listo!');
};

/**
 * Actualizar cantidad en el carrito
 */
async function actualizarCantidadCarrito(tipo, id, nuevaCantidad) {
    if (nuevaCantidad < 1) {
        mostrarToast('La cantidad debe ser al menos 1', 'error', 'Error');
        return;
    }
    
    try {
        const response = await fetch('/api/carrito/actualizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo, id, cantidad: nuevaCantidad })
        });
        const data = await response.json();
        
        if (response.ok) {
            cargarCarrito();
            actualizarContadorCarrito();
        } else {
            mostrarToast(data.error || 'Error al actualizar cantidad', 'error', 'Error');
        }
    } catch (error) {
        mostrarToast('Error de conexión', 'error', 'Error');
    }
}

/**
 * Eliminar item del carrito
 */
async function eliminarDelCarrito(tipo, id, timestamp, carrito_index) {
    const result = await Swal.fire({
        title: '¿Eliminar del carrito?',
        text: '¿Estás seguro de que deseas eliminar este item?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    });
    
    if (result.isConfirmed) {
        try {
            const body = { tipo, id };
            if (timestamp !== null && timestamp !== undefined) {
                body.timestamp = timestamp;
            }
            if (carrito_index !== null && carrito_index !== undefined) {
                body.carrito_index = carrito_index;
            }
            const response = await fetch('/api/carrito/eliminar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await response.json();
            
            if (response.ok) {
                Swal.fire('Eliminado', data.message, 'success');
                cargarCarrito();
            } else {
                Swal.fire('Error', data.error || 'Error al eliminar', 'error');
            }
        } catch (error) {
            Swal.fire('Error', 'Error de conexión', 'error');
        }
    }
}

/**
 * Limpiar todo el carrito
 */
async function limpiarCarrito() {
    const result = await Swal.fire({
        title: '¿Limpiar carrito?',
        text: '¿Estás seguro de que deseas eliminar todos los items?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, limpiar',
        cancelButtonText: 'Cancelar'
    });
    
    if (result.isConfirmed) {
        try {
            const response = await fetch('/api/carrito/limpiar', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (response.ok) {
                Swal.fire('Carrito limpiado', data.message, 'success');
                cargarCarrito();
            } else {
                Swal.fire('Error', data.error || 'Error al limpiar', 'error');
            }
        } catch (error) {
            Swal.fire('Error', 'Error de conexión', 'error');
        }
    }
}

/**
 * Proceder con la reserva
 */
function procederReserva() {
    if (!tieneUsuario) {
        Swal.fire({
            title: 'Iniciar Sesión Requerido',
            text: 'Debes iniciar sesión para realizar reservas',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Iniciar Sesión',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = '/auth/login';
            }
        });
        return;
    }
    
    const paquetesEnCarrito = carritoItems.filter(item => item.tipo === 'paquete');
    
    if (paquetesEnCarrito.length === 0) {
        mostrarToast('No hay paquetes en el carrito para reservar', 'error', 'Info');
        return;
    }
    
    const datosPorPaquete = [];
    let hayErrores = false;
    
    // Iterar sobre cada item del carrito individualmente (cada uno tiene su propio itemId único)
    paquetesEnCarrito.forEach((item, index) => {
        const paqueteId = item.id;
        const itemId = String(item.timestamp || item.carrito_index || index);
        
        const numeroPasajerosInput = document.querySelector(`.numero-pasajeros-paquete[data-item-id="${itemId}"]`);
        if (!numeroPasajerosInput) {
            mostrarToast(`Error: No se encontró el campo de número de pasajeros para ${item.nombre}`, 'error', 'Error');
            hayErrores = true;
            return;
        }
        
        const numeroPasajeros = parseInt(numeroPasajerosInput.value) || 1;
        
        if (item.disponibles < numeroPasajeros) {
            mostrarToast(`No hay suficientes cupos en ${item.nombre}. Disponibles: ${item.disponibles}, Solicitados: ${numeroPasajeros}`, 'error', 'Error');
            hayErrores = true;
            return;
        }
        
        const viajeros = [];
        for (let i = 1; i <= numeroPasajeros; i++) {
            const nombreInput = document.querySelector(`.viajero-nombre[data-item-id="${itemId}"][data-viajero="${i}"]`);
            const rutInput = document.querySelector(`.viajero-rut[data-item-id="${itemId}"][data-viajero="${i}"]`);
            const fechaInput = document.querySelector(`.viajero-fecha[data-item-id="${itemId}"][data-viajero="${i}"]`);
            const telefonoInput = document.querySelector(`.viajero-telefono[data-item-id="${itemId}"][data-viajero="${i}"]`);
            const emailInput = document.querySelector(`.viajero-email[data-item-id="${itemId}"][data-viajero="${i}"]`);
            
            const nombre = nombreInput?.value?.trim() || '';
            const rut = rutInput?.value?.trim() || '';
            let fecha = fechaInput?.value || null;
            const telefono = telefonoInput?.value?.trim() || '';
            const email = emailInput?.value?.trim() || '';
            
            // Validar nombre
            if (!nombre || !validarNombre(nombre)) {
                mostrarToast(`El nombre del viajero ${i} no es válido. Solo se permiten letras y espacios.`, 'error', 'Error');
                if (nombreInput) nombreInput.classList.add('is-invalid');
                hayErrores = true;
                return;
            }
            
            // Validar RUT
            if (!rut || !validarRutChileno(rut)) {
                mostrarToast(`El RUT del viajero ${i} no es válido. Verifica el formato y el dígito verificador.`, 'error', 'Error');
                if (rutInput) rutInput.classList.add('is-invalid');
                hayErrores = true;
                return;
            }
            
            // Validar email si está presente
            if (email && !validarEmail(email)) {
                mostrarToast(`El email del viajero ${i} no tiene un formato válido.`, 'error', 'Error');
                if (emailInput) emailInput.classList.add('is-invalid');
                hayErrores = true;
                return;
            }
            
            // Validar teléfono (obligatorio)
            if (!telefono) {
                mostrarToast(`El teléfono del viajero ${i} es requerido.`, 'error', 'Error');
                if (telefonoInput) telefonoInput.classList.add('is-invalid');
                hayErrores = true;
                return;
            }
            if (!validarTelefono(telefono)) {
                mostrarToast(`El teléfono del viajero ${i} no tiene un formato válido.`, 'error', 'Error');
                if (telefonoInput) telefonoInput.classList.add('is-invalid');
                hayErrores = true;
                return;
            }
            
            // Validar fecha si está presente
            if (fecha && !validarFechaNacimiento(fecha)) {
                mostrarToast(`La fecha de nacimiento del viajero ${i} no es válida o es futura.`, 'error', 'Error');
                if (fechaInput) fechaInput.classList.add('is-invalid');
                hayErrores = true;
                return;
            }
            
            if (fecha && fecha.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
                const parts = fecha.split('/');
                fecha = `${parts[2]}-${parts[1]}-${parts[0]}`;
            }
            
            viajeros.push({
                nombre_completo: nombre,
                rut: rut,
                fecha_nacimiento: fecha || null,
                telefono: telefono || null,
                email: email || null
            });
        }
        
        if (viajeros.length < numeroPasajeros) {
            mostrarToast(`Debes completar los datos de los ${numeroPasajeros} viajero${numeroPasajeros > 1 ? 's' : ''} para ${item.nombre}`, 'error', 'Error');
            hayErrores = true;
            return;
        }
        
        datosPorPaquete.push({
            paquete_id: paqueteId,
            paquete_nombre: item.nombre,
            numero_pasajeros: numeroPasajeros,
            viajeros: viajeros
        });
    });
    
    if (hayErrores) {
        return;
    }
    
    // Obtener teléfono del viajero titular (primer viajero del primer paquete)
    // Como el teléfono es obligatorio, siempre debería estar disponible
    let telefonoContacto = null;
    if (datosPorPaquete.length > 0 && datosPorPaquete[0].viajeros.length > 0) {
        // Usar el teléfono del primer viajero (titular)
        telefonoContacto = datosPorPaquete[0].viajeros[0].telefono;
    }
    
    // Si por alguna razón no hay teléfono, usar el del usuario logueado como fallback
    if (!telefonoContacto && usuarioData?.telefono) {
        telefonoContacto = usuarioData.telefono;
    }
    
    // Si aún no hay teléfono, mostrar error (no debería pasar si las validaciones funcionan)
    if (!telefonoContacto) {
        mostrarToast('El teléfono del viajero titular es requerido. Por favor, completa los datos del viajero.', 'error', 'Error');
        return;
    }
    
    // Proceder directamente con la reserva (sin modal)
    crearReservas(datosPorPaquete, telefonoContacto, null);
}

/**
 * Crear reservas
 */
async function crearReservas(datosPorPaquete, telefonoContacto, comentarios) {
    try {
        for (const datos of datosPorPaquete) {
            const response = await fetch('/api/reservas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    paquete_id: datos.paquete_id,
                    estado: 'confirmada',
                    numero_pasajeros: datos.numero_pasajeros,
                    telefono_contacto: telefonoContacto,
                    comentarios: comentarios,
                    viajeros: datos.viajeros
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Error al crear reserva');
            }
        }
        
        await fetch('/api/carrito/limpiar', { method: 'POST' });
        
        Swal.fire({
            title: '¡Reservas Confirmadas!',
            text: 'Tus reservas se han creado exitosamente',
            icon: 'success',
            confirmButtonText: 'Ver Mis Reservas'
        }).then(() => {
            window.location.href = '/mis-reservas';
        });
    } catch (error) {
        Swal.fire('Error', error.message || 'Error al crear las reservas', 'error');
    }
}

/**
 * Actualizar contador del carrito
 */
function actualizarContadorCarrito() {
    if (typeof actualizarContadorCarritoGlobal === 'function') {
        actualizarContadorCarritoGlobal();
    }
}

