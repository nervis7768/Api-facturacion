from rest_framework import serializers
from .base_comprobante import BaseEmpresaSerializer, BaseClienteSerializer, BaseItemSerializer

class FacturaVentaSerializer(serializers.Serializer):
    tipo_documento_codigo = serializers.ChoiceField(choices=["01"])  # Factura
    tipo_operacion = serializers.CharField(default="0101")
    serie = serializers.CharField()
    numero = serializers.CharField()
    fecha_emision = serializers.DateField()
    hora_emision = serializers.TimeField()
    fecha_vencimiento = serializers.DateField(required=False, allow_null=True)
    moneda_id = serializers.ChoiceField(choices=["1", "2"])  # PEN, USD
    forma_pago_id = serializers.ChoiceField(choices=["1", "2"])  # contado, crédito
    total_gravada = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_igv = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_exonerada = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    total_inafecta = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    nota = serializers.CharField(allow_blank=True, required=False)

class FacturaSerializer(serializers.Serializer):
    empresa = BaseEmpresaSerializer()
    cliente = BaseClienteSerializer()
    venta = FacturaVentaSerializer()
    items = BaseItemSerializer(many=True)
