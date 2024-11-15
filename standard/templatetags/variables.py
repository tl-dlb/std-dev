from django import template
register = template.Library()


@register.simple_tag
def btn_action_class():
    return "btn btn-success mb-3 me-3 px-4"

@register.simple_tag
def btn_submit_class():
    return "btn btn-success my-3 px-4"