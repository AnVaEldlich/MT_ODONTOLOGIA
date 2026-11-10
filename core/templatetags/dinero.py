from decimal import Decimal, ROUND_HALF_UP

from django import template

register = template.Library()


@register.filter
def pesos(valor):
    """Miles con punto, sin decimales: 80000 → 80.000."""
    if valor is None or valor == "":
        return ""
    entero = int(Decimal(valor).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return f"{entero:,}".replace(",", ".")
