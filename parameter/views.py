from typing import Any

from django.contrib import auth
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.utils import timezone

from main import constants
from main import messages as MSG
from main.utils import getClientIp

from .models import Parameter
from .service import getParameterValue


def systemSettings(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated and not request.user.is_superuser:
        raise Http404
    
    allowed_clients: dict[str, int] = cache.get(constants.CACHE.ALLOWED_ClIENTS)
    if not allowed_clients or not allowed_clients.get(getClientIp(request)):
        if request.method == constants.POST_METHOD:
            UserName: str = request.POST.get('user_name')
            Password: str = request.POST.get('password')
            user: User = auth.authenticate(
                request, username=UserName, password=Password)

            if user is not None:
                if user.is_superuser:
                    if not allowed_clients:
                        allowed_clients = {}
                    allowed_clients[getClientIp(request)] = timezone.now() + timezone.timedelta(minutes=5)
                    cache.set(
                        constants.CACHE.ALLOWED_ClIENTS,
                        allowed_clients,
                        constants.DEFAULT_CACHE_EXPIRE
                    )
                    return redirect(constants.PAGES.SETTINGS_PAGE)
                else:
                    return redirect(constants.PAGES.UNAUTHORIZED_PAGE)
            
        MSG.PAGE_REQUIRE_RE_LOGIN(request)
        return render(request, constants.TEMPLATES.LOGIN_TEMPLATE)
    
    expire_time: timezone.datetime = allowed_clients.get(getClientIp(request))
    if expire_time < timezone.now():
        MSG.PAGE_REQUIRE_RE_LOGIN(request)
        del allowed_clients[getClientIp(request)]
        cache.set(
            constants.CACHE.ALLOWED_ClIENTS,
            allowed_clients,
            constants.DEFAULT_CACHE_EXPIRE
        )
        return render(request, constants.TEMPLATES.LOGIN_TEMPLATE)
    
    parameters: QuerySet[Parameter] = Parameter.filter(
        access_type=constants.ACCESS_TYPE.ADMIN_ACCESS)

    if request.method == constants.POST_METHOD:
        for parameter in parameters:
            if parameter.getParameterType == constants.DATA_TYPE.BOOLEAN:
                current_value: bool = getParameterValue(parameter.name)
                if current_value and not request.POST.get(parameter.name):
                    parameter.value = "false"
                    parameter.save()
                elif not current_value and request.POST.get(parameter.name) and request.POST.get(parameter.name) == "true":
                    parameter.value = "true"
                    parameter.save()
            else:
                value: str = request.POST.get(parameter.name)
                if value and value != parameter.getValue:
                    parameter.value = value
                    try:
                        parameter.clean()
                        parameter.save()
                    except ValidationError as error:
                        MSG.ERROR_MESSAGE(request, error.args[0])
    
    context: dict[str, Any] = {'parameters': parameters}
    return render(request, constants.TEMPLATES.SYSTEM_SETTINGS_PAGE_TEMPLATE, context)
