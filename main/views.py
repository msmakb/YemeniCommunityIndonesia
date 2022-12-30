from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

from . import constants

def index(request: HttpRequest) -> HttpResponse:
    context = {}
    return render(request, constants.TEMPLATES.INDEX_TEMPLATE, context)
