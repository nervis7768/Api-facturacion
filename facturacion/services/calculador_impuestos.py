from decimal import Decimal, ROUND_HALF_UP

def calcular_impuestos_item(item_data):
    """
    Calcula los impuestos de un item según su tipo de operación
    """
    cantidad = Decimal(str(item_data['cantidad']))
    precio_base = Decimal(str(item_data['precio_base']))
    codigo_afectacion = item_data['codigo_afectacion_igv']
    
    monto_base = cantidad * precio_base
    
    # Definir cálculos según código de afectación
    if codigo_afectacion.startswith('1'):  # Gravado
        if codigo_afectacion == '10':  # Operación onerosa
            igv = monto_base * Decimal('0.18')
            total_gravada = monto_base
            total_exonerada = Decimal('0')
            total_inafecta = Decimal('0')
            total_gratuita = Decimal('0')
        elif codigo_afectacion in ['11', '12', '13', '14', '15', '16']:  # Retiros/bonificaciones
            valor_referencial = Decimal(str(item_data.get('valor_referencial', monto_base)))
            igv = valor_referencial * Decimal('0.18')
            total_gravada = Decimal('0')
            total_exonerada = Decimal('0')
            total_inafecta = Decimal('0')
            total_gratuita = valor_referencial
        else:
            igv = monto_base * Decimal('0.18')
            total_gravada = monto_base
            total_exonerada = Decimal('0')
            total_inafecta = Decimal('0')
            total_gratuita = Decimal('0')
            
    elif codigo_afectacion.startswith('2'):  # Exonerado
        igv = Decimal('0')
        total_gravada = Decimal('0')
        total_exonerada = monto_base
        total_inafecta = Decimal('0')
        total_gratuita = Decimal('0')
        
    elif codigo_afectacion.startswith('3'):  # Inafecto
        igv = Decimal('0')
        total_gravada = Decimal('0')
        total_exonerada = Decimal('0')
        total_inafecta = monto_base
        total_gratuita = Decimal('0')
        
    elif codigo_afectacion == '40':  # Exportación
        igv = Decimal('0')
        total_gravada = Decimal('0')
        total_exonerada = monto_base
        total_inafecta = Decimal('0')
        total_gratuita = Decimal('0')
        
    else:
        # Por defecto, gravado
        igv = monto_base * Decimal('0.18')
        total_gravada = monto_base
        total_exonerada = Decimal('0')
        total_inafecta = Decimal('0')
        total_gratuita = Decimal('0')
    
    # Redondear a 2 decimales
    igv = igv.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_gravada = total_gravada.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_exonerada = total_exonerada.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_inafecta = total_inafecta.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_gratuita = total_gratuita.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return {
        'monto_base': monto_base,
        'igv': igv,
        'total_gravada': total_gravada,
        'total_exonerada': total_exonerada,
        'total_inafecta': total_inafecta,
        'total_gratuita': total_gratuita
    }

def calcular_percepcion(total_gravada, regimen_percepcion):
    """
    Calcula la percepción según el régimen
    """
    tasas_percepcion = {
        '01': Decimal('2.00'),  # 2% venta interna
        '02': Decimal('1.00'),  # 1% combustible
        '03': Decimal('0.50')   # 0.5% agente percepción
    }
    
    tasa = tasas_percepcion.get(regimen_percepcion, Decimal('0'))
    monto_percepcion = (total_gravada * tasa / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return {
        'tasa_percepcion': tasa,
        'monto_percepcion': monto_percepcion,
        'total_incluido_percepcion': total_gravada + monto_percepcion
    }

def calcular_totales_comprobante(items_data):
    """
    Calcula los totales del comprobante basado en todos los items
    """
    totales = {
        'total_gravada': Decimal('0'),
        'total_exonerada': Decimal('0'),
        'total_inafecta': Decimal('0'),
        'total_gratuita': Decimal('0'),
        'total_igv': Decimal('0')
    }
    
    for item in items_data:
        calculo_item = calcular_impuestos_item(item)
        totales['total_gravada'] += calculo_item['total_gravada']
        totales['total_exonerada'] += calculo_item['total_exonerada']
        totales['total_inafecta'] += calculo_item['total_inafecta']
        totales['total_gratuita'] += calculo_item['total_gratuita']
        totales['total_igv'] += calculo_item['igv']
    
    # Total a pagar (sin incluir gratuitas)
    totales['total_pagar'] = (
        totales['total_gravada'] + 
        totales['total_exonerada'] + 
        totales['total_inafecta'] + 
        totales['total_igv']
    )
    
    return totales