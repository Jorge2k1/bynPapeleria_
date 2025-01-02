from flask import Blueprint, request, render_template, session
from redsys import Client  # Importa la clase Client desde la librería Redsys

payment_tpv_bp = Blueprint('payment_tpv', __name__)

# Configuración de Redsys
BUSINESS_CODE = "123456789"  # Código de comercio proporcionado por Redsys
SECRET_KEY = "MI_CLAVE_SECRETA"  # Clave secreta proporcionada por Redsys
SANDBOX = True  # Cambiar a False en producción

@payment_tpv_bp.route('/payment_tpv', methods=['GET'])
def payment_tpv():
    """Página para iniciar el pago"""
    cart_total = session.get('cart_total', 0.0)  # Total del carrito
    return render_template('payment_tpv.html', cart_total=cart_total)

@payment_tpv_bp.route('/payment_tpv/process', methods=['POST'])
def process_payment():
    """Generar los parámetros para Redsys"""
    # Crear instancia del cliente de Redsys
    redsys = Client(BUSINESS_CODE, SECRET_KEY, sandbox=SANDBOX)

    # Generar los parámetros del pago
    params = {
        'DS_MERCHANT_AMOUNT': float(session.get('cart_total', 0.0)),  # Monto total en euros
        'DS_MERCHANT_ORDER': '12345678',  # Un número de pedido único
        'DS_MERCHANT_CURRENCY': '978',  # Código de moneda (978 para EUR)
        'DS_MERCHANT_TRANSACTIONTYPE': '0',  # Tipo de transacción (0 para autorizaciones normales)
        'DS_MERCHANT_TERMINAL': '1',  # Número de terminal asignado por Redsys
        'DS_MERCHANT_URLOK': request.host_url + 'payment_tpv/success',
        'DS_MERCHANT_URLKO': request.host_url + 'payment_tpv/failed',
        'DS_MERCHANT_MERCHANTURL': request.host_url + 'payment_tpv/notification',
        'DS_MERCHANT_PRODUCTDESCRIPTION': 'Compra en papelería',
        'DS_MERCHANT_TITULAR': 'Nombre del titular',
        'DS_MERCHANT_MERCHANTNAME': 'Nombre de tu negocio',
        'DS_MERCHANT_CONSUMERLANGUAGE': '001',  # Idioma (001 para español)
    }

    # Generar parámetros codificados y firma
    data = redsys.redsys_generate_request(params)

    # Pasar los datos al frontend para redirigir a Redsys
    return render_template('redirect_to_redsys.html', data=data)

@payment_tpv_bp.route('/payment_tpv/success', methods=['GET'])
def payment_success():
    """Página de éxito del pago"""
    return render_template('payment_success.html')

@payment_tpv_bp.route('/payment_tpv/failed', methods=['GET'])
def payment_failed():
    """Página de error del pago"""
    return render_template('payment_failed.html')

@payment_tpv_bp.route('/payment_tpv/notification', methods=['POST'])
def payment_notification():
    """Manejar notificaciones de Redsys"""
    signature = request.form.get('Ds_Signature')
    parameters = request.form.get('Ds_MerchantParameters')

    # Verificar la firma
    redsys = Client(BUSINESS_CODE, SECRET_KEY, sandbox=SANDBOX)
    valid = redsys.redsys_check_response(signature, parameters)

    if valid:
        # Lógica para procesar el pago exitoso
        return "OK", 200
    else:
        # Manejar pagos no válidos
        return "Fallo en la validación", 400
