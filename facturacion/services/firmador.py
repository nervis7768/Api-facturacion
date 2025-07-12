from cryptography.hazmat.primitives.serialization import pkcs12
from signxml import XMLSigner, methods
from lxml import etree
from cryptography.hazmat.primitives import serialization


def firmar_xml(xml_bytes, pfx_path, pfx_password):
    # Leer el archivo PFX
    with open(pfx_path, "rb") as f:
        pfx_data = f.read()

    try:
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            pfx_data, pfx_password.encode()
        )
    except Exception as e:
        raise ValueError(f"Error al cargar el certificado .pfx: {e}")

    if not private_key or not certificate:
        raise ValueError("El certificado no contiene clave privada o certificado público.")

    # Serializar a PEM
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    certificate_pem = certificate.public_bytes(serialization.Encoding.PEM)

    # Parsear XML original
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml_bytes, parser=parser)

    # Obtener namespace "ext"
    nsmap = root.nsmap
    ext_ns = nsmap.get("ext", "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2")

    # Buscar nodo <ext:ExtensionContent>
    ext_content = root.find(".//{%s}ExtensionContent" % ext_ns)
    if ext_content is None:
        raise ValueError("El XML no contiene <ext:ExtensionContent>. SUNAT requiere esta estructura para firmar.")

    # Firmar XML con signxml (no inserta aún)
    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256"
    )
    signed_root = signer.sign(root, key=private_key_pem, cert=certificate_pem)

    # Buscar nodo <Signature> generado
    signature_element = signed_root.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
    if signature_element is None:
        raise ValueError("No se generó el nodo <ds:Signature>. Verifica el certificado.")

    # Eliminar firmas duplicadas (fuera de <ExtensionContent>)
    for sig in root.findall(".//{http://www.w3.org/2000/09/xmldsig#}Signature"):
        if sig.getparent() is not ext_content:
            sig.getparent().remove(sig)

    # Insertar la firma dentro del <ext:ExtensionContent>
    ext_content.append(signature_element)

    # Retornar el XML firmado
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")
