from flask import Flask, request, render_template, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'folders' not in session:
        session['folders'] = []

    if 'cart' not in session:
        session['cart'] = []

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create_folder':
            folder_name = f"Carpeta {len(session['folders']) + 1}"
            session['folders'].append({'name': folder_name, 'archivos': [], 'configuracion': {}})
            session.modified = True

        elif action == 'upload_to_folder':
            folder_name = request.form['folder_name']
            folder = next((f for f in session['folders'] if f['name'] == folder_name), None)
            if folder:
                archivos = request.files.getlist('file')
                for archivo in archivos:
                    if archivo and archivo.filename:
                        archivo.save(os.path.join(UPLOAD_FOLDER, archivo.filename))
                        folder['archivos'].append(archivo.filename)
                session.modified = True

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

        elif action == 'add_to_cart':
            for folder in session['folders']:
                if folder['configuracion']:
                    # Buscar si la carpeta ya está en el carrito
                    existing_folder = next((f for f in session['cart'] if f['name'] == folder['name']), None)
                    if existing_folder:
                        # Reemplazar la carpeta existente en el carrito
                        session['cart'].remove(existing_folder)
                    # Añadir la carpeta actualizada al carrito
                    session['cart'].append(folder.copy())
            session.modified = True
            print(f"Carrito actualizado: {session['cart']}")


    return render_template('index.html', folders=session['folders'])


@app.route('/cart')
def cart():
    print(f"Carrito actual: {session.get('cart', [])}")
    return render_template('cart.html', cart=session.get('cart', []))

if __name__ == '__main__':
    app.run(debug=True)
