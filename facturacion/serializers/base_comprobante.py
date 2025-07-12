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
    tipo_igv_codigo = serializers.CharField()
