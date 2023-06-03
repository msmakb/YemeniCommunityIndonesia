from django.urls import path

from main.constants import PAGES

from . import views

urlpatterns = [
    path(
        'Broadcast/',
        views.emailBroadcastPage,
        name=PAGES.BROADCAST_PAGE
    ),
    path(
        'Broadcast/detail/<str:pk>/',
        views.detailBroadcastPage,
        name=PAGES.DETAIL_BROADCAST_PAGE
    ),
    path(
        'Broadcast/Add/',
        views.addBroadcastPage,
        name=PAGES.ADD_BROADCAST_PAGE
    ),
    path(
        'Broadcast/update/<str:pk>/',
        views.updateBroadcastPage,
        name=PAGES.UPDATE_BROADCAST_PAGE
    ),
    path(
        'Broadcast/Attachment/Add/<str:pk>/',
        views.addAttachmentPage,
        name=PAGES.ADD_ATTACHMENT_PAGE
    ),
    path(
        'Broadcast/Attachment/Delete/<str:pk>/',
        views.deleteAttachment,
        name=PAGES.DELETE_ATTACHMENT_PAGE
    ),
    path(
        'Broadcast/api/<str:pk>/<str:status>/',
        views.updateSpecialBroadcastEmailAttacheMembershipCard,
        name=PAGES.UPDATE_ATTACH_MEMBERSHIP_CARD_API
    ),
]
