from django import template

from items.models import Category

register = template.Library()


@register.inclusion_tag('items/categories.html')
def list_category(user):
    return {'cats': Category.objects.adult_control(user).all()}


@register.inclusion_tag('items/types.html')
def list_type():
    return {'types': ['Все товары', 'Книги', 'Журналы', 'Фигурки']}
