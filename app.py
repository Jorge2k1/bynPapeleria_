from flask import Flask, request, render_template, redirect, url_for, session, flash
import os
import json
import fitz  # PyMuPDF
from payment_bizum import payment_bizum_bp  # Importa el módulo de Bizum
from flask_sqlalchemy import SQLAlchemy
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)

# Registrar el blueprint para Bizum
app.register_blueprint(payment_bizum_bp, url_prefix='/payment_bizum')

app.secret_key = 'super_secret_key'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/papeleriabyn'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'mananes.jm@gmail.com'
EMAIL_PASSWORD = 'loxvisgikvhgppsi'


class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_nombre = db.Column(db.String(255), nullable=False)
    cliente_email = db.Column(db.String(255), nullable=False)
    detalles_pedido = db.Column(db.Text, nullable=False)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.Enum('pendiente', 'procesado'), default='pendiente')
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())
    direccion = db.Column(db.String(255), nullable=True)
    provincia = db.Column(db.String(255), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)

# Crea la tabla automáticamente
with app.app_context():
    db.create_all()

UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load pricing from JSON
with open('pricing.json') as f:
    PRICES = json.load(f)

def count_pdf_pages(file_path):
    try:
        with fitz.open(file_path) as pdf:
           return pdf.page_count
    except Exception as e:
        print(f"Error al contar páginas del PDF: {e}")
        return 0

def calculate_folder_price(folder):
    config = folder['configuracion']
    copies = int(config.get('copias', 1))
    color = config.get('color', 'byn').lower()
    cara = config.get('cara', 'una_cara')
    encuadernacion = config.get('encuadernacion', 'hasta_50_hojas')

    per_page_price = PRICES.get(color, {}).get(cara, 0)
    encuadernacion_price = PRICES['encuadernacion_a4'].get(encuadernacion, 0)

    total_price = copies * per_page_price + encuadernacion_price
    return round(total_price, 2)

def calculate_cart_total(cart):
    return round(sum(calculate_folder_price(folder) for folder in cart), 2)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'folders' not in session:
        session['folders'] = []
    if 'cart' not in session:
        session['cart'] = []
    if 'cart_total' not in session:
        session['cart_total'] = 0.0

    cart_total = session['cart_total']
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create_folder':
            folder_name = f"Carpeta {len(session['folders']) + 1}"
            session['folders'].append({'name': folder_name, 'archivos': [], 'configuracion': {}})
            session.modified = True
            return redirect(url_for('index'))

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
            return redirect(url_for('index'))

        elif action == 'update_config':
            folder_name = request.form['folder_name']
            folder = next((f for f in session['folders'] if f['name'] == folder_name), None)
            if folder:
                folder['configuracion'] = {
                    'copias': request.form.get('copias', '1'),
                    'color': request.form.get('color', 'byn'),
                    'cara': request.form.get('cara', 'una_cara'),
                    'encuadernacion': request.form.get('encuadernacion', 'hasta_50_hojas'),
                    'comentarios': request.form.get('comentarios', '')
                }
                session.modified = True
            return redirect(url_for('index'))

        elif action == 'add_to_cart':
            cart_total = float(request.form.get("cart_total", 0.0))
            envio_total = float(request.form.get("envio_total", 0.0))

            name = request.form.get("name")
            direccion = request.form.get("direccion")
            provincia = request.form.get("provincia")
            email = request.form.get("email")
            telefono = request.form.get("telefono")

            session["cart_total"] = cart_total
            session["envio_total"] = envio_total
            session["name"] = name
            session["envio_direccion"] = direccion
            session["envio_provincia"] = provincia
            session["envio_email"] = email
            session["envio_telefono"] = telefono

            for folder in session["folders"]:
                if folder["configuracion"]:
                    existing_folder = next((f for f in session["cart"] if f["name"] == folder["name"]), None)
                    if existing_folder:
                        session["cart"].remove(existing_folder)
                    session["cart"].append(folder.copy())
            session.modified = True

            return {"success": True}


    return render_template('index.html', folders=session['folders'], cart_total=cart_total, prices=PRICES)

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    cart_total = session.get('cart_total', 0.0)
    envio_total = session.get('envio_total', 0.0)
    total_con_envio = round(cart_total + envio_total, 2)
    return render_template('cart.html', cart=cart, cart_total=cart_total, envio_total=envio_total, total_con_envio=total_con_envio)

@app.route('/procesar_pedido', methods=['POST'])
def procesar_pedido():
    cliente_nombre = session.get('name', 'Cliente Anónimo')
    cliente_email = session.get('envio_email', 'correo@ejemplo.com')
    detalles_pedido = session.get('cart', [])
    total = session.get('cart_total', 0.0)
    direccion = session.get('envio_direccion', None)
    provincia = session.get('envio_provincia', None)
    telefono = session.get('envio_telefono', None)

    if not detalles_pedido:
        return "No hay productos en el carrito para procesar."

    pedido = Pedido(
        cliente_nombre=cliente_nombre,
        cliente_email=cliente_email,
        detalles_pedido=json.dumps(detalles_pedido, ensure_ascii=False, indent=4),
        total=total,
        direccion=direccion,
        provincia=provincia,
        telefono=telefono
    )
    db.session.add(pedido)
    db.session.commit()

    # Limpiar la sesión
    session['cart'] = []
    session['cart_total'] = 0.0
    session['envio_direccion'] = None
    session['envio_provincia'] = None
    session['envio_email'] = None
    session['envio_telefono'] = None
    session.modified = True

    # Enviar correo con los detalles del pedido
    enviar_correo_pedido(pedido)
    return f"Pedido procesado correctamente. ID del pedido: {pedido.id}"

def enviar_correo_pedido(pedido):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = 'mananes.jm@gmail.com'
        msg['Subject'] = f"Nuevo pedido recibido: {pedido.id}"

        detalles_pedido = json.loads(pedido.detalles_pedido)
        detalles_pedido_formateados = ""
        for folder in detalles_pedido:
            detalles_pedido_formateados += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{folder['name']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        {"<br>".join([f"{archivo['name']} ({archivo.get('pages', 0)} páginas)" for archivo in folder.get('archivos', [])])}
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        {"<br>".join([f"{key}: {value}" for key, value in folder.get('configuracion', {}).items()])}
                    </td>
                </tr>
            """

        body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .header {{
                    background-color: #f4f4f4;
                    padding: 10px;
                    text-align: center;
                    font-size: 18px;
                    font-weight: bold;
                }}
                .total {{
                    font-size: 25px;

                }}
                .details {{
                    font-size: 17px;
                    margin: 20px 0;
                    
                }}
                .details th, .details td {{
                    text-align: left;
                    font-size: 17px;

                }}
                .table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .table th, .table td {{
                    padding: 8px;
                    border: 1px solid #ddd;
                    text-align: left;
                }}
                .table th {{
                    background-color: #f4f4f4;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 17px;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="header">Nuevo Pedido Recibido</div>
            <p>Se ha recibido un nuevo pedido con los siguientes detalles:</p>

            <div class="details">
                <p class"total" ><strong>Total:</strong> {pedido.total} €</p>
                <p><strong>Nombre del cliente:</strong> {pedido.cliente_nombre}</p>
                <p><strong>Email del cliente:</strong> {pedido.cliente_email}</p>
                <p><strong>Dirección:</strong> {pedido.direccion}</p>
                <p><strong>Provincia:</strong> {pedido.provincia}</p>
                <p><strong>Teléfono:</strong> {pedido.telefono}</p>
            </div>

            <table class="table">
                <thead>
                    <tr>
                        <th>Carpeta</th>
                        <th>Archivos</th>
                        <th>Configuración</th>
                    </tr>
                </thead>
                <tbody class="details">
                    {detalles_pedido_formateados}
                </tbody>
            </table>

            <div class="footer">
                <p> <strong>ARCHIVOS DEL CLIENTE ADJUNTOS A ESTE EMAIL</strong> </p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        for folder in detalles_pedido:
            for archivo in folder.get('archivos', []):
                file_name = archivo['name']
                file_path = os.path.join(UPLOAD_FOLDER, file_name)
                if os.path.exists(file_path):  # Verifica si el archivo existe
                    try:
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename="{file_name}"'
                            )
                            msg.attach(part)
                    except Exception as e:
                        print(f"Error adjuntando el archivo {file_name}: {e}")
                else:
                    print(f"Archivo no encontrado: {file_name}")

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, 'mananes.jm@gmail.com', msg.as_string())
        server.quit()
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

if __name__ == '__main__':
    app.run(debug=True)
    # from werkzeug.middleware.proxy_fix import ProxyFix
    # app.wsgi_app = ProxyFix(app.wsgi_app)
    # app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

