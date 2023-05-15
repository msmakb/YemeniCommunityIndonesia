from typing import Any

from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.http.request import QueryDict
from django.shortcuts import redirect, render, get_object_or_404

from main import constants
from main import messages as MSG
from main.utils import Pagination

from member.models import Person

from .models import Attachment, EmailBroadcast
from .forms import AttachmentForm, EmailBroadcastForm

def emailBroadcastPage(request: HttpRequest) -> HttpResponse:
    queryset: QuerySet[EmailBroadcast] = EmailBroadcast.getAllOrdered(
        'created',
        reverse=True
    )
    page: str = request.GET.get('page')
    pagination = Pagination(queryset, int(page) if page is not None else 1)
    page_obj: QuerySet[Person] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {'page_obj': page_obj, 'is_paginated': is_paginated,}
    return render(request, constants.TEMPLATES.BROADCAST_PAGE_TEMPLATE, context)


def detailBroadcastPage(request: HttpRequest, pk: str) -> HttpResponse:
    broadcast: EmailBroadcast = get_object_or_404(EmailBroadcast, pk=pk)
    attachments: QuerySet[Attachment] | None = None
    if broadcast.has_attachment:
        attachments = Attachment.filter(email_broadcast=broadcast)

    if request.method == constants.POST_METHOD:
        if "test-broadcast" in request.POST:
            email: str = request.POST.get('email')
            try:
                broadcast.testBroadcast(email)
            except Exception as e:
                error_message = str(e.args[0]) if e.args else "Unknown error"
                MSG.ERROR_MESSAGE(request, error_message)
        elif "push-broadcast" in request.POST:
            try:
                broadcast.broadcast()
            except Exception as e:
                error_message = str(e.args[0]) if e.args else "Unknown error"
                MSG.ERROR_MESSAGE(request, error_message)

    context: dict[str, Any] = {'broadcast': broadcast, 'attachments': attachments}
    return render(request, constants.TEMPLATES.DETAIL_BROADCAST_PAGE_TEMPLATE, context)


def addBroadcastPage(request: HttpRequest) -> HttpResponse:
    broadcastForm = EmailBroadcastForm()
    if request.method == constants.POST_METHOD:
        
        filter_data: dict[str, Any] = {
            'is_validated': True
        }
        match request.POST.get('to'):
            case 'MEMBERS':
                filter_data['membership__isnull'] = False
            case 'NON-MEMBERS':
                filter_data['membership__isnull'] = True
            case 'STUDENTS':
                filter_data['job_title'] = constants.JOB_TITLE.STUDENT

        email_list = list(
            Person.filter(**filter_data).values_list('email', flat=True))

        updated_post: QueryDict = request.POST.copy()
        updated_post.update({'email_list': str(email_list)})
        broadcastForm = EmailBroadcastForm(updated_post)
        if broadcastForm.is_valid():
            broadcastForm.save()
            MSG.ADD_BROADCAST(request)
            return redirect(constants.PAGES.BROADCAST_PAGE)

    context: dict[str, Any] = {'broadcastForm': broadcastForm}
    return render(request, constants.TEMPLATES.ADD_UPDATE_BROADCAST_PAGE_TEMPLATE, context)


def updateBroadcastPage(request: HttpRequest, pk: str) -> HttpResponse:
    broadcast: EmailBroadcast = get_object_or_404(EmailBroadcast, pk=pk)
    broadcast.email_list = None
    broadcastForm = EmailBroadcastForm(instance=broadcast)
    if request.method == constants.POST_METHOD:
        
        filter_data: dict[str, Any] = {
            'is_validated': True
        }
        match request.POST.get('to'):
            case 'MEMBERS':
                filter_data['membership__isnull'] = False
            case 'NON-MEMBERS':
                filter_data['membership__isnull'] = True
            case 'STUDENTS':
                filter_data['job_title'] = constants.JOB_TITLE.STUDENT

        email_list = list(
            Person.filter(**filter_data).values_list('email', flat=True))

        updated_post: QueryDict = request.POST.copy()
        updated_post.update({'email_list': str(email_list)})
        broadcastForm = EmailBroadcastForm(updated_post, instance=broadcast)
        if broadcastForm.is_valid():
            broadcastForm.save()
            MSG.UPDATE_BROADCAST(request)
            return redirect(constants.PAGES.DETAIL_BROADCAST_PAGE, broadcast.id)

    context: dict[str, Any] = {'broadcastForm': broadcastForm, 'broadcastId': broadcast.id}
    return render(request, constants.TEMPLATES.ADD_UPDATE_BROADCAST_PAGE_TEMPLATE, context)


def addAttachmentPage(request: HttpRequest, pk: str) -> HttpResponse:
    attachmentForm = AttachmentForm()
    if request.method == constants.POST_METHOD:
        updated_post: QueryDict = request.POST.copy()
        updated_post.update({'email_broadcast': EmailBroadcast.get(pk=pk)})
        attachmentForm = AttachmentForm(updated_post, request.FILES)
        if attachmentForm.is_valid():
            attachmentForm.save()
            EmailBroadcast.filter(pk=pk).update(has_attachment=True)
            MSG.ADD_ATTACHMENT(request)
            return redirect(constants.PAGES.DETAIL_BROADCAST_PAGE, pk)
        else:
            for messages in attachmentForm.errors.get('__all__'):
                MSG.ERROR_MESSAGE(request, messages)

    context: dict[str, Any] = {'attachmentForm': attachmentForm, 'broadcastId': pk}
    return render(request, constants.TEMPLATES.ADD_ATTACHMENT_PAGE_TEMPLATE, context)


def deleteAttachment(request: HttpRequest, pk: str) -> HttpResponse:
    attachment: Attachment = get_object_or_404(Attachment, pk=pk)
    broadcastId: int = attachment.email_broadcast.id
    attachment.delete()

    if not Attachment.filter(email_broadcast__id=broadcastId).exists():
        EmailBroadcast.filter(pk=broadcastId).update(has_attachment=False)

    MSG.DELETE_ATTACHMENT(request)
    return redirect(constants.PAGES.DETAIL_BROADCAST_PAGE, broadcastId)
