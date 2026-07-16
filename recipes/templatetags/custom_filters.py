import math

from django import template

from recipes.models import Unit

register = template.Library()

@register.filter
def display_quantity(value, unit):
    decimal_value = round(value - math.floor(value), 2)
    if decimal_value == 0 :
        return round(value) # Remove extra 0s

    if unit == Unit.CUP or unit == Unit.TABLESPOON or unit == Unit.TEASPOON:
        integer_value = round(value - decimal_value)
        integer_value = '' if integer_value == 0 else integer_value

        numerator = int(decimal_value * 10 ** len(str(decimal_value)))
        denominator = 10 ** len(str(decimal_value))
        gcd = math.gcd(numerator, denominator)
        return f"{integer_value} {numerator // gcd}/{denominator // gcd}"

    return value