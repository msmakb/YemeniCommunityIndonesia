import json
import logging
from logging import Logger
from pathlib import Path
from typing import Any
import requests

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.db.models.query import QuerySet, Q
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from httplib2.error import ServerNotFoundError
from google.auth.exceptions import TransportError

from main import constants
from main import messages as MSG
from main.google import (FormResponse, GoogleForm, GoogleFormItem,
                         GoogleFormsService, GOOGLE_FORM_ITEM_TYPE,
                         GoogleAuthenticationError, HttpError)

from main.utils import generateRandomString
from member.models import Membership, Person

from .models import CustomFormItem, CustomFormResponse
from .forms import CustomFormItemForm


logger: Logger = logging.getLogger(constants.LOGGERS.FORMS)


def formsListPage(request: HttpRequest) -> HttpResponse:
    form_list: list[GoogleForm] = []
    custom_form_item_form: CustomFormItemForm = CustomFormItemForm()

    with GoogleFormsService() as googleFormsService:
        try:
            token: str = str(settings.BASE_DIR / 'data/google_client.json')
            googleFormsService.authenticate(token)
            if googleFormsService.credentials.valid:
                logger.info("Authenticated to Google Drive Successfully.")
            else:
                raise GoogleAuthenticationError(
                    "فشلت المصادقة على Google Drive.")

            formsService = googleFormsService.formService()

            if request.method == constants.POST_METHOD:
                formId: str = request.POST.get('formId')
                try:
                    if "savePermission" in request.POST:
                        email_address: str = request.POST.get('emailAddress')
                        formsService.addUserPermissionToForm(
                            formId, email_address)
                    elif "removePermission" in request.POST:
                        permissionId: str = request.POST.get('permissionId')
                        formsService.removeUserPermissionToForm(
                            formId, permissionId)
                    elif "createForm" in request.POST:
                        title: str = request.POST.get('title')
                        formsService.createForm(title)
                    elif "deleteForm" in request.POST:
                        formsService.deleteForm(formId)
                    elif "addCustomItem" in request.POST:
                        print(request.POST)
                        print(request.FILES)
                        itemType: str = request.POST.get('itemType')
                        title: str = request.POST.get('title')
                        description: str = request.POST.get('description')
                        required: bool = bool(request.POST.get('required'))
                        autofill: bool = bool(request.POST.get('autofill'))
                        isHidden: bool = bool(request.POST.get('isHidden'))
                        index: int = int(request.POST.get('fieldIndex'))
                        headerImg: UploadedFile | None = request.FILES.get(
                            'headerImg')

                        itemId: str = "itemId"
                        itemData: dict[str, Any] = {}

                        if itemType == constants.CUSTOM_FORM_ITEM_TYPE.EMAIL_ADDRESS:
                            itemId = 'email'
                            itemData = {
                                "required": required, "autoFillUserEmail": autofill,
                                "isHidden": isHidden, "distinctResponsePerEmail": False}
                        elif itemType == constants.CUSTOM_FORM_ITEM_TYPE.MEMBERSHIP:
                            itemId = 'membership'
                            itemData = {
                                "required": required, "autoFillUserMembership": autofill,
                                "isHidden": isHidden}
                        elif itemType == constants.CUSTOM_FORM_ITEM_TYPE.FILE_UPLOAD:
                            itemId = generateRandomString()  # TODO
                            itemData = {
                                "required": required, "accept": ".png, .jpeg, .jpg"}
                        elif itemType == constants.CUSTOM_FORM_ITEM_TYPE.HEADER_IMAGE:
                            form_headers_dir: Path = settings.MEDIA_ROOT / \
                                constants.MEDIA_DIR.FORMS_HEADERS_DIR

                            logger.info("Form Header DIR => %s" %
                                        str(form_headers_dir))
                            file_path: str = str(form_headers_dir /
                                                 (f"{formId}." + headerImg.name.split('.')[-1]))
                            default_storage.save(file_path, headerImg)
                            file_url = default_storage.url(file_path)

                            index = -1
                            itemId = constants.CUSTOM_FORM_ITEM_TYPE
                            title = constants.CUSTOM_FORM_ITEM_TYPE_AR[itemType]
                            itemData = {"src": file_url, "alt": "header"}

                        CustomFormItem.create(
                            formId=formId,
                            index=index,
                            itemId=itemId,
                            itemType=itemType,
                            title=title,
                            description=description,
                            itemData=itemData
                        )

                    elif "deleteCustomItem" in request.POST:
                        itemId = request.POST.get("deleteFieldId")
                        CustomFormItem.get(id=itemId).delete()
                except HttpError as error:
                    logger.exception(error)
                    try:
                        error_content: dict[str, Any] = json.loads(
                            error.content)
                        error_message: str = error_content['error']['message']
                        error_message = error_message.replace("\"", "").replace(
                            'Bad Request. User message:', '')
                        MSG.ERROR_MESSAGE(request, error_message)
                    except:
                        MSG.ERROR_MESSAGE(request, repr(error))

                return redirect(constants.PAGES.FORMS_LIST_PAGE)

            form_list = formsService.getFormsList()

            if None in form_list:
                form_list = filter(None, form_list)
                MSG.INVALID_FORMS(request)

            form_list = sorted(form_list,
                               key=lambda form: form.modifiedTime,
                               reverse=True)

            for i, form in enumerate(form_list):
                from django.forms.models import model_to_dict
                custom_form_items: list[CustomFormItem] = CustomFormItem.objects.filter(
                    formId=form.formId)

                for item in custom_form_items:
                    if item.itemType == constants.CUSTOM_FORM_ITEM_TYPE.HEADER_IMAGE:
                        continue

                    index: int = item.index
                    membership_field = GoogleFormItem(
                        **model_to_dict(item))
                    if index == -1:
                        form.items.append(membership_field)
                    else:
                        form.items.insert(index, membership_field)

                object.__setattr__(form, 'customItems', [
                    {
                        "id": item.id,
                        "type": item.itemType,
                        "title": item.title
                    } for item in custom_form_items])

                form_list[i].numberOfQuestions += len(list(filter(
                    lambda item: item.itemType != constants.CUSTOM_FORM_ITEM_TYPE.HEADER_IMAGE,
                    custom_form_items)))

        except (GoogleAuthenticationError, HttpError, TimeoutError,
                ServerNotFoundError, TransportError) as e:
            logger.exception(e)
            MSG.ERROR_MESSAGE(request, repr(e))

    context: dict[str, Any] = {"form_list": form_list,
                               "customFormItemForm": custom_form_item_form}
    return render(request, constants.TEMPLATES.FORMS_LIST_PAGE_TEMPLATE, context=context)


def formResponsesPage(request: HttpRequest, formId: str) -> HttpResponse:
    with GoogleFormsService() as googleFormsService:
        try:
            token: str = str(settings.BASE_DIR / 'data/google_client.json')
            googleFormsService.authenticate(token)
            if googleFormsService.credentials.valid:
                logger.info("Authenticated to Google Drive Successfully.")
            else:
                raise GoogleAuthenticationError(
                    "فشلت المصادقة على Google Drive.")

            formsService = googleFormsService.formService()
            form: GoogleForm = formsService.getForm(formId)
            i: int = 0  # enumerate will not work here
            for item in form.items:
                if item.itemType == GOOGLE_FORM_ITEM_TYPE.QUESTION_GROUP_ITEM:
                    form.items = form.items[:i] + \
                        item.questions + form.items[i:]
                    i += len(item.questions) - 1
                i += 1
            form_responses: list[FormResponse] = formsService.getFormResponses(
                formId, questions_order=[item.itemData.get("questionId")
                                         for item in filter(
                    lambda item: item.itemType in ("questionItem"), form.items)])
            # Remove empty answers
            form_responses = list(filter(
                lambda response: response.answers, form_responses))

        except (GoogleAuthenticationError, HttpError,
                ServerNotFoundError, TransportError) as e:
            logger.exception(e)

            MSG.ERROR_MESSAGE(request, repr(e))
    context: dict[str, Any] = {"form": form, "form_responses": form_responses,
                               "numberOfResponses": len(form_responses)}
    return render(request, constants.TEMPLATES.FORM_RESPONSES_PAGE_TEMPLATE, context=context)


def formPage(request: HttpRequest, formId: str, messageType: str | None = None) -> HttpResponse:
    form: GoogleForm = None
    require_login: bool = False
    require_membership: bool = False
    restricted: bool | None = False
    distinct_response_per_email: bool = False
    is_authenticated: bool = request.user.is_authenticated
    customFormItems: QuerySet = CustomFormItem.filter(
        formId=formId).values(
        'index', 'itemId', 'itemType',
        'title', 'description', 'itemData')

    if not messageType and customFormItems:
        for item in customFormItems:
            if item["itemType"] == constants.CUSTOM_FORM_ITEM_TYPE.EMAIL_ADDRESS:
                auto_fill_user_email: bool = item["itemData"].get(
                    "autoFillUserEmail", False)
                distinct_response_per_email = item["itemData"].get(
                    "distinctResponsePerEmail", False)
                require_login = auto_fill_user_email
            if item["itemType"] == constants.CUSTOM_FORM_ITEM_TYPE.MEMBERSHIP:
                auto_fill_user_email: bool = item["itemData"].get(
                    "autoFillUserMembership", False)
                require_membership = auto_fill_user_email
                if require_membership:
                    require_login = True

    if require_login and not is_authenticated:
        MSG.FORM_REQUIRE_LOGIN(request)
        form_page_url = reverse(
            constants.PAGES.FORM_PAGE, args=[formId])
        login_page_url = reverse(
            constants.PAGES.LOGIN_PAGE) + f'?nextPage={form_page_url}'
        return redirect(login_page_url)

    if distinct_response_per_email and not request.user.is_staff:
        restricted = CustomFormResponse.isExists(
            answers__email=Person.getUserData(
                request.user).get('email'))

    if restricted:
        return redirect(constants.PAGES.FORM_PAGE, formId, "restricted")

    if require_membership:
        if not request.user.is_staff and not Person.getUserData(request.user).get('has_membership'):
            context: dict[str, Any] = {
                "formTitle": form.info.title, "messageType": "requireMembership"}
            return render(request, constants.TEMPLATES.FORM_MESSAGE_PAGE_TEMPLATE, context=context)

    with GoogleFormsService() as googleFormsService:
        try:
            token: str = str(settings.BASE_DIR / 'data/google_client.json')
            googleFormsService.authenticate(token)
            if googleFormsService.credentials.valid:
                logger.info("Authenticated to Google Drive Successfully.")
            else:
                raise GoogleAuthenticationError(
                    "Failed to authenticate to google Drive/Forms.")

            formsService = googleFormsService.formService()

            if messageType:
                context: dict[str, Any] = {
                    "formTitle": formsService.getFormTitle(formId), "messageType": messageType}
                return render(request, constants.TEMPLATES.FORM_MESSAGE_PAGE_TEMPLATE, context=context)

            form = formsService.getForm(formId)

            # Check if form closed
            response = requests.head(form.responderUri, allow_redirects=True)
            if "/ClosedForm".lower() in response.url.lower():
                logger.info("Form Closed!")
                return redirect(constants.PAGES.FORM_PAGE, formId, "close")

            header_image: GoogleFormItem | None = None
            membership_field: GoogleFormItem | None = None
            if customFormItems:
                for item in customFormItems:
                    if item["itemType"] == constants.CUSTOM_FORM_ITEM_TYPE.HEADER_IMAGE:
                        header_image = GoogleFormItem(**item)
                        continue
                    if item["itemType"] == constants.CUSTOM_FORM_ITEM_TYPE.EMAIL_ADDRESS:
                        if is_authenticated:
                            if request.user.is_staff:
                                item["itemData"]["userEmail"] = request.user.email
                            else:
                                item["itemData"]["userEmail"] = Person.getUserData(
                                    request.user).get('email')

                    index: int = item['index']
                    membership_field = GoogleFormItem(**item)
                    if index == -1:
                        form.items.append(membership_field)
                    else:
                        form.items.insert(index, membership_field)

            if request.method == constants.POST_METHOD:
                if request.user.is_staff and require_login:
                    MSG.ERROR_MESSAGE(request, "هذا النموذج مقيد للأعضاء فقط."
                                      + " كمسؤول، يمكنك عرض النموذج لتحريره والتحقق منه ولا يمكنك إرسال رد")
                    return redirect(constants.PAGES.FORM_PAGE, form.formId)

                if distinct_response_per_email:
                    restricted = CustomFormResponse.isExists(
                        answers__email=request.POST.get("email"))

                if restricted:
                    return redirect(constants.PAGES.FORM_PAGE, formId, "restricted")

                if membership_field:
                    membership_card_number: str = str(
                        request.POST.get("membership"))
                    if membership_card_number:
                        if not Membership.isExists(card_number=membership_card_number):
                            MSG.ERROR_MESSAGE(
                                request, "رقم بطاقة العضوية غير صالح")
                            return redirect(constants.PAGES.FORM_PAGE, form.formId)
                    else:
                        if membership_field.itemData["required"]:
                            MSG.ERROR_MESSAGE(
                                request, "يرجى إدخال رقم بطاقة العضوية")
                            return redirect(constants.PAGES.FORM_PAGE, form.formId)

                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                url: str = f"https://docs.google.com/forms/u/0/d/e/{form.responserUriId}/formResponse"
                data: bytes = b''
                for field_name, value in request.POST.items():
                    if field_name.startswith("entry."):
                        data += f"{field_name}={value}&".encode("utf-8")
                data += b"pageHistory="
                for i in range(form.numberOfPages):
                    data += f"{i},".encode("utf-8")
                data = data[:-1]
                logger.info("request  => %s" % data)
                response = requests.post(url, data=data, headers=headers)
                logger.info("response status code => %s" %
                            str(response.status_code))

                if response.status_code == 200:
                    responseId: str = sorted(formsService.getFormResponses(formId),
                                             key=lambda response: response.createTime,
                                             reverse=True)[0].responseId
                    custom_form_response_answers: dict[str, Any] = {}
                    email: str = request.POST.get("email")
                    membership: str = request.POST.get("membership")
                    if email:
                        custom_form_response_answers["email"] = email
                    if membership:
                        custom_form_response_answers["membership"] = membership

                    files: MultiValueDict[str, UploadedFile] = request.FILES
                    form_files_dir: Path = settings.MEDIA_ROOT / \
                        constants.MEDIA_DIR.FORMS_FILES_DIR / formId / responseId

                    logger.info("Form DIR => %s" % str(form_files_dir))
                    for key, file in files.items():
                        file_path: str = str(form_files_dir /
                                             (key + "." + file.name.split('.')[-1]))
                        default_storage.save(file_path, file)
                        file_url = default_storage.url(file_path)
                        custom_form_response_answers[key] = file_url

                    CustomFormResponse.create(
                        responseId=responseId,
                        answers=custom_form_response_answers
                    )

                    return redirect(constants.PAGES.FORM_PAGE, formId, "success")
                else:
                    MSG.ERROR_MESSAGE(request, "حدث خطأ ما أثناء إرسال ردك."
                                      + " إذا تكرر هذا الخطأ، يرجى مراجعة الدعم الفني.")

            if require_membership:
                if request.user.is_staff:
                    for item in form.items:
                        if item.itemType == constants.CUSTOM_FORM_ITEM_TYPE.MEMBERSHIP:
                            item.itemData["userMembership"] = "YEMXXXXXXX"
                else:
                    user_data: dict[str, Any] = Person.getUserData(
                        request.user)
                    for item in form.items:
                        if item.itemType == constants.CUSTOM_FORM_ITEM_TYPE.MEMBERSHIP:
                            item.itemData["userMembership"] = user_data.get(
                                'membership_card_number')

            items: list[GoogleFormItem] = []
            current_section: GoogleFormItem = GoogleFormItem(
                itemId="start", title=form.info.title,
                itemType=GOOGLE_FORM_ITEM_TYPE.PAGE_BREAK_ITEM)
            current_questions_list: list[GoogleFormItem] = []
            for index, item in enumerate(form.items):
                # format description template
                if item.description:
                    item_description_template: str = ""
                    for line in item.description.splitlines():
                        indentation: str = "   "
                        indented: str = ""
                        while line.startswith(indentation):
                            if indented:
                                if indented.endswith("1"):
                                    indented = "indented-paragraph-2"
                                else:
                                    indented = "indented-paragraph-3"
                                    break
                            else:
                                indented = "indented-paragraph-1"

                            line = line[3:]
                        item_description_template += f'<h6 class="fw-light lh-base {indented}">{line}</h6>'
                        indented = ""
                    item.description = item_description_template

                if item.itemType == GOOGLE_FORM_ITEM_TYPE.PAGE_BREAK_ITEM:
                    if index != 0:
                        current_section.questions = current_questions_list
                        items.append(current_section)
                        current_questions_list = []
                    current_section = item
                elif item.itemType in GOOGLE_FORM_ITEM_TYPE \
                        or item.itemType in constants.CUSTOM_FORM_ITEM_TYPE_AR.keys():
                    current_questions_list.append(item)
                else:
                    raise NotImplementedError("Unsupported Item type.")
            else:
                current_section.questions = current_questions_list
                items.append(current_section)

            if form.info.description:
                form_description_template: str = ""
                for line in form.info.description.splitlines():
                    indentation: str = "   "
                    indented: str = ""
                    while line.startswith(indentation):
                        if indented:
                            if indented.endswith("1"):
                                indented = "indented-paragraph-2"
                            else:
                                indented = "indented-paragraph-3"
                                break
                        else:
                            indented = "indented-paragraph-1"

                        line = line[3:]
                    form_description_template += f'<h6 class="fw-light lh-base {indented}">{line}</h6>'
                    indented = ""
                form.info.description = form_description_template
            form.items = items

        except Exception as e:
            form = None
            logger.exception(e)

    context: dict[str, Any] = {"form": form, "head_img": header_image}
    return render(request, constants.TEMPLATES.FORM_PAGE_TEMPLATE, context=context)
