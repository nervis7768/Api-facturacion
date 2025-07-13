from lxml import etree
from decimal import Decimal

NSMAP = {
    None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
}

CBC = "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}"
CAC = "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}"
EXT = "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}"


def generar_xml_factura_mejorada(datos):
    venta = datos['venta']
    cliente = datos['cliente']
    empresa = datos['empresa']
    items = datos['items']

    # Calcular total_pagar si no existe
    venta["total_pagar"] = float(venta.get("total_pagar", 0.0))
    if not venta["total_pagar"]:
        venta["total_pagar"] = float(venta.get("total_gravada", 0.0)) + float(venta.get("total_igv", 0.0))

    invoice = etree.Element("Invoice", nsmap=NSMAP)

    ext_ubl_extensions = etree.SubElement(invoice, EXT + "UBLExtensions")
    etree.SubElement(etree.SubElement(ext_ubl_extensions, EXT + "UBLExtension"), EXT + "ExtensionContent")

    etree.SubElement(invoice, CBC + "UBLVersionID").text = "2.1"
    etree.SubElement(invoice, CBC + "CustomizationID").text = "2.0"
    etree.SubElement(invoice, CBC + "ProfileID").text = "0101"
    etree.SubElement(invoice, CBC + "ID").text = f"{venta['serie']}-{venta['numero']}"
    etree.SubElement(invoice, CBC + "IssueDate").text = venta['fecha_emision'].isoformat()
    etree.SubElement(invoice, CBC + "IssueTime").text = venta['hora_emision'].isoformat()
    etree.SubElement(invoice, CBC + "InvoiceTypeCode").text = venta['tipo_documento_codigo']
    etree.SubElement(invoice, CBC + "DocumentCurrencyCode").text = "PEN"

    if venta.get('fecha_vencimiento'):
        etree.SubElement(invoice, CBC + "DueDate").text = venta['fecha_vencimiento'].isoformat()

    generar_signature_xml(invoice, empresa)
    generar_supplier_party_xml(invoice, empresa)
    generar_customer_party_xml(invoice, cliente)
    generar_tax_totals_xml(invoice, venta)
    generar_monetary_total_xml(invoice, venta)

    if venta.get('cuotas'):
        generar_cuotas_xml(invoice, venta['cuotas'])

    if venta.get('percepcion'):
        generar_percepcion_xml(invoice, venta['percepcion'])

    generar_items_xml(invoice, items)

    return etree.tostring(invoice, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def generar_signature_xml(invoice, empresa):
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


def generar_supplier_party_xml(invoice, empresa):
    supplier_party = etree.SubElement(invoice, CAC + "AccountingSupplierParty")
    party = etree.SubElement(supplier_party, CAC + "Party")
    party_name = etree.SubElement(party, CAC + "PartyName")
    etree.SubElement(party_name, CBC + "Name").text = empresa['nombre_comercial']
    etree.SubElement(party, CBC + "RegistrationName").text = empresa['razon_social']
    etree.SubElement(party, CBC + "CompanyID", schemeID="6").text = empresa['ruc']


def generar_customer_party_xml(invoice, cliente):
    customer_party = etree.SubElement(invoice, CAC + "AccountingCustomerParty")
    party = etree.SubElement(customer_party, CAC + "Party")
    etree.SubElement(party, CBC + "RegistrationName").text = cliente['razon_social_nombres']
    etree.SubElement(party, CBC + "CompanyID", schemeID=cliente['codigo_tipo_entidad']).text = cliente['numero_documento']


def generar_tax_totals_xml(invoice, venta):
    total_igv = float(venta.get('total_igv', 0.0))
    if total_igv > 0:
        tax_total = etree.SubElement(invoice, CAC + "TaxTotal")
        etree.SubElement(tax_total, CBC + "TaxAmount", currencyID="PEN").text = f"{total_igv:.2f}"
        tax_subtotal = etree.SubElement(tax_total, CAC + "TaxSubtotal")
        etree.SubElement(tax_subtotal, CBC + "TaxAmount", currencyID="PEN").text = f"{total_igv:.2f}"
        tax_category = etree.SubElement(tax_subtotal, CAC + "TaxCategory")
        tax_scheme = etree.SubElement(tax_category, CAC + "TaxScheme")
        etree.SubElement(tax_scheme, CBC + "ID").text = "1000"
        etree.SubElement(tax_scheme, CBC + "Name").text = "IGV"
        etree.SubElement(tax_scheme, CBC + "TaxTypeCode").text = "VAT"


def generar_monetary_total_xml(invoice, venta):
    total = etree.SubElement(invoice, CAC + "LegalMonetaryTotal")

    total_gravada = float(venta.get("total_gravada", 0.0))
    total_pagar = float(venta.get("total_pagar", total_gravada))

    etree.SubElement(total, CBC + "LineExtensionAmount", currencyID="PEN").text = f"{total_gravada:.2f}"
    etree.SubElement(total, CBC + "TaxInclusiveAmount", currencyID="PEN").text = f"{total_pagar:.2f}"
    etree.SubElement(total, CBC + "AllowanceTotalAmount", currencyID="PEN").text = "0.00"
    etree.SubElement(total, CBC + "PayableAmount", currencyID="PEN").text = f"{total_pagar:.2f}"


def generar_items_xml(invoice, items):
    for i, item in enumerate(items, start=1):
        invoice_line = etree.SubElement(invoice, CAC + "InvoiceLine")
        etree.SubElement(invoice_line, CBC + "ID").text = str(i)
        etree.SubElement(invoice_line, CBC + "InvoicedQuantity", unitCode=item["codigo_unidad"]).text = str(item["cantidad"])

        precio_base = Decimal(item["precio_base"])
        cantidad = Decimal(item["cantidad"])
        monto_base = precio_base * cantidad

        etree.SubElement(invoice_line, CBC + "LineExtensionAmount", currencyID="PEN").text = f"{monto_base:.2f}"

        pricing_reference = etree.SubElement(invoice_line, CAC + "PricingReference")
        price_type_code = "01" if not item.get("es_bonificacion") else "02"
        price = etree.SubElement(pricing_reference, CAC + "AlternativeConditionPrice")
        etree.SubElement(price, CBC + "PriceAmount", currencyID="PEN").text = f"{precio_base:.2f}"
        etree.SubElement(price, CBC + "PriceTypeCode").text = price_type_code

        tax_total = etree.SubElement(invoice_line, CAC + "TaxTotal")
        afectacion = item.get("tipo_igv_codigo", "10")

        if afectacion.startswith("1"):
            igv = monto_base * Decimal("0.18")
        elif afectacion in ["11", "12", "13"]:
            valor_referencial = Decimal(item.get("valor_referencial") or monto_base)
            igv = valor_referencial * Decimal("0.18")
        else:
            igv = Decimal("0.00")

        etree.SubElement(tax_total, CBC + "TaxAmount", currencyID="PEN").text = f"{igv:.2f}"
        tax_subtotal = etree.SubElement(tax_total, CAC + "TaxSubtotal")
        etree.SubElement(tax_subtotal, CBC + "TaxAmount", currencyID="PEN").text = f"{igv:.2f}"
        tax_category = etree.SubElement(tax_subtotal, CAC + "TaxCategory")
        etree.SubElement(tax_category, CBC + "TaxExemptionReasonCode").text = afectacion
        tax_scheme = etree.SubElement(tax_category, CAC + "TaxScheme")
        etree.SubElement(tax_scheme, CBC + "ID").text = "1000"
        etree.SubElement(tax_scheme, CBC + "Name").text = "IGV"
        etree.SubElement(tax_scheme, CBC + "TaxTypeCode").text = "VAT"

        item_element = etree.SubElement(invoice_line, CAC + "Item")
        etree.SubElement(item_element, CBC + "Description").text = item["producto"]

        if item.get("codigo_producto"):
            sellers_id = etree.SubElement(item_element, CAC + "SellersItemIdentification")
            etree.SubElement(sellers_id, CBC + "ID").text = item["codigo_producto"]

        price = etree.SubElement(invoice_line, CAC + "Price")
        etree.SubElement(price, CBC + "PriceAmount", currencyID="PEN").text = f"{precio_base:.2f}"


def generar_cuotas_xml(invoice, cuotas):
    for cuota in cuotas:
        payment_terms = etree.SubElement(invoice, CAC + "PaymentTerms")
        etree.SubElement(payment_terms, CBC + "ID").text = cuota.get("id", "Cuota")
        etree.SubElement(payment_terms, CBC + "PaymentMeansID").text = cuota.get("codigo", "Credito")
        etree.SubElement(payment_terms, CBC + "Amount", currencyID="PEN").text = f"{cuota['monto']:.2f}"
        etree.SubElement(payment_terms, CBC + "PaymentDueDate").text = cuota['fecha_vencimiento']


def generar_percepcion_xml(invoice, percepcion):
    additional_monetary_total = etree.SubElement(invoice, CAC + "AdditionalMonetaryTotal")
    etree.SubElement(additional_monetary_total, CBC + "ID").text = "2005"
    etree.SubElement(additional_monetary_total, CBC + "PayableAmount", currencyID="PEN").text = f"{percepcion['monto_percibido']:.2f}"