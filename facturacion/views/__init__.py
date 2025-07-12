from django.shortcuts import render

# Create your views here.

def index(request):
    """
    Vista principal para mostrar el frontend de pruebas
    de la API de facturación electrónica
    """
    return render(request, 'index.html')

# Importar las vistas de otros módulos
from .emitir_comprobante import EmitirComprobanteView