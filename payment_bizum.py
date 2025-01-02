from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import qrcode
import io
from flask import send_file

payment_bizum_bp = Blueprint('payment_bizum', __name__, template_folder='templates')

def generate_bizum_qr(phone, amount, concept):
    """
    Genera un código QR con los detalles del pago en texto plano.
    """
    qr_data = f"Paga con Bizum\nNúmero: {phone}\nMonto: {amount} €\nConcepto: {concept}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Generar la imagen del QR
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

@payment_bizum_bp.route('/generate_qr', methods=['GET'])
def generate_qr():
    total_price = session.get('cart_total', 0.0) + session.get('envio_total', 0.0)
    if total_price == 0.0:
        flash("El carrito está vacío.", "danger")
        return redirect(url_for('cart'))

    phone = "+34600000000"  # Número de teléfono de Bizum
    concept = f"Pedido-{session.get('order_id', '0001')}"
    qr_image = generate_bizum_qr(phone, f"{total_price:.2f}", concept)

    return send_file(qr_image, mimetype="image/png")

@payment_bizum_bp.route('/process_payment', methods=['POST'])
def process_payment():
    total_price = session.get('cart_total', 0.0) + session.get('envio_total', 0.0)
    if total_price == 0.0:
        flash("El carrito está vacío o no se calculó el total.", "danger")
        return redirect(url_for('cart'))
    
    # Redirigir a payment.html con los datos necesarios para el pago
    return render_template('payment.html', 
                           cart_total=session.get('cart_total'), 
                           envio_total=session.get('envio_total'), 
                           total_con_envio=total_price)

@payment_bizum_bp.route('/process_payment_final', methods=['POST'])
def process_payment_final():
    reference = request.form.get('reference')  # Número de referencia del pago
    if not reference:
        flash("Por favor, introduce un número de referencia válido.", "danger")
        return redirect(url_for('payment_bizum.process_payment'))
    
    # Aquí puedes guardar el número de referencia para validarlo manualmente más tarde
    session['payment_reference'] = reference
    
    # Confirmación manual (simulación)
    flash(f"Pago recibido con la referencia: {reference}. Será procesado pronto.", "success")
    
    # Vaciar carrito (puedes retrasar esto hasta que valides el pago si prefieres)
    session['cart'] = []
    session['cart_total'] = 0.0
    session['envio_total'] = 0.0
    session.modified = True
    
    return redirect(url_for('index'))
