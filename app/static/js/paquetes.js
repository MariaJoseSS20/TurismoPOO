/**
 * JavaScript para la página de paquetes
 * Maneja la carga, filtrado y gestión de paquetes turísticos
 */

// Variables globales
let esAdmin = false;
let todosPaquetes = [];
let destinosData = [];
let destinosDataEditar = [];

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    // Obtener si es admin desde data attribute
    const paquetesPage = document.getElementById('paquetes-page');
    if (paquetesPage) {
        esAdmin = paquetesPage.dataset.esAdmin === 'true';
    }
    
    // Inicializar página
    init();
});

/**
 * Inicializar la página de paquetes
 */
function init() {
    if (typeof initPriceSlider === 'function') {
        initPriceSlider('price-range-paquetes', filtrarPaquetes);
    }
    if (typeof setupBusquedaTiempoReal === 'function') {
        setupBusquedaTiempoReal(filtrarPaquetes);
    }
    cargarPaquetes();
    
    // Configurar modales de admin si es admin
    if (esAdmin) {
        setupAdminModals();
    }
}

/**
 * Cargar paquetes desde la API
 */
async function cargarPaquetes() {
    try {
        const response = await fetch('/api/paquetes');
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        const paquetes = await response.json();
        
        if (paquetes.error) {
            throw new Error(paquetes.error);
        }
        
        todosPaquetes = paquetes;
        filtrarPaquetes();
    } catch (error) {
        console.error('Error al cargar paquetes:', error);
        const container = document.getElementById('paquetes-container');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i> Error: ${error.message}
                </div>
            `;
        }
    }
}

/**
 * Filtrar paquetes según los criterios de búsqueda
 */
function filtrarPaquetes() {
    if (!todosPaquetes || todosPaquetes.length === 0) {
        const container = document.getElementById('paquetes-container');
        if (container) {
            container.innerHTML = '<div class="card"><div class="card-body p-5"><p class="text-muted mb-0">No hay paquetes disponibles</p></div></div>';
        }
        return;
    }
    
    const origenEl = document.getElementById('origen');
    const destinoEl = document.getElementById('destino');
    const fechaInicioEl = document.getElementById('fecha_inicio');
    const fechaFinEl = document.getElementById('fecha_fin');
    const precioMinSlider = document.getElementById('precio_min_slider');
    const precioMaxSlider = document.getElementById('precio_max_slider');
    
    const origen = origenEl ? origenEl.value.toLowerCase() : '';
    const destino = destinoEl ? destinoEl.value.toLowerCase() : '';
    const fechaInicio = fechaInicioEl ? fechaInicioEl.value : '';
    const fechaFin = fechaFinEl ? fechaFinEl.value : '';
    const precioMin = precioMinSlider ? parseFloat(precioMinSlider.value) : 0;
    const precioMax = precioMaxSlider ? parseFloat(precioMaxSlider.value) : 50000;
    
    const paquetesFiltrados = todosPaquetes.filter(p => {
        if (origen && (!p.origen || !p.origen.toLowerCase().includes(origen))) return false;
        if (destino) {
            const destinosStr = p.destinos.map(d => d.nombre).join(' ').toLowerCase();
            if (!destinosStr.includes(destino)) return false;
        }
        if (fechaInicio) {
            const fechaInicioPaquete = new Date(p.fecha_inicio);
            const fechaInicioFiltro = new Date(fechaInicio);
            if (fechaInicioPaquete < fechaInicioFiltro) return false;
        }
        if (fechaFin) {
            const fechaFinPaquete = new Date(p.fecha_fin);
            const fechaFinFiltro = new Date(fechaFin);
            if (fechaFinPaquete > fechaFinFiltro) return false;
        }
        if (p.precio_total < precioMin || p.precio_total > precioMax) return false;
        return true;
    });
    
    const container = document.getElementById('paquetes-container');
    if (!container) return;
    
    if (!paquetesFiltrados.length) {
        container.innerHTML = '<div class="card"><div class="card-body p-5"><p class="text-muted mb-0">No se encontraron paquetes con los filtros aplicados</p></div></div>';
        return;
    }
    
    let cardsHTML = '<div class="row g-4">';
    paquetesFiltrados.forEach(paquete => {
        const fechaInicio = new Date(paquete.fecha_inicio).toLocaleDateString('es-ES');
        const fechaFin = new Date(paquete.fecha_fin).toLocaleDateString('es-ES');
        const dias = Math.ceil((new Date(paquete.fecha_fin) - new Date(paquete.fecha_inicio)) / (1000 * 60 * 60 * 24));
        const destinos = paquete.destinos && paquete.destinos.length > 0 ? paquete.destinos.map(d => d.nombre).join(', ') : 'Sin destinos';
        
        cardsHTML += `
            <div class="col-md-6 col-lg-4 col-xl-3 mb-4">
                <div class="card shadow-sm h-100 border-0 rounded-3">
                    <div class="card-body p-4 d-flex flex-column">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h5 class="card-title text-dark fw-bold mb-0">${paquete.nombre}</h5>
                            <span class="badge ${paquete.disponibles > 0 ? 'badge-cupos' : 'bg-danger'} ms-2">
                                ${paquete.disponibles > 0 ? `${paquete.disponibles} cupos` : 'Agotado'}
                            </span>
                        </div>
                        
                        <div class="mb-3 flex-grow-1">
                            <div class="d-flex align-items-center justify-content-between mb-3 p-3 rounded bg-light border">
                                <div class="d-flex align-items-center flex-fill">
                                    <div>
                                        <small class="text-muted d-block">Origen</small>
                                        <strong>${paquete.origen || 'N/A'}</strong>
                                    </div>
                                </div>
                                <i class="bi bi-arrow-right text-primary mx-3"></i>
                                <div class="d-flex align-items-center flex-fill">
                                    <i class="bi bi-geo-alt-fill text-danger me-2"></i>
                                    <div>
                                        <small class="text-muted d-block">Destinos</small>
                                        <strong>${destinos}</strong>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="d-flex align-items-center justify-content-between p-2 rounded bg-light mb-3">
                                <div class="d-flex align-items-center">
                                    <i class="bi bi-clock text-primary me-2"></i>
                                    <div>
                                        <small class="text-muted d-block">Duración</small>
                                        <strong class="small">${dias} días</strong>
                                    </div>
                                </div>
                                <div class="d-flex align-items-center">
                                    <i class="bi bi-calendar3 text-primary me-2"></i>
                                    <div>
                                        <small class="text-muted d-block">Fechas</small>
                                        <strong class="small">${fechaInicio} - ${fechaFin}</strong>
                                    </div>
                                </div>
                            </div>
                            
                            ${paquete.destinos && paquete.destinos.length > 0 ? `
                                <div class="mb-3">
                                    ${paquete.destinos.map(destino => {
                                        const actividadesArray = Array.isArray(destino.actividades) ? destino.actividades : (destino.actividades ? destino.actividades.split(',').map(a => a.trim()) : []);
                                        const descripcion = destino.descripcion || '';
                                        return `
                                            <div class="mb-3">
                                                ${actividadesArray.length > 0 ? `
                                                    <div class="mb-2">
                                                        <small class="text-muted d-block mb-2 text-center">
                                                            <i class="bi bi-list-check text-warning me-1"></i> Actividades
                                                        </small>
                                                        <div class="d-flex flex-wrap gap-1 justify-content-center">
                                                            ${actividadesArray.slice(0, 3).map(act => `<span class="badge bg-purple-pastel text-purple-dark small">${act}</span>`).join('')}
                                                            ${actividadesArray.length > 3 ? `<span class="badge bg-secondary-subtle text-secondary small">+${actividadesArray.length - 3}</span>` : ''}
                                                        </div>
                                                    </div>
                                                ` : ''}
                                                
                                                ${descripcion ? `
                                                    <div class="mb-0 text-center">
                                                        <p class="text-muted small mb-0 lh-sm">${descripcion}</p>
                                                    </div>
                                                ` : ''}
                                            </div>
                                        `;
                                    }).join('')}
                                </div>
                            ` : ''}
                        </div>
                        
                        <div class="mt-auto border-top pt-3">
                            <div class="text-center mb-3">
                                <small class="text-muted d-block mb-1">Precio Total</small>
                                <h3 class="text-primary fw-bold mb-0">${typeof formatCLP !== 'undefined' ? formatCLP(paquete.precio_total) : '$' + paquete.precio_total.toLocaleString('es-CL')}</h3>
                            </div>
                            ${esAdmin ? `
                                <div class="d-flex gap-2 mb-3">
                                    <button class="btn btn-primary flex-fill" onclick="editarPaquete(${paquete.id})">
                                        <i class="bi bi-pencil me-2"></i> Editar
                                    </button>
                                    <button class="btn btn-danger flex-fill" onclick="eliminarPaquete(${paquete.id}, '${paquete.nombre.replace(/'/g, "\\'")}')">
                                        <i class="bi bi-trash me-2"></i> Eliminar
                                    </button>
                                </div>
                            ` : ''}
                            ${!esAdmin && paquete.disponibles > 0 ? 
                                `<div class="mb-3">
                                    <label class="form-label small fw-bold text-muted mb-2">Cantidad</label>
                                    <div class="d-flex align-items-center justify-content-center gap-2">
                                        <button type="button" class="btn btn-outline-primary btn-sm cantidad-btn" 
                                                onclick="cambiarCantidad('paquete-${paquete.id}', -1, ${paquete.disponibles})" 
                                                id="btn-restar-${paquete.id}"
                                                disabled>
                                            <i class="bi bi-dash-lg"></i>
                                        </button>
                                        <input type="number" 
                                               class="form-control text-center cantidad-input" 
                                               id="cantidad-paquete-${paquete.id}" 
                                               value="1" 
                                               min="1" 
                                               max="${paquete.disponibles}" 
                                               readonly
                                               style="max-width: 80px; -webkit-appearance: none !important; -moz-appearance: textfield !important; appearance: none !important;">
                                        <button type="button" class="btn btn-outline-primary btn-sm cantidad-btn" 
                                                onclick="cambiarCantidad('paquete-${paquete.id}', 1, ${paquete.disponibles})" 
                                                id="btn-sumar-${paquete.id}"
                                                ${paquete.disponibles <= 1 ? 'disabled' : ''}>
                                            <i class="bi bi-plus-lg"></i>
                                        </button>
                                    </div>
                                </div>
                                <button class="btn btn-success w-100" onclick="agregarAlCarritoConCantidad('paquete', ${paquete.id})">
                                    <i class="bi bi-cart-plus-fill me-2"></i> Agregar al Carrito
                                </button>` : 
                                !esAdmin && paquete.disponibles === 0 ?
                                '<button class="btn btn-secondary w-100" disabled>Agotado</button>' : ''
                            }
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    cardsHTML += '</div>';
    container.innerHTML = cardsHTML;
}

/**
 * Cambiar cantidad de un paquete
 */
function cambiarCantidad(prefijo, cambio, maxDisponibles) {
    const inputId = `cantidad-${prefijo}`;
    const input = document.getElementById(inputId);
    if (!input) {
        console.error('No se encontró el input:', inputId);
        return;
    }
    
    let cantidadActual = parseInt(input.value) || 1;
    let nuevaCantidad = cantidadActual + cambio;
    
    if (nuevaCantidad < 1) nuevaCantidad = 1;
    if (nuevaCantidad > maxDisponibles) nuevaCantidad = maxDisponibles;
    
    input.value = nuevaCantidad;
    
    const paqueteId = prefijo.replace('paquete-', '');
    const btnRestar = document.getElementById(`btn-restar-${paqueteId}`);
    const btnSumar = document.getElementById(`btn-sumar-${paqueteId}`);
    
    if (btnRestar) btnRestar.disabled = nuevaCantidad <= 1;
    if (btnSumar) btnSumar.disabled = nuevaCantidad >= maxDisponibles;
}

/**
 * Agregar paquete al carrito con cantidad
 */
async function agregarAlCarritoConCantidad(tipo, id) {
    try {
        const inputId = `cantidad-${tipo}-${id}`;
        const cantidadInput = document.getElementById(inputId);
        
        if (!cantidadInput) {
            console.error('No se encontró el input de cantidad:', inputId);
            if (typeof mostrarToast === 'function') {
                mostrarToast('Error: No se pudo obtener la cantidad', 'error', 'Error');
            }
            return;
        }
        
        const cantidad = parseInt(cantidadInput.value) || 1;
        
        if (cantidad < 1) {
            if (typeof mostrarToast === 'function') {
                mostrarToast('La cantidad debe ser al menos 1', 'error', 'Error');
            }
            return;
        }
        
        const response = await fetch('/api/carrito/agregar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo, id, cantidad })
        });
        const data = await response.json();
        
        if (response.ok) {
            if (typeof mostrarToast === 'function') {
                mostrarToast(data.message, 'success', '¡Agregado!');
            }
            
            if (data.cantidad !== undefined) {
                const contador = document.getElementById('carrito-contador');
                if (contador) {
                    if (data.cantidad > 0) {
                        contador.textContent = data.cantidad;
                        contador.style.display = 'inline-block';
                    } else {
                        contador.style.display = 'none';
                    }
                }
            } else if (typeof actualizarContadorCarrito === 'function') {
                actualizarContadorCarrito();
            }
            
            if (cantidadInput) {
                cantidadInput.value = 1;
                const paqueteId = id;
                const btnRestar = document.getElementById(`btn-restar-${paqueteId}`);
                const btnSumar = document.getElementById(`btn-sumar-${paqueteId}`);
                if (btnRestar) btnRestar.disabled = true;
                if (btnSumar) {
                    const paquete = todosPaquetes.find(p => p.id === id);
                    if (paquete) {
                        btnSumar.disabled = paquete.disponibles <= 1;
                    }
                }
            }
        } else {
            if (typeof mostrarToast === 'function') {
                mostrarToast(data.error || 'Error al agregar al carrito', 'error', 'Error');
            }
        }
    } catch (error) {
        if (typeof mostrarToast === 'function') {
            mostrarToast('Error de conexión', 'error', 'Error');
        }
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

// ========== FUNCIONES DE ADMINISTRACIÓN ==========

/**
 * Configurar modales de administración
 */
function setupAdminModals() {
    const modalCrear = document.getElementById('modalCrearPaquete');
    if (modalCrear) {
        modalCrear.addEventListener('show.bs.modal', cargarDestinosModal);
    }
    
    const fechaInicio = document.getElementById('modal_fecha_inicio');
    const fechaFin = document.getElementById('modal_fecha_fin');
    if (fechaInicio) fechaInicio.addEventListener('change', calcularPrecioTotal);
    if (fechaFin) fechaFin.addEventListener('change', calcularPrecioTotal);
    
    const formCrear = document.getElementById('formCrearPaquete');
    if (formCrear) {
        formCrear.addEventListener('submit', handleCrearPaquete);
    }
    
    const formEditar = document.getElementById('formEditarPaquete');
    if (formEditar) {
        formEditar.addEventListener('submit', handleEditarPaquete);
    }
}

/**
 * Determinar si una fecha está en temporada alta
 */
function esTemporadaAlta(fecha) {
    const mes = fecha.getMonth() + 1;
    return mes >= 10 || mes <= 4;
}

/**
 * Calcular precio total (modal crear)
 */
function calcularPrecioTotal() {
    const fechaInicio = document.getElementById('modal_fecha_inicio')?.value;
    const fechaFin = document.getElementById('modal_fecha_fin')?.value;
    const destinoSeleccionado = document.querySelector('#destinos-container input[type="radio"]:checked');
    const precioInput = document.getElementById('modal_precio_total');
    
    if (!fechaInicio || !fechaFin || !destinoSeleccionado || !precioInput) {
        if (precioInput) precioInput.value = '';
        return;
    }
    
    const fechaInicioDate = new Date(fechaInicio);
    const fechaFinDate = new Date(fechaFin);
    
    if (fechaFinDate < fechaInicioDate) {
        precioInput.value = '';
        return;
    }
    
    const diffTime = Math.abs(fechaFinDate - fechaInicioDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    
    const destinoId = parseInt(destinoSeleccionado.value);
    const destino = destinosData.find(d => d.id === destinoId);
    
    if (!destino) {
        precioInput.value = '';
        return;
    }
    
    const precioBase = destino.costo_base * diffDays;
    const temporadaAlta = esTemporadaAlta(fechaInicioDate);
    const multiplicador = temporadaAlta ? 1.2 : 0.8;
    const precioTotal = precioBase * multiplicador;
    
    precioInput.value = precioTotal.toFixed(2);
}

/**
 * Calcular precio total (modal editar)
 */
function calcularPrecioTotalEditar() {
    const fechaInicio = document.getElementById('modal_editar_fecha_inicio')?.value;
    const fechaFin = document.getElementById('modal_editar_fecha_fin')?.value;
    const destinoSeleccionado = document.querySelector('#destinos-container-editar input[type="radio"]:checked');
    const precioInput = document.getElementById('modal_editar_precio_total');
    
    if (!fechaInicio || !fechaFin || !destinoSeleccionado || !precioInput) {
        if (precioInput) precioInput.value = '';
        return;
    }
    
    const fechaInicioDate = new Date(fechaInicio);
    const fechaFinDate = new Date(fechaFin);
    
    if (fechaFinDate < fechaInicioDate) {
        precioInput.value = '';
        return;
    }
    
    const diffTime = Math.abs(fechaFinDate - fechaInicioDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    
    const destinoId = parseInt(destinoSeleccionado.value);
    const destino = destinosDataEditar.find(d => d.id === destinoId);
    
    if (!destino) {
        precioInput.value = '';
        return;
    }
    
    const precioBase = destino.costo_base * diffDays;
    const temporadaAlta = esTemporadaAlta(fechaInicioDate);
    const multiplicador = temporadaAlta ? 1.2 : 0.8;
    const precioTotal = precioBase * multiplicador;
    
    precioInput.value = precioTotal.toFixed(2);
}

/**
 * Cargar destinos en el modal de crear
 */
async function cargarDestinosModal() {
    const container = document.getElementById('destinos-container');
    if (!container) return;
    
    try {
        const response = await fetch('/admin/api/destinos');
        if (!response.ok) throw new Error('Error al cargar destinos');
        destinosData = await response.json();
        
        if (destinosData.length === 0) {
            container.innerHTML = '<p class="text-muted mb-0">No hay destinos disponibles. Crea destinos primero.</p>';
            return;
        }
        
        container.innerHTML = '';
        destinosData.forEach(destino => {
            container.innerHTML += `
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="destino" 
                           value="${destino.id}" id="modal_destino_${destino.id}" required>
                    <label class="form-check-label" for="modal_destino_${destino.id}">
                        ${destino.nombre} - ${typeof formatCLP !== 'undefined' ? formatCLP(destino.costo_base) : '$' + destino.costo_base.toLocaleString('es-CL')}
                    </label>
                </div>
            `;
        });
        
        container.querySelectorAll('input[type="radio"]').forEach(radio => {
            radio.addEventListener('change', calcularPrecioTotal);
        });
        
        const precioInput = document.getElementById('modal_precio_total');
        if (precioInput) precioInput.value = '';
    } catch (error) {
        container.innerHTML = '<p class="text-danger mb-0">Error al cargar destinos</p>';
    }
}

/**
 * Manejar creación de paquete
 */
async function handleCrearPaquete(e) {
    e.preventDefault();
    
    const destinoSeleccionado = document.querySelector('#destinos-container input[type="radio"]:checked');
    if (!destinoSeleccionado) {
        Swal.fire('Destino requerido', 'Debes seleccionar un destino', 'warning');
        return;
    }
    if (!this.checkValidity()) return this.reportValidity();
    
    const formData = new FormData(this);
    const data = {
        nombre: formData.get('nombre'),
        origen: formData.get('origen'),
        fecha_inicio: formData.get('fecha_inicio'),
        fecha_fin: formData.get('fecha_fin'),
        precio_total: formData.get('precio_total'),
        disponibles: formData.get('disponibles'),
        destinos: [parseInt(destinoSeleccionado.value)]
    };
    
    try {
        const response = await fetch('/admin/paquetes/crear/api', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        if (response.ok) {
            Swal.fire('¡Éxito!', result.message, 'success').then(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalCrearPaquete'));
                if (modal) modal.hide();
                this.reset();
                cargarPaquetes();
            });
        } else {
            Swal.fire('Error', result.error || 'Error al crear el paquete', 'error');
        }
    } catch (error) {
        Swal.fire('Error', 'Error de conexión', 'error');
    }
}

/**
 * Editar paquete
 */
async function editarPaquete(paqueteId) {
    try {
        const response = await fetch(`/api/paquetes/${paqueteId}`);
        if (!response.ok) throw new Error('Error al cargar el paquete');
        const paquete = await response.json();
        
        const destinosResponse = await fetch('/admin/api/destinos');
        if (!destinosResponse.ok) throw new Error('Error al cargar destinos');
        const destinos = await destinosResponse.json();
        
        destinosDataEditar = destinos;
        
        document.getElementById('modal_editar_nombre').value = paquete.nombre || '';
        document.getElementById('modal_editar_origen').value = 'Punta Arenas';
        document.getElementById('modal_editar_fecha_inicio').value = paquete.fecha_inicio || '';
        document.getElementById('modal_editar_fecha_fin').value = paquete.fecha_fin || '';
        document.getElementById('modal_editar_disponibles').value = paquete.disponibles || '';
        
        const destinosContainer = document.getElementById('destinos-container-editar');
        destinosContainer.innerHTML = '';
        destinos.forEach(destino => {
            const isSelected = paquete.destinos.length > 0 && paquete.destinos[0].id === destino.id;
            destinosContainer.innerHTML += `
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="destino" 
                           value="${destino.id}" id="modal_editar_destino_${destino.id}"
                           ${isSelected ? 'checked' : ''} required>
                    <label class="form-check-label" for="modal_editar_destino_${destino.id}">
                        ${destino.nombre} - ${typeof formatCLP !== 'undefined' ? formatCLP(destino.costo_base) : '$' + destino.costo_base.toLocaleString('es-CL')}
                    </label>
                </div>
            `;
        });
        
        destinosContainer.querySelectorAll('input[type="radio"]').forEach(radio => {
            radio.addEventListener('change', calcularPrecioTotalEditar);
        });
        
        const fechaInicioInput = document.getElementById('modal_editar_fecha_inicio');
        const fechaFinInput = document.getElementById('modal_editar_fecha_fin');
        
        if (fechaInicioInput && fechaFinInput) {
            fechaInicioInput.replaceWith(fechaInicioInput.cloneNode(true));
            fechaFinInput.replaceWith(fechaFinInput.cloneNode(true));
            
            document.getElementById('modal_editar_fecha_inicio').addEventListener('change', calcularPrecioTotalEditar);
            document.getElementById('modal_editar_fecha_fin').addEventListener('change', calcularPrecioTotalEditar);
        }
        
        calcularPrecioTotalEditar();
        
        const formEditar = document.getElementById('formEditarPaquete');
        if (formEditar) {
            formEditar.dataset.paqueteId = paqueteId;
        }
        
        if (typeof flatpickr !== 'undefined') {
            flatpickr('#modal_editar_fecha_inicio', {
                locale: 'es',
                dateFormat: 'Y-m-d',
                minDate: 'today',
                allowInput: false,
                clickOpens: true,
                theme: 'light',
                appendTo: document.body,
                monthSelectorType: 'static',
                animate: true
            });
            flatpickr('#modal_editar_fecha_fin', {
                locale: 'es',
                dateFormat: 'Y-m-d',
                minDate: 'today',
                allowInput: false,
                clickOpens: true,
                theme: 'light',
                appendTo: document.body,
                monthSelectorType: 'static',
                animate: true
            });
        }
        
        new bootstrap.Modal(document.getElementById('modalEditarPaquete')).show();
    } catch (error) {
        Swal.fire('Error', 'No se pudo cargar el paquete para editar', 'error');
    }
}

/**
 * Manejar edición de paquete
 */
async function handleEditarPaquete(e) {
    e.preventDefault();
    
    const paqueteId = this.dataset.paqueteId;
    if (!paqueteId) {
        Swal.fire('Error', 'No se pudo identificar el paquete', 'error');
        return;
    }
    
    const destinoSeleccionado = document.querySelector('#destinos-container-editar input[type="radio"]:checked');
    if (!destinoSeleccionado) {
        Swal.fire('Destino requerido', 'Debes seleccionar un destino', 'warning');
        return;
    }
    
    const formData = new FormData(this);
    const data = {
        nombre: formData.get('nombre'),
        origen: formData.get('origen'),
        fecha_inicio: formData.get('fecha_inicio'),
        fecha_fin: formData.get('fecha_fin'),
        precio_total: formData.get('precio_total'),
        disponibles: formData.get('disponibles'),
        destinos: [parseInt(destinoSeleccionado.value)]
    };
    
    try {
        const response = await fetch(`/admin/paquetes/editar/${paqueteId}/api`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        if (response.ok) {
            Swal.fire('¡Éxito!', result.message, 'success').then(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalEditarPaquete'));
                if (modal) modal.hide();
                this.reset();
                cargarPaquetes();
            });
        } else {
            Swal.fire('Error', result.error || 'Error al actualizar el paquete', 'error');
        }
    } catch (error) {
        Swal.fire('Error', 'Error de conexión', 'error');
    }
}

/**
 * Eliminar paquete
 */
async function eliminarPaquete(id, nombre) {
    const result = await Swal.fire({
        title: '¿Estás seguro?',
        text: `¿Deseas eliminar "${nombre}"?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    });
    
    if (result.isConfirmed) {
        try {
            const response = await fetch(`/admin/paquetes/eliminar/${id}/api`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            
            if (response.ok) {
                Swal.fire('¡Eliminado!', data.message, 'success').then(() => cargarPaquetes());
            } else {
                Swal.fire('Error', data.error || 'Error al eliminar el paquete', 'error');
            }
        } catch (error) {
            Swal.fire('Error', 'Error de conexión', 'error');
        }
    }
}

