from rest_framework import serializers
from .base_comprobante import BaseEmpresaSerializer, BaseClienteSerializer, BaseItemSerializer

class NotaVentaSerializer(serializers.Serializer):
    tipo_documento_codigo = serializers.ChoiceField(choices=["07", "08"])  # Nota crédito o débito
    serie = serializers.CharField()
    numero = serializers.CharField()
    fecha_emision = serializers.DateField()
    hora_emision = serializers.TimeField()
    moneda_id = serializers.ChoiceField(choices=["1", "2"])
    total_gravada = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_igv = serializers.DecimalField(max_digits=10, decimal_places=2)
    documento_afectado = serializers.CharField()
    tipo_nota = serializers.CharField()
    motivo_nota = serializers.CharField()

class NotaCreditoSerializer(serializers.Serializer):
    empresa = BaseEmpresaSerializer()
    cliente = BaseClienteSerializer()
    venta = NotaVentaSerializer()
    items = BaseItemSerializer(many=True)
