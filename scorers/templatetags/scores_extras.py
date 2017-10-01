from django import template

register = template.Library()


@register.filter
def dec(value, arg):
    return value - arg


@register.filter
def place(scores: list, index: int) -> int:
    goals = scores[index]['total']
    while index > 0 and goals == scores[index - 1]['total']:
        index -= 1
    return index+1
