from django.urls import path
from . import views
from main.constants import PAGES

urlpatterns = [
    path(
        'Monitor/',
        views.monitorPage,
        name=PAGES.MONITOR_PAGE
    ),
    path(
        'Monitor/Activity-Log/',
        views.activityLogPage,
        name=PAGES.ACTIVITY_LOG_PAGE
    ),
    path(
        'Monitor/Block-List/',
        views.blockListPage,
        name=PAGES.BLOCK_LIST_PAGE
    ),
]
