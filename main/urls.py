from django.urls import path
from . import views
from .constants import PAGES

app_name = 'main'
urlpatterns = [
    path(
        '',
        views.index,
        name=PAGES.INDEX_PAGE
    ),
]
