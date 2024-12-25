// Inyectar precios desde el backend
const PRICES = JSON.parse('{{ prices | tojson | safe }}');

// Función para calcular el precio dinámicamente
function calculatePrice() {
    const copies = parseInt(document.getElementById('copias').value) || 1;
    let color = document.getElementById('color-input').value;

    // Normalizar el valor de color
    if (color === 'B/N') {
        color = 'byn';
    } else if (color === 'Color') {
        color = 'color';
    }

    const paperWeight = document.getElementById('grosor-papel').value;
    const paperSize = document.getElementById('tamano-papel').value;

    const perCopyPrice = PRICES[color]?.una_cara || 0;
    const weightPrice = PRICES.paper_weight[paperWeight] || 0;
    const sizeMultiplier = PRICES.paper_size[paperSize] || 1;

    const totalPrice = copies * (perCopyPrice + weightPrice) * sizeMultiplier;
    document.getElementById('current-price').textContent = totalPrice.toFixed(2);
}
