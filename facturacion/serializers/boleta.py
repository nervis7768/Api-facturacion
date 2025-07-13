from rest_framework import serializers
from .base_comprobante import BaseEmpresaSerializer, BaseClienteSerializer, BaseItemSerializer

class BoletaVentaSerializer(serializers.Serializer):
    tipo_documento_codigo = serializers.ChoiceField(choices=["03"])  # Boleta
    tipo_operacion = serializers.CharField(default="0101")
    serie = serializers.CharField()
    numero = serializers.CharField()
    fecha_emision = serializers.DateField()
    hora_emision = serializers.TimeField()
    moneda_id = serializers.ChoiceField(choices=["1", "2"])
    forma_pago_id = serializers.ChoiceField(choices=["1", "2"])
    total_gravada = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_igv = serializers.DecimalField(max_digits=10, decimal_places=2)
    nota = serializers.CharField(allow_blank=True, required=False)

class BoletaSerializer(serializers.Serializer):
    empresa = BaseEmpresaSerializer()
    cliente = BaseClienteSerializer()
    venta = BoletaVentaSerializer()
    items = BaseItemSerializer(many=True)
