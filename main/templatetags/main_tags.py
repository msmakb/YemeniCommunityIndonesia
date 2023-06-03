import uuid

from django import template
from django.conf import settings
from django.http import HttpRequest
from django.forms import ModelForm
from django.template.context import RenderContext

from main import menu_manager
from main.menu_manager import MenuItem

# Register template library
register = template.Library()


@register.simple_tag
def getFieldErrors(form: ModelForm, filed_name: str) -> list[str] | None:
    if form.errors:
        return form.errors.get(filed_name)
    else:
        return None


@register.simple_tag
def getUserMenus(request: HttpRequest) -> list[MenuItem]:
    return menu_manager.getUserMenus(request)


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


@register.simple_tag(name='cache_bust')
def cache_bust():

    if settings.DEBUG:
        version = uuid.uuid1()
    else:
        version = settings.PROJECT_VERSION

    return 'version={version}'.format(version=version)


@register.simple_tag
def setPage(path: str, page_number: int) -> str:
    if '?' in path:
        if 'page' in path:
            path = path.replace(
                f"page={path.split('page=')[-1].split('&')[0]}", f"page={page_number}")
        else:
            path += f'&page={page_number}'
    else:
        path += f'?page={page_number}'

    return path
