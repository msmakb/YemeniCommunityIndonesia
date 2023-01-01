from django.urls import path
from . import views
from .constants import PAGES

urlpatterns = [
    path(
        '',
        views.index,
        name=PAGES.INDEX_PAGE
    ),
    path(
        'Error/',
        views.unauthorized,
        name=PAGES.UNAUTHORIZED_PAGE
    ),
    path(
        'About/',
        views.about,
        name=PAGES.ABOUT_PAGE
    ),
    path(
        'Logout/',
        views.logoutUser,
        name=PAGES.LOGOUT
    ),
]
