from lxml import etree

NSMAP = {
    None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
}

CBC = "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}"
CAC = "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}"
EXT = "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}"

def generar_xml_factura(datos):
    venta = datos['venta']
    cliente = datos['cliente']
    empresa = datos['empresa']
    items = datos['items']

    invoice = etree.Element("Invoice", nsmap=NSMAP)

    # UBLExtensions (firma)
    ext_ubl_extensions = etree.SubElement(invoice, EXT + "UBLExtensions")
    etree.SubElement(etree.SubElement(ext_ubl_extensions, EXT + "UBLExtension"), EXT + "ExtensionContent")

    etree.SubElement(invoice, CBC + "UBLVersionID").text = "2.1"
    etree.SubElement(invoice, CBC + "CustomizationID").text = "2.0"
    etree.SubElement(invoice, CBC + "ProfileID").text = "0101"  # SUNAT exige este valor
    etree.SubElement(invoice, CBC + "ID").text = f"{venta['serie']}-{venta['numero']}"
    etree.SubElement(invoice, CBC + "IssueDate").text = venta['fecha_emision'].isoformat()
    etree.SubElement(invoice, CBC + "IssueTime").text = venta['hora_emision'].isoformat()
    etree.SubElement(invoice, CBC + "InvoiceTypeCode").text = venta['tipo_documento_codigo']
    etree.SubElement(invoice, CBC + "DocumentCurrencyCode").text = "PEN"

    # Firma obligatoria para SUNAT (cac:Signature)
    signature = etree.SubElement(invoice, CAC + "Signature")
    etree.SubElement(signature, CBC + "ID").text = "SignSUNAT"
    signatory_party = etree.SubElement(signature, CAC + "SignatoryParty")
    party_identification = etree.SubElement(signatory_party, CAC + "PartyIdentification")
    etree.SubElement(party_identification, CBC + "ID").text = empresa["ruc"]
    party_name = etree.SubElement(signatory_party, CAC + "PartyName")
    etree.SubElement(party_name, CBC + "Name").text = empresa["nombre_comercial"]
    digital_signature = etree.SubElement(signature, CAC + "DigitalSignatureAttachment")
    external_ref = etree.SubElement(digital_signature, CAC + "ExternalReference")
    etree.SubElement(external_ref, CBC + "URI").text = "#SignatureSP"

    # Emisor
    supplier_party = etree.SubElement(invoice, CAC + "AccountingSupplierParty")
    party = etree.SubElement(supplier_party, CAC + "Party")
    party_name = etree.SubElement(party, CAC + "PartyName")
    etree.SubElement(party_name, CBC + "Name").text = empresa['nombre_comercial']
    etree.SubElement(party, CBC + "RegistrationName").text = empresa['razon_social']
    etree.SubElement(party, CBC + "CompanyID", schemeID="6").text = empresa['ruc']

    # Cliente
    customer_party = etree.SubElement(invoice, CAC + "AccountingCustomerParty")
    party2 = etree.SubElement(customer_party, CAC + "Party")
    etree.SubElement(party2, CBC + "RegistrationName").text = cliente['razon_social_nombres']
    etree.SubElement(party2, CBC + "CompanyID", schemeID=cliente['codigo_tipo_entidad']).text = cliente['numero_documento']

    # Totales de impuestos
    total_igv = float(venta['total_igv'])
    tax_total = etree.SubElement(invoice, CAC + "TaxTotal")
    etree.SubElement(tax_total, CBC + "TaxAmount", currencyID="PEN").text = f"{total_igv:.2f}"
    tax_subtotal = etree.SubElement(tax_total, CAC + "TaxSubtotal")
    etree.SubElement(tax_subtotal, CBC + "TaxAmount", currencyID="PEN").text = f"{total_igv:.2f}"
    tax_category = etree.SubElement(tax_subtotal, CAC + "TaxCategory")
    tax_scheme = etree.SubElement(tax_category, CAC + "TaxScheme")
    etree.SubElement(tax_scheme, CBC + "ID").text = "1000"
    etree.SubElement(tax_scheme, CBC + "Name").text = "IGV"
    etree.SubElement(tax_scheme, CBC + "TaxTypeCode").text = "VAT"

    # Monto total
    total = etree.SubElement(invoice, CAC + "LegalMonetaryTotal")
    total_pagar = float(venta['total_gravada']) + float(venta['total_igv'])
    etree.SubElement(total, CBC + "PayableAmount", currencyID="PEN").text = f"{total_pagar:.2f}"

    # Ítems
    for idx, item in enumerate(items, start=1):
        line = etree.SubElement(invoice, CAC + "InvoiceLine")
        cantidad = float(item['cantidad'])
        precio = float(item['precio_base'])
        monto_linea = cantidad * precio
        igv_linea = monto_linea * 0.18

        etree.SubElement(line, CBC + "ID").text = str(idx)
        etree.SubElement(line, CBC + "InvoicedQuantity", unitCode=item['codigo_unidad']).text = f"{cantidad:.2f}"
        etree.SubElement(line, CBC + "LineExtensionAmount", currencyID="PEN").text = f"{monto_linea:.2f}"

        # Impuestos por ítem
        tax_total_line = etree.SubElement(line, CAC + "TaxTotal")
        etree.SubElement(tax_total_line, CBC + "TaxAmount", currencyID="PEN").text = f"{igv_linea:.2f}"

        tax_subtotal = etree.SubElement(tax_total_line, CAC + "TaxSubtotal")
        etree.SubElement(tax_subtotal, CBC + "TaxAmount", currencyID="PEN").text = f"{igv_linea:.2f}"
        tax_category = etree.SubElement(tax_subtotal, CAC + "TaxCategory")
        etree.SubElement(tax_category, CBC + "ID").text = item['tipo_igv_codigo']
        etree.SubElement(tax_category, CBC + "Percent").text = "18.00"
        etree.SubElement(tax_category, CBC + "TaxExemptionReasonCode").text = item['tipo_igv_codigo']
        tax_scheme = etree.SubElement(tax_category, CAC + "TaxScheme")
        etree.SubElement(tax_scheme, CBC + "ID").text = "1000"
        etree.SubElement(tax_scheme, CBC + "Name").text = "IGV"
        etree.SubElement(tax_scheme, CBC + "TaxTypeCode").text = "VAT"

        # Precio
        price = etree.SubElement(line, CAC + "Price")
        etree.SubElement(price, CBC + "PriceAmount", currencyID="PEN").text = f"{precio:.2f}"

    return etree.tostring(invoice, pretty_print=True, xml_declaration=True, encoding="UTF-8")
