# facturacion/urls.py
from django.urls import path
from facturacion.views.emitir_comprobante import EmitirComprobanteView

urlpatterns = [
     path('emitir/', EmitirComprobanteView.as_view(), name='emitir_comprobante'),
]