from rest_framework import serializers

class BaseEmpresaSerializer(serializers.Serializer):
    ruc = serializers.CharField()
    razon_social = serializers.CharField()
    nombre_comercial = serializers.CharField()
    domicilio_fiscal = serializers.CharField()
    ubigeo = serializers.CharField()
    urbanizacion = serializers.CharField()
    distrito = serializers.CharField()
    provincia = serializers.CharField()
    departamento = serializers.CharField()
    modo = serializers.ChoiceField(choices=["0", "1"])
    usu_secundario_produccion_user = serializers.CharField()
    usu_secundario_produccion_password = serializers.CharField()

class BaseClienteSerializer(serializers.Serializer):
    razon_social_nombres = serializers.CharField()
    numero_documento = serializers.CharField()
    codigo_tipo_entidad = serializers.ChoiceField(choices=["1", "6"])
    cliente_direccion = serializers.CharField()

class BaseItemSerializer(serializers.Serializer):
    producto = serializers.CharField()
    cantidad = serializers.DecimalField(max_digits=10, decimal_places=2)
    precio_base = serializers.DecimalField(max_digits=10, decimal_places=2)
    codigo_sunat = serializers.CharField(required=False, allow_blank=True)
    codigo_producto = serializers.CharField()
    codigo_unidad = serializers.CharField()
    
    # NUEVOS CAMPOS PARA MANEJAR DIFERENTES TIPOS DE OPERACIÓN
    tipo_operacion = serializers.ChoiceField(
        choices=[
            ("01", "Venta gravada"),
            ("02", "Venta exonerada"),
            ("03", "Venta inafecta"),
            ("04", "Exportación"),
            ("05", "Percepción"),
            ("06", "Bonificación"),
            ("07", "Transferencia gratuita")
        ],
        default="01"
    )
    
    # Código de afectación al IGV (Catálogo 7 SUNAT)
    codigo_afectacion_igv = serializers.ChoiceField(
        choices=[
            ("10", "Gravado - Operación Onerosa"),
            ("11", "Gravado - Retiro por premio"),
            ("12", "Gravado - Retiro por publicidad"),
            ("13", "Gravado - Bonificaciones"),
            ("20", "Exonerado - Operación Onerosa"),
            ("21", "Exonerado - Transferencia gratuita"),
            ("30", "Inafecto - Operación Onerosa"),
            ("31", "Inafecto - Retiro por Bonificación"),
            ("32", "Inafecto - Retiro"),
            ("40", "Exportación")
        ],
        default="10"
    )
    
    # Para transferencias gratuitas
    valor_referencial = serializers.DecimalField(
        max_digits=10, decimal_places=2, 
        required=False, 
        allow_null=True,
        help_text="Valor de mercado para transferencias gratuitas"
    )
    
    # Para bonificaciones
    es_bonificacion = serializers.BooleanField(default=False)
    item_relacionado = serializers.IntegerField(
        required=False, 
        allow_null=True,
        help_text="Índice del item al que está relacionada esta bonificación"
    )