from django import template

register = template.Library()

@register.simple_tag
def rating_color(rating):
    try:
        rating = float(str(rating).replace(',', '.'))
    except:
        return ''
    if 1 <= rating < 2:
        return 'color: #8B0000; font-weight: bold;'
    elif 2 <= rating < 3:
        return 'color: #FF7F7F;'
    elif 3 <= rating < 4:
        return 'color: #9ACD32;'
    elif 4 <= rating < 4.5:
        return 'color: #2E8B57;'
    elif 4.5 <= rating <= 5:
        return 'color: #006400; font-weight: bold;'
    return ''