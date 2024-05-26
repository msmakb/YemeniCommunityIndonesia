from django.urls import path
from . import views

from main.constants import PAGES

urlpatterns = [
    path(
        'Forms/',
        views.formsListPage,
        name=PAGES.FORMS_LIST_PAGE
    ),
    path(
        'Forms/<str:formId>/Responses/',
        views.formResponsesPage,
        name=PAGES.FORM_RESPONSES_PAGE
    ),
    path(
        'Forms/<str:responseId>/<str:questionId>/',
        views.downloadFormFile,
        name=PAGES.DOWNLOAD_FORM_FILE
    ),
    path(
        'Form/<str:formId>/',
        views.formPage,
        name=PAGES.FORM_PAGE
    ),
    path(
        'Form/<str:formId>/<str:messageType>/',
        views.formPage,
        name=PAGES.FORM_PAGE
    ),
]
