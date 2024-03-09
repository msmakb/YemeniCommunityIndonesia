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
    path(
        '422f0ac8d0a24d9f8486d5a3b3f5c8e6874bbc9e4a354d6c92221baadb95d8c73b564ff9fbd948a989d3b9946f0471dce3606505671f42949a3dfb8b4f2ff27b3bfb647e5da64ef89c28eba87aee6c3e/',
        views.whatsappWebhook
    ),
]
