from rest_framework import serializers
from .base_comprobante import BaseEmpresaSerializer, BaseClienteSerializer, BaseItemSerializer

class CuotaSerializer(serializers.Serializer):
    numero_cuota = serializers.IntegerField()
    fecha_vencimiento = serializers.DateField()
    importe_cuota = serializers.DecimalField(max_digits=10, decimal_places=2)

class PercepcionSerializer(serializers.Serializer):
    regimen_percepcion = serializers.ChoiceField(
        choices=[
            ("01", "Percepción venta interna"),
            ("02", "Percepción a la adquisición de combustible"),
            ("03", "Percepción realizada al agente de percepción")
        ],
        required=False
    )
    tasa_percepcion = serializers.DecimalField(
        max_digits=5, decimal_places=2,
        required=False,
        help_text="Tasa de percepción (ej: 2.00 para 2%)"
    )
    monto_percepcion = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        required=False
    )
    total_incluido_percepcion = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        required=False
    )

class FacturaVentaSerializer(serializers.Serializer):
    tipo_documento_codigo = serializers.ChoiceField(choices=["01"])  # Factura
    tipo_operacion = serializers.CharField(default="0101")
    serie = serializers.CharField()
    numero = serializers.CharField()
    fecha_emision = serializers.DateField()
    hora_emision = serializers.TimeField(required=False, allow_null=True)
    fecha_vencimiento = serializers.DateField(required=False, allow_null=True)
    moneda_id = serializers.ChoiceField(choices=["1", "2"])  # PEN, USD
    forma_pago_id = serializers.ChoiceField(choices=["1", "2"])  # contado, crédito
    
    # TOTALES ACTUALIZADOS
    total_gravada = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_igv = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_exonerada = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_inafecta = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_gratuita = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # CAMPOS PARA VENTAS AL CRÉDITO
    cuotas = CuotaSerializer(many=True, required=False)
    
    # CAMPOS PARA PERCEPCIÓN
    percepcion = PercepcionSerializer(required=False)
    
    nota = serializers.CharField(allow_blank=True, required=False)

class FacturaSerializer(serializers.Serializer):
    empresa = BaseEmpresaSerializer()
    cliente = BaseClienteSerializer()
    venta = FacturaVentaSerializer()
    items = BaseItemSerializer(many=True)
    