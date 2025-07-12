# services/utilitarios.py

import hashlib
import base64
from datetime import datetime

def generar_nombre_archivo(ruc, tipo_doc, serie, numero):
    return f"{ruc}-{tipo_doc}-{serie}-{numero}.xml"

def obtener_hash(xml_bytes):
    sha256 = hashlib.sha256()
    sha256.update(xml_bytes)
    return sha256.hexdigest()

def codificar_a_base64(xml_bytes):
    return base64.b64encode(xml_bytes).decode("utf-8")

def timestamp_actual():
    return datetime.now().isoformat()
