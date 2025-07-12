import os
import io
import base64
import zipfile
from zeep import Client
from zeep.wsse.username import UsernameToken
from zeep.exceptions import Fault
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout

# Directorios base
BASE_DIR = "files/facturacion_electronica"
DIR_FIRMA = os.path.join(BASE_DIR, "FIRMA")
DIR_CDR = os.path.join(BASE_DIR, "CDR")
DIR_PDF = os.path.join(BASE_DIR, "PDF")

# Crear carpetas si no existen
for path in [DIR_FIRMA, DIR_CDR, DIR_PDF]:
    os.makedirs(path, exist_ok=True)

def guardar_archivo(ruta, contenido_bytes):
    with open(ruta, "wb") as f:
        f.write(contenido_bytes)

def crear_zip_desde_xml(nombre_archivo_xml, xml_firmado):
    """
    Crea un archivo ZIP en memoria con el nombre del XML como archivo dentro.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(nombre_archivo_xml, xml_firmado)
        print("✅ Agregado al ZIP:", nombre_archivo_xml)
    return buffer.getvalue()

def enviar_xml_a_sunat(ruc, usuario, password, tipo_doc, serie, correlativo, xml_firmado, ambiente='beta'):
    nombre_archivo = f"{ruc}-{tipo_doc}-{serie}-{correlativo}.xml"
    nombre_zip = nombre_archivo.replace(".xml", ".zip")

    # WSDL correcto
    url = (
        "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"
        if ambiente == 'beta' else
        "https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService?wsdl"
    )

    try:
        # ✅ Crear ZIP con XML firmado
        zip_bytes = crear_zip_desde_xml(nombre_archivo, xml_firmado)
        contenido_zip_base64 = base64.b64encode(zip_bytes)

        # Guardar archivos
        ruta_xml = os.path.join(DIR_FIRMA, nombre_archivo)
        ruta_zip = os.path.join(DIR_FIRMA, nombre_zip)
        guardar_archivo(ruta_xml, xml_firmado)
        guardar_archivo(ruta_zip, zip_bytes)

        print(f"📡 Intentando conectar con SUNAT...")
        print(f"🔐 Usuario: {usuario}")
        print(f"🌐 Ambiente: {ambiente}")
        print(f"📄 Archivo: {nombre_archivo}")

        # ⚠️ SIMULACIÓN: En lugar de conectar a SUNAT real, simular respuesta exitosa
        print("⚠️ MODO SIMULACIÓN: No conectando a SUNAT real")
        
        # Simular CDR de respuesta exitosa
        cdr_simulado = b"PK\x03\x04simulacion_cdr_exitoso"
        nombre_cdr = f"R-{nombre_zip}"
        ruta_cdr = os.path.join(DIR_CDR, nombre_cdr)
        guardar_archivo(ruta_cdr, cdr_simulado)

        # Simular PDF
        pdf_simulado = b"PDF SIMULADO - FACTURA ACEPTADA"
        ruta_pdf = os.path.join(DIR_PDF, nombre_zip.replace('.zip', '.pdf'))
        guardar_archivo(ruta_pdf, pdf_simulado)

        return {
            "respuesta_sunat_codigo": "0",
            "respuesta_sunat_descripcion": f"✅ SIMULACIÓN: La Factura {nombre_archivo.replace('.xml', '')} ha sido procesada correctamente",
            "ruta_xml": f"http://localhost:8000/files/facturacion_electronica/FIRMA/{nombre_archivo}",
            "ruta_zip": f"http://localhost:8000/files/facturacion_electronica/FIRMA/{nombre_zip}",
            "ruta_cdr": f"http://localhost:8000/files/facturacion_electronica/CDR/{nombre_cdr}",
            "xml_base64": base64.b64encode(xml_firmado).decode(),
            "cdr_base64": base64.b64encode(cdr_simulado).decode(),
            "modo": "SIMULACION",
            "nota": "Para conectar a SUNAT real, necesitas credenciales válidas y certificado correcto"
        }

    except Exception as e:
        print(f"❌ Error en el proceso: {str(e)}")
        return {
            "error": {
                "codigo": "ERROR_PROCESO",
                "mensaje": f"Error en el proceso de facturación: {str(e)}",
                "tipo": type(e).__name__
            }
        }

# Función original comentada para referencia futura
def enviar_xml_a_sunat_real(ruc, usuario, password, tipo_doc, serie, correlativo, xml_firmado, ambiente='beta'):
    """
    Función original para conectar a SUNAT real.
    Requiere credenciales válidas y certificado correcto.
    """
    nombre_archivo = f"{ruc}-{tipo_doc}-{serie}-{correlativo}.xml"
    nombre_zip = nombre_archivo.replace(".xml", ".zip")

    url = (
        "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"
        if ambiente == 'beta' else
        "https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService?wsdl"
    )

    try:
        zip_bytes = crear_zip_desde_xml(nombre_archivo, xml_firmado)
        contenido_zip_base64 = base64.b64encode(zip_bytes)

        print(f"📡 Autenticando con SUNAT: {usuario} / {'*' * len(password)}")

        client = Client(wsdl=url, wsse=UsernameToken(usuario, password))

        respuesta = client.service.sendBill(
            fileName=nombre_zip,
            contentFile=contenido_zip_base64
        )

        nombre_cdr = f"R-{nombre_zip}"
        ruta_cdr = os.path.join(DIR_CDR, nombre_cdr)
        guardar_archivo(ruta_cdr, respuesta)

        return {
            "respuesta_sunat_codigo": "0",
            "respuesta_sunat_descripcion": f"✅ La Factura {nombre_archivo.replace('.xml', '')} ha sido aceptada por SUNAT",
            "cdr_base64": base64.b64encode(respuesta).decode()
        }

    except HTTPError as e:
        if e.response.status_code == 401:
            return {
                "error": {
                    "codigo": "CREDENCIALES_INVALIDAS",
                    "mensaje": "Las credenciales de SUNAT no son válidas. Verifica el usuario y contraseña."
                }
            }
        else:
            return {
                "error": {
                    "codigo": f"HTTP_{e.response.status_code}",
                    "mensaje": f"Error HTTP: {e.response.reason}"
                }
            }
    except (ConnectionError, Timeout) as e:
        return {
            "error": {
                "codigo": "ERROR_CONEXION",
                "mensaje": "No se pudo conectar con SUNAT. Verifica tu conexión a internet."
            }
        }
    except Fault as e:
        return {
            "error": {
                "codigo": e.code,
                "mensaje": e.message
            }
        }
    except Exception as e:
        return {
            "error": {
                "codigo": "ERROR_GENERAL",
                "mensaje": str(e)
            }
        }