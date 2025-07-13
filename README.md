API de Facturación Electrónica - Perú
API desarrollada en Django REST Framework para la emisión de comprobantes electrónicos (facturas, boletas y notas de crédito) cumpliendo con las especificaciones técnicas de SUNAT Perú.

🚀 Características
✅ Emisión de Facturas Electrónicas (Tipo 01)
✅ Emisión de Boletas de Venta (Tipo 03)
✅ Emisión de Notas de Crédito/Débito (Tipos 07/08)
✅ Generación automática de XML UBL 2.1
✅ Firma digital con certificados .pfx
✅ Integración con SUNAT (Beta y Producción)
✅ Interfaz web para pruebas
✅ Validación completa de datos
✅ Generación de archivos PDF simulados
✅ Almacenamiento de CDR de respuesta
📋 Requisitos del Sistema
Python 3.8+
Django 5.2.3
PostgreSQL 12+
Certificado digital .pfx válido para SUNAT
Dependencias principales
django==5.2.3
djangorestframework==3.14.0
psycopg2-binary==2.9.7
lxml==4.9.3
cryptography==41.0.3
signxml==3.2.1
zeep==4.2.1
requests==2.31.0
🛠️ Instalación
1. Clonar el repositorio
git clone <url-del-repositorio>
cd api_facturacion
2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
3. Instalar dependencias
pip install -r requirements.txt
4. Configurar base de datos
Editar api_facturacion/settings.py:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db_facturacion_electronica',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
5. Ejecutar migraciones
python manage.py migrate
6. Configurar certificado digital
Colocar tu certificado .pfx en la carpeta certificados/ y actualizar la ruta en:

# facturacion/views/emitir_comprobante.py
path_pfx = "certificados/TU_CERTIFICADO.pfx"
clave_pfx = "tu_password_certificado"
7. Ejecutar servidor
python manage.py runserver
🌐 Uso de la API
Endpoint principal
POST /api/emitir/
Estructura de datos para Factura
{
  "empresa": {
    "ruc": "20103129061",
    "razon_social": "FACTURACION ELECTRONICA MONSTRUO E.I.R.L.",
    "nombre_comercial": "FACTURACION INTEGRAL",
    "domicilio_fiscal": "AV. PRINCIPAL 123",
    "ubigeo": "140101",
    "urbanizacion": "URBANIZACION",
    "distrito": "DISTRITO",
    "provincia": "PROVINCIA",
    "departamento": "DEPARTAMENTO",
    "modo": "0",
    "usu_secundario_produccion_user": "MODDATOS",
    "usu_secundario_produccion_password": "MODDATOS"
  },
  "cliente": {
    "razon_social_nombres": "Hector De La Cruz",
    "numero_documento": "10407086274",
    "codigo_tipo_entidad": "6",
    "cliente_direccion": "AV. CLIENTE 456"
  },
  "venta": {
    "tipo_documento_codigo": "01",
    "tipo_operacion": "0101",
    "serie": "FF03",
    "numero": "12345",
    "fecha_emision": "2025-07-12",
    "moneda_id": "1",
    "forma_pago_id": "1",
    "total_gravada": 500.00,
    "total_igv": 90.00
  },
  "items": [
    {
      "producto": "Producto de Prueba",
      "cantidad": 1.00,
      "precio_base": 100.00,
      "codigo_sunat": "",
      "codigo_producto": "PROD001",
      "codigo_unidad": "ZZ",
      "tipo_igv_codigo": "10"
    }
  ]
}
Respuesta exitosa
{
  "data": {
    "respuesta_sunat_codigo": "0",
    "respuesta_sunat_descripcion": "✅ SIMULACIÓN: La Factura FF03-12345 ha sido procesada correctamente",
    "ruta_xml": "http://localhost:8000/files/facturacion_electronica/FIRMA/20103129061-01-FF03-12345.xml",
    "ruta_cdr": "http://localhost:8000/files/facturacion_electronica/CDR/R-20103129061-01-FF03-12345.zip",
    "ruta_pdf": "http://localhost:8000/files/facturacion_electronica/PDF/20103129061-01-FF03-12345.pdf",
    "xml_base_64": "PD94bWwgdmVyc2lvbj0nMS4wJyBlbmNvZGluZz0nVVRGLTgnPz4K...",
    "cdr_base_64": "UEsDBBQAAAAIAA==",
    "hora_emision": "14:30:25"
  }
}
🖥️ Interfaz Web
La aplicación incluye una interfaz web completa para realizar pruebas:

URL: http://localhost:8000/
Características:
Formulario interactivo para facturación
Validación en tiempo real
Visualización de respuestas JSON
Soporte para múltiples items
Generación automática de fechas y números
📁 Estructura del Proyecto
api_facturacion/
├── api_facturacion/           # Configuración principal
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── facturacion/               # App principal
│   ├── serializers/           # Validadores de datos
│   │   ├── base_comprobante.py
│   │   ├── factura.py
│   │   ├── boleta.py
│   │   └── nota_credito.py
│   ├── services/              # Lógica de negocio
│   │   ├── generador_xml.py
│   │   ├── firmador.py
│   │   ├── sunat_client.py
│   │   └── utilitarios.py
│   └── views/                 # Controladores
│       └── emitir_comprobante.py
├── files/                     # Archivos generados
│   └── facturacion_electronica/
│       ├── FIRMA/             # XML firmados
│       ├── CDR/               # Respuestas de SUNAT
│       └── PDF/               # PDFs generados
├── templates/                 # Frontend
│   └── index.html
└── certificados/              # Certificados digitales
🔧 Configuración
Variables importantes
Modo de operación
"0": Ambiente de pruebas (Beta SUNAT)
"1": Ambiente de producción
Tipos de documento
"01": Factura
"03": Boleta de venta
"07": Nota de crédito
"08": Nota de débito
Tipos de moneda
"1": Soles peruanos (PEN)
"2": Dólares americanos (USD)
Configuración de SUNAT
# Para ambiente Beta
WSDL_BETA = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"

# Para ambiente Producción
WSDL_PROD = "https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService?wsdl"
🔒 Certificados Digitales
Formato requerido
Archivo: .pfx (PKCS#12)
Emisor: Autoridad certificadora autorizada por SUNAT
Vigencia: Debe estar vigente
Uso: Firma de documentos electrónicos
Obtener certificado
Solicitar a una autoridad certificadora autorizada por SUNAT
Descargar en formato .pfx
Colocar en carpeta certificados/
Actualizar ruta y contraseña en el código
🧪 Modo Simulación
Por defecto, la API funciona en modo simulación para facilitar las pruebas sin conectar a SUNAT real:

# En facturacion/services/sunat_client.py
def enviar_xml_a_sunat():
    # ⚠️ SIMULACIÓN: No conectando a SUNAT real
    return {
        "respuesta_sunat_codigo": "0",
        "respuesta_sunat_descripcion": "✅ SIMULACIÓN: Factura procesada correctamente",
        "modo": "SIMULACION"
    }
Activar conexión real a SUNAT
Tener certificado digital válido
Credenciales de usuario secundario SUNAT
Cambiar función enviar_xml_a_sunat_real() por enviar_xml_a_sunat()
📊 Códigos de Respuesta
SUNAT
0: Aceptado
2324: RUC del emisor no existe
2335: Certificado revocado
4000: Error en formato XML
API Interna
200: Procesado correctamente
400: Error en validación de datos
500: Error interno del servidor
🐛 Resolución de Problemas
Error: "Certificate verify failed"
# Instalar certificados de CA
pip install --upgrade certifi
Error: "Database connection failed"
# Verificar PostgreSQL esté ejecutándose
sudo service postgresql start
Error: "Invalid certificate"
Verificar que el certificado .pfx esté vigente
Confirmar que la contraseña sea correcta
Verificar que sea emitido por CA autorizada por SUNAT
Error: "XML validation failed"
Revisar que todos los campos obligatorios estén presentes
Verificar formato de fechas (YYYY-MM-DD)
Confirmar que los códigos SUNAT sean válidos
📜 Cumplimiento Legal
Esta API cumple con:

✅ UBL 2.1 (Universal Business Language)
✅ XMLDSig para firma digital
✅ Resolución de Superintendencia N° 097-2012/SUNAT
✅ Resolución de Superintendencia N° 300-2014/SUNAT
🤝 Contribuciones
Fork el proyecto
Crear branch para nueva feature (git checkout -b feature/nueva-funcionalidad)
Commit cambios (git commit -am 'Agregar nueva funcionalidad')
Push al branch (git push origin feature/nueva-funcionalidad)
Crear Pull Request
📞 Soporte
Documentación SUNAT: Portal SUNAT
Especificaciones técnicas: Facturación Electrónica SUNAT
📄 Licencia
Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

⚠️ Nota importante: Este es un proyecto de demostración. Para uso en producción, asegúrate de:

Implementar medidas de seguridad adicionales
Realizar pruebas exhaustivas
Configurar backup de base de datos
Implementar logs de auditoría
Validar cumplimiento legal específico de tu caso de uso
