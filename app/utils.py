"""
Módulo de utilidades compartidas
Funciones auxiliares utilizadas en múltiples partes de la aplicación
"""


def validar_rut_chileno(rut_raw: str) -> bool:
    """
    Valida un RUT chileno básico:
    - Acepta con o sin puntos, con guion.
    - Verifica dígito verificador.
    """
    if not rut_raw:
        return False

    rut = rut_raw.replace('.', '').replace('-', '').strip().upper()
    if len(rut) < 2:
        return False

    cuerpo, dv = rut[:-1], rut[-1]
    if not cuerpo.isdigit():
        return False

    # Cálculo dígito verificador
    suma = 0
    multiplicador = 2
    for d in reversed(cuerpo):
        suma += int(d) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2

    resto = suma % 11
    dv_calc = 11 - resto
    if dv_calc == 11:
        dv_calc_str = '0'
    elif dv_calc == 10:
        dv_calc_str = 'K'
    else:
        dv_calc_str = str(dv_calc)

    return dv == dv_calc_str
