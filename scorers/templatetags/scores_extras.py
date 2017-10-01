from django import template

register = template.Library()


@register.filter
def dec(value, arg):
    return value - arg


@register.filter
def place(scorers: list, index: int) -> int:
    goals = scorers[index].total_goals
    while index > 0 and goals == scorers[index - 1].total_goals:
        index -= 1
    return index+1
