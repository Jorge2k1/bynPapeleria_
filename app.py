from flask import Flask, request, render_template, redirect, url_for, session
import os
import json
import fitz  # PyMuPDF

app = Flask(__name__)
app.secret_key = 'super_secret_key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load pricing from JSON
with open('pricing.json') as f:
    PRICES = json.load(f)

def count_pdf_pages(file_path):
    """Cuenta las páginas de un archivo PDF."""
    try:
        with fitz.open(file_path) as pdf:
           return pdf.page_count
    except Exception as e:
        print(f"Error al contar páginas del PDF: {e}")
        return 0

def calculate_folder_price(folder):
    config = folder['configuracion']
    copies = int(config.get('copias', 1))
    color = config.get('color', 'B/N').lower()
    paper_weight = config.get('grosor_papel', '80 gr (Estándar)')
    paper_size = config.get('tamano_papel', 'A4 (297 x 210 mm)')

    per_copy_price = PRICES.get(color, {}).get('una_cara', 0)
    weight_price = PRICES['paper_weight'].get(paper_weight, 0)
    size_multiplier = PRICES['paper_size'].get(paper_size, 1)

    return round(copies * (per_copy_price + weight_price) * size_multiplier, 2)

def calculate_cart_total(cart):
    return round(sum(calculate_folder_price(folder) for folder in cart), 2)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'folders' not in session:
        session['folders'] = []
    if 'cart' not in session:
        session['cart'] = []
    if 'cart_total' not in session:  # Asegúrate de que cart_total esté definido
        session['cart_total'] = 0.0

    cart_total = session['cart_total']
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create_folder':
            folder_name = f"Carpeta {len(session['folders']) + 1}"
            session['folders'].append({'name': folder_name, 'archivos': [], 'configuracion': {}})
            session.modified = True
            return redirect(url_for('index'))  # Redirige a la misma página después de crear la carpeta

        elif action == 'upload_to_folder':
            folder_name = request.form['folder_name']
            folder = next((f for f in session['folders'] if f['name'] == folder_name), None)
            if folder:
                archivos = request.files.getlist('file')
                for archivo in archivos:
                    if archivo and archivo.filename:
                        file_path = os.path.join(UPLOAD_FOLDER, archivo.filename)
                        archivo.save(file_path)
                        num_pages = count_pdf_pages(file_path)
                        folder['archivos'].append({'name': archivo.filename, 'pages': num_pages})
                session.modified = True
            return redirect(url_for('index'))  # Redirige tras subir archivos

        elif action == 'update_config':
            folder_name = request.form['folder_name']
            folder = next((f for f in session['folders'] if f['name'] == folder_name), None)
            if folder:
                folder['configuracion'] = {
                    'copias': request.form.get('copias', '1'),
                    'color': request.form.get('color', 'B/N'),
                    'tamano_papel': request.form.get('tamano_papel', 'A4 (297 x 210 mm)'),
                    'grosor_papel': request.form.get('grosor_papel', '80 gr (Estándar)')
                }
                session.modified = True
            return redirect(url_for('index'))  # Redirige tras actualizar configuración

        elif action == 'add_to_cart':
            cart_total = request.form.get("cart_total")  # Recibe el precio desde el frontend
            session["cart_total"] = float(cart_total) if cart_total else 0.0  # Guarda el precio en sesión

            for folder in session["folders"]:
                if folder["configuracion"]:
                    existing_folder = next((f for f in session["cart"] if f["name"] == folder["name"]), None)
                    if existing_folder:
                        session["cart"].remove(existing_folder)
                    session["cart"].append(folder.copy())
            session.modified = True
            return redirect(url_for('cart'))  # Redirige al carrito

    return render_template('index.html', folders=session['folders'], cart_total=cart_total, prices=PRICES)

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    cart_total = session.get('cart_total', 0.0)  # Obtén el precio total guardado
    return render_template('cart.html', cart=cart, cart_total=cart_total)

if __name__ == '__main__':
    app.run(debug=True)
