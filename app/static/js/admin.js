/**
 * Funciones compartidas para el panel de administración
 * Mantiene el código simple y sin redundancia
 */

/**
 * Eliminar un destino (función compartida)
 * @param {number} id - ID del destino
 * @param {string} nombre - Nombre del destino
 * @param {object} options - Opciones adicionales
 * @param {function} options.onSuccess - Callback cuando se elimina exitosamente
 * @param {boolean} options.redirectToList - Si debe redirigir a la lista después de eliminar
 */
async function eliminarDestino(id, nombre, options = {}) {
    const { onSuccess, redirectToList = false } = options;
    
    const result = await Swal.fire({
        title: '¿Estás seguro?',
        text: `¿Estás seguro de eliminar el destino ${nombre}?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    });
    
    if (!result.isConfirmed) {
        return;
    }
    
    try {
        const response = await fetch(`/admin/destinos/eliminar/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        });
        
        // Intentar parsear como JSON primero
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Ejecutar callback personalizado si existe
                if (onSuccess && typeof onSuccess === 'function') {
                    onSuccess(data);
                }
                
                // Mostrar toast de éxito
                if (typeof mostrarToast === 'function') {
                    mostrarToast(data.message || 'Destino eliminado exitosamente', 'success', 'Éxito');
                } else {
                    Swal.fire('¡Eliminado!', data.message || 'Destino eliminado exitosamente', 'success');
                }
                
                // Redirigir si es necesario
                if (redirectToList) {
                    setTimeout(() => {
                        window.location.href = '/admin/destinos';
                    }, 1000);
                }
            } else {
                // Error en formato JSON - mostrar como toast
                if (typeof mostrarToast === 'function') {
                    mostrarToast(data.error || 'Error al eliminar el destino', 'error', 'Error');
                } else {
                    Swal.fire('Error', data.error || 'Error al eliminar el destino', 'error');
                }
            }
        } else if (response.ok || response.redirected) {
            // Respuesta HTML (redirect)
            if (onSuccess && typeof onSuccess === 'function') {
                onSuccess({ message: 'Destino eliminado exitosamente' });
            }
            
            // Mostrar toast de éxito
            if (typeof mostrarToast === 'function') {
                mostrarToast('Destino eliminado exitosamente', 'success', 'Éxito');
            } else {
                Swal.fire('¡Eliminado!', 'Destino eliminado exitosamente', 'success');
            }
            
            if (redirectToList) {
                setTimeout(() => {
                    window.location.href = '/admin/destinos';
                }, 1000);
            }
        } else {
            // Error en formato HTML
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const errorMsg = doc.querySelector('.alert-danger')?.textContent || 'Error al eliminar el destino';
            if (typeof mostrarToast === 'function') {
                mostrarToast(errorMsg, 'error', 'Error');
            } else {
                Swal.fire('Error', errorMsg, 'error');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        if (typeof mostrarToast === 'function') {
            mostrarToast('Error de conexión al eliminar el destino', 'error', 'Error');
        } else {
            Swal.fire('Error', 'Error de conexión al eliminar el destino', 'error');
        }
    }
}

