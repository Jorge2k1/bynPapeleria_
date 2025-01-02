let activeFolder = null;

// Función para establecer la carpeta activa y cargar sus configuraciones
function setActiveFolder(folderName) {
    activeFolder = folderName;
    document.getElementById('active-folder').value = folderName;

    const folderElement = document.querySelector(`[data-folder-name="${folderName}"]`);
    const config = JSON.parse(folderElement.getAttribute('data-config'));

    // Cargar valores en el formulario
    document.getElementById('copias').value = config.copias || 1;
    document.getElementById('color-input').value = config.color || 'B/N';
    document.getElementById('tamano-papel').value = config.tamano_papel || 'A4 (297 x 210 mm)';
    document.getElementById('grosor-papel').value = config.grosor_papel || '80 gr (Estándar)';

    // Actualizar los botones activos de color
    document.querySelectorAll('#color-impresion .btn').forEach(btn => btn.classList.remove('active'));
    const activeButton = document.getElementById(`color-${config.color.toLowerCase().replace(/\s/g, '')}`);
    if (activeButton) activeButton.classList.add('active');
}

// Función para enviar la configuración al backend
function sendConfigUpdate(callback = null) {
    const configForm = document.getElementById('config-form');
    const formData = new FormData(configForm);

    fetch('/', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (response.ok) {
            console.log('Configuración guardada.');
            if (callback) callback();
        } else {
            console.error('Error al guardar configuración.');
        }
    })
    .catch(error => console.error('Error al enviar la configuración:', error));
}

// Función para manejar cambios en los valores de copias
function updateCopies(delta) {
    const copiesInput = document.getElementById('copias');
    let copies = parseInt(copiesInput.value) + delta;
    copies = Math.max(1, copies);
    copiesInput.value = copies;

    // Recalcular el precio después del cambio
    calculatePrice();
    sendConfigUpdate();
}

// Función para seleccionar color y recalcular
function selectColor(color) {
    document.getElementById('color-input').value = color;
    calculatePrice();
    sendConfigUpdate();
}
