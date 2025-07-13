from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import base64
from datetime import datetime, time

from facturacion.serializers.factura import FacturaSerializer as ComprobanteSerializer
from facturacion.services.generador_xml import generar_xml_factura_mejorada
from facturacion.services.firmador import firmar_xml
from facturacion.services.sunat_client import enviar_xml_a_sunat
from facturacion.services.utilitarios import generar_nombre_archivo, codificar_a_base64

class EmitirComprobanteView(APIView):
    def post(self, request):
        serializer = ComprobanteSerializer(data=request.data)
        if serializer.is_valid():
            datos = serializer.validated_data
            venta = datos['venta']
            empresa = datos['empresa']

            # Generar hora automáticamente si no viene
            if not venta.get('hora_emision'):
                ahora = datetime.now()
                venta['hora_emision'] = time(ahora.hour, ahora.minute, ahora.second)
                print(f"🕐 Hora generada automáticamente: {venta['hora_emision']}")

            # Nombre del archivo
            nombre_archivo = generar_nombre_archivo(
                empresa['ruc'],
                venta['tipo_documento_codigo'],
                venta['serie'],
                venta['numero']
            ) + ".xml"

            # 🔄 Generar XML MEJORADO
            xml_bytes = generar_xml_factura_mejorada(datos)

            # Firma
            path_pfx = "certificados/C23022479065.pfx"
            clave_pfx = empresa.get("clave_certificado_pfx", "Ch14pp32023")
            xml_firmado = firmar_xml(xml_bytes, path_pfx, clave_pfx)

            # Guardar XML firmado
            ruta_xml = f"files/facturacion_electronica/FIRMA/{nombre_archivo}"
            os.makedirs(os.path.dirname(ruta_xml), exist_ok=True)
            with open(ruta_xml, "wb") as f:
                f.write(xml_firmado)

            # Enviar a SUNAT
            response = enviar_xml_a_sunat(
                ruc=empresa['ruc'],
                usuario=empresa['usu_secundario_produccion_user'],
                password=empresa['usu_secundario_produccion_password'],
                tipo_doc=venta['tipo_documento_codigo'],
                serie=venta['serie'],
                correlativo=venta['numero'],
                xml_firmado=xml_firmado,
                ambiente='beta'
            )

            # Error de SUNAT
            if 'error' in response:
                return Response({
                    "error": {
                        "codigo": response['error'].get("codigo", "ERROR_DESCONOCIDO"),
                        "mensaje": response['error'].get("mensaje", "Error desconocido desde SUNAT"),
                        "tipo": response['error'].get("tipo", "Unknown")
                    }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Guardar CDR
            ruta_cdr = f"files/facturacion_electronica/CDR/R-{nombre_archivo.replace('.xml', '.zip')}"
            with open(ruta_cdr, "wb") as f:
                f.write(base64.b64decode(response["cdr_base64"]))

            # Simular PDF
            ruta_pdf = f"files/facturacion_electronica/PDF/{nombre_archivo.replace('.xml', '.pdf')}"
            with open(ruta_pdf, "wb") as f:
                f.write(b"PDF SIMULADO")

            return Response({
                "data": {
                    "respuesta_sunat_codigo": response.get("respuesta_sunat_codigo", "0"),
                    "respuesta_sunat_descripcion": response.get("respuesta_sunat_descripcion", "Aceptado por SUNAT"),
                    "ruta_xml": f"http://localhost:8000/{ruta_xml.replace(os.sep, '/')}",
                    "ruta_cdr": f"http://localhost:8000/{ruta_cdr.replace(os.sep, '/')}",
                    "ruta_pdf": f"http://localhost:8000/{ruta_pdf.replace(os.sep, '/')}",
                    "codigo_hash": "hash-simulacion",
                    "xml_base_64": codificar_a_base64(xml_firmado),
                    "cdr_base_64": response["cdr_base64"],
                    "hora_emision": str(venta['hora_emision'])
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)