from django import template
from django.template.context import RenderContext
from django.forms import ModelForm

# Register template library
register = template.Library()


@register.simple_tag
def getFieldErrors(form: ModelForm, filed_name: str) -> list[str] | None:
    if form.errors:
        return form.errors.get(filed_name)
    else:
        return None


@register.filter(name="rng")
def rng(number):
    return range(number)


@register.simple_tag(takes_context=True)
def isVarExists(context: RenderContext, name: str) -> bool:
    dicts: dict = context.dicts
    if dicts:
        for d in dicts:
            if name in d:
                return True
    return False
