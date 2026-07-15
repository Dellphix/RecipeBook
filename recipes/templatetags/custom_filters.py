from fractions import Fraction

from django import template

from recipes.models import Unit

register = template.Library()

@register.filter
def display_quantity(value, unit):
    decimal_value = round(value) - value
    if decimal_value == 0 :
        return round(value)

    if unit == Unit.CUP:
        integer_value = round(value - decimal_value)
        return f"{integer_value} {Fraction(decimal_value)}"

    return value