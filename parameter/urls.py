from django.urls import path
from . import views
from main.constants import PAGES

urlpatterns = [
    path(
        'Settings/',
        views.systemSettings,
        name=PAGES.SETTINGS_PAGE
    ),
]
