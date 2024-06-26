from django.forms.models import model_to_dict
import json
import os
from typing import Any, Callable

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import EmptyResultSet
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.db.models import Subquery, OuterRef
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from company_user.models import CompanyUser

from main import constants
from main import messages as MSG
from main.image_processing import ImageProcessor, ImageProcessingError
from main.models import AuditEntry
from parameter.service import getParameterValue
from main.utils import (Pagination, getClientIp, getUserAgent,
                        exportAsCsvExcel, logUserActivity, sendEmail)

from .models import (Academic, Address, Membership,
                     FamilyMembers, FamilyMembersChild,
                     FamilyMembersWife, Person)
from .forms import (AddPersonForm, AcademicForm,
                    AddressForm, FamilyMembersForm)
from .filters import PersonFilter


def staffDashboard(request: HttpRequest) -> HttpResponse:
    if request.user.is_superuser:
        user_role: str = "مستخدم متميز"
    else:
        user_role: str = CompanyUser.filter(
            user=request.user).values('role__name').first()['role__name']
    context: dict[str, Any] = {'user_role': user_role}
    return render(request, constants.TEMPLATES.DASHBOARD_TEMPLATE, context)


def membersPage(request: HttpRequest, currentPage: str) -> HttpResponse:
    waiting: int = Person.countFiltered(is_validated=False)
    is_validated: bool | None = None
    match currentPage.lower():
        case "list":
            is_validated = True
        case "approve":
            is_validated = False
        case _:
            raise Http404

    queryset: QuerySet[Person] = Person.objects.select_related(
        'address', 'membership').filter(is_validated=is_validated)

    personFilter: PersonFilter = PersonFilter(request.GET, queryset=queryset)
    queryset = personFilter.qs

    page: str = request.GET.get('page')
    pagination = Pagination(queryset, int(page) if page is not None else 1)
    page_obj: QuerySet[Person] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    if request.method == constants.POST_METHOD:
        fields: list[str] = [
            'name_ar',
            'name_en',
            'gender',
            'place_of_birth',
            'date_of_birth',
            'call_number',
            'whatsapp_number',
            'email',
            'job_title',
            'period_of_residence',
            'passport_number',
            'academic__academic_qualification',
            'academic__school',
            'academic__major',
            'academic__semester',
            'address__street_address',
            'address__district',
            'address__city',
            'address__province',
            'address__postal_code',
            'membership__card_number',
            'membership__membership_type',
            'membership__issue_date',
            'membership__expire_date',
            'family_members__family_name',
            'family_members__member_count'
        ]
        labels_to_change: dict[str, str] = {
            'name_ar': 'الاسم بالعربي',
            'name_en': 'الاسم بالإنجليزي',
            'gender': 'الجنس',
            'place_of_birth': 'مكان الميلاد',
            'date_of_birth': 'تاريخ الميلاد',
            'call_number': 'رقم الهاتف (اتصال)',
            'whatsapp_number': 'رقم الواتساب',
            'email': 'البريد الإلكتروني',
            'job_title': 'المسمى الوظيفي',
            'period_of_residence': 'فترة الإقامة في إندونيسيا',
            'passport_number': 'رقم جواز',
            'academic__academic_qualification': 'المؤهل العلمي',
            'academic__school': 'أسم الجامعة / معهد / مدرسة',
            'academic__major': 'التخصص الدراسي',
            'academic__semester': 'الفصل الدراسي',
            'address__street_address': 'عنوان الشارع',
            'address__district': 'المنطقة',
            'address__city': 'المدينة',
            'address__province': 'الولاية',
            'address__postal_code': 'الرمز البريدي',
            'membership__card_number': 'رقم البطاقة',
            'membership__membership_type': 'نوع العضوية',
            'membership__issue_date': 'تاريخ الإصدار',
            'membership__expire_date': 'تاريخ الانتهاء',
            'family_members__family_name': 'الأسم العائلي',
            'family_members__member_count': 'عدد أفراد الأسرة التي يعيلها في إندونيسيا'
        }
        values_to_change: dict[str, Callable] = {
            'gender': lambda gender: constants.GENDER_AR[int(gender)],
            'job_title': lambda job_title: constants.JOB_TITLE_AR[int(job_title)],
            'period_of_residence': lambda period_of_residence: constants.PERIOD_OF_RESIDENCE_AR[int(period_of_residence)],
            'academic__academic_qualification': lambda academic_qualification: constants.ACADEMIC_QUALIFICATION_AR[int(academic_qualification)],
            'membership__membership_type': lambda membership_type: constants.MEMBERSHIP_TYPE_AR[int(membership_type)],
        }
        try:
            file: HttpResponse = exportAsCsvExcel(
                queryset=queryset,
                fields=fields,
                labels_to_change=labels_to_change,
                values_to_change=values_to_change,
                sheet_type=request.POST.get('export_type')
            )
            return file
        except EmptyResultSet:
            MSG.NO_DATA(request)

    context: dict[str, Any] = {
        'waiting': waiting,
        'page_obj': page_obj,
        'is_paginated': is_paginated,
        'currentPage': currentPage,
        'personFilter': personFilter
    }
    return render(request, constants.TEMPLATES.MEMBERS_PAGE_TEMPLATE, context)


def memberPage(request: HttpRequest) -> HttpResponse:
    try:
        person: Person = Person.get(account=request.user.id)
        if not person:
            MSG.SOMETHING_WRONG(request)
            return redirect(constants.PAGES.LOGOUT)
    except Person.DoesNotExist:
        MSG.SOMETHING_WRONG(request)
        return redirect(constants.PAGES.LOGOUT)

    context: dict[str, Any] = {
        'person': person
    }
    return render(request, constants.TEMPLATES.MEMBER_PAGE_TEMPLATE, context)


def downloadMembershipCard(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect(constants.PAGES.UNAUTHORIZED_PAGE)
    try:
        pk: int = Person.getUserData(request.user).get('membership_id')
        membership: Membership = Membership.get(id=pk)
        person: Person = Person.get(account=request.user)
    except (Membership.DoesNotExist, Person.DoesNotExist):
        raise Http404

    if person.membership != membership:
        return redirect(constants.PAGES.UNAUTHORIZED_PAGE)

    file_path = membership.membership_card.path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type="image/jpg")
            response['Content-Disposition'] = f'inline; filename={membership.card_number}.jpg'
            return response
    raise Http404


def memberFormPage(request: HttpRequest) -> HttpResponse:
    if not getParameterValue(constants.PARAMETERS.OPEN_MEMBER_REGISTRATION_FORM):
        MSG.MEMBER_FORM_CLOSE(request)
        return redirect(constants.PAGES.INDEX_PAGE)

    person_form: AddPersonForm = AddPersonForm()
    academic_form: AcademicForm = AcademicForm()
    address_form: AddressForm = AddressForm()
    family_members_form: FamilyMembersForm = FamilyMembersForm()

    if request.method == constants.POST_METHOD:
        is_request_membership: bool = False
        validFamilyMembers: bool = True
        isAgree: bool = True
        partner_list: list[tuple[str, int]] = []
        children_list: list[tuple[str, int]] = []
        person_form = AddPersonForm(request.POST, request.FILES)
        academic_form = AcademicForm(request.POST)
        address_form = AddressForm(request.POST)
        family_members_form = FamilyMembersForm(request.POST)

        for i in range(4):
            name: str = request.POST.get(f"partner_name{i}")
            age: str = request.POST.get(f"partner_age{i}")
            if age:
                try:
                    int(age)
                except ValueError:
                    validFamilyMembers = False
                    MSG.SOMETHING_WRONG(request)
            if name:
                partner_list.append((name, None if not age else int(age)))

        for i in range(10):
            name: str = request.POST.get(f"child_name{i}")
            age: str = request.POST.get(f"child_age{i}")
            if age:
                try:
                    int(age)
                except ValueError:
                    validFamilyMembers = False
                    MSG.SOMETHING_WRONG(request)
            if name:
                children_list.append((name, None if not age else int(age)))

        validations: tuple[bool, ...] = (
            person_form.is_valid(),
            academic_form.is_valid(),
            address_form.is_valid(),
            family_members_form.is_valid(),
            validFamilyMembers,
            isAgree
        )

        if request.POST.get('membership') == "1":
            if "agreed" in request.POST.getlist("agree"):
                is_request_membership = True
            else:
                MSG.TERMS_MUST_AGREE(request)
                isAgree = False

        if person_form.errors.get("__all__"):
            person_form.add_error(
                "photograph", person_form.errors.get("__all__"))

        if all(validations):
            academic_form.save()
            academic: Academic = Academic.getLastInsertedObject()
            address_form.save()
            address: Address = Address.getLastInsertedObject()
            family_members_form.save()
            family_members: FamilyMembers = FamilyMembers.getLastInsertedObject()
            person_form.save()
            person: Person = Person.getLastInsertedObject()
            person.academic = academic
            person.address = address
            person.family_members = family_members
            person.is_request_membership = is_request_membership
            person.save()

            for name, age in partner_list:
                FamilyMembersWife.create(
                    family_members=family_members,
                    name=name,
                    age=age
                )
            for name, age in children_list:
                FamilyMembersChild.create(
                    family_members=family_members,
                    name=name,
                    age=age
                )

            AuditEntry.create(ip=getClientIp(request),
                              user_agent=getUserAgent(request),
                              action=constants.ACTION.MEMBER_FORM_POST,
                              username=request.user)

            MEMBER_POST_COUNT_CACHED_KEY: str = "MEMBER_FORM:%s" % getClientIp(
                request)
            membership_form_posts_count: int = cache.get(
                MEMBER_POST_COUNT_CACHED_KEY, 0)
            cache.set(
                MEMBER_POST_COUNT_CACHED_KEY,
                membership_form_posts_count + 1,
                constants.DEFAULT_CACHE_EXPIRE * getParameterValue(
                    constants.PARAMETERS.ALLOWED_LOGGED_IN_ATTEMPTS_RESET)
            )

            if settings.MAILING_IS_ACTIVE:
                try:
                    email: EmailMessage = EmailMessage(
                        "شكراً على المساهمة",
                        render_to_string(
                            constants.TEMPLATES.THANK_YOU_EMAIL_TEMPLATE,
                            {
                                "name": person.name_ar,
                                "is_request_membership": person.is_request_membership
                            }
                        ),
                        settings.EMAIL_HOST_USER,
                        [person.email]
                    )
                    email.fail_silently = False
                    sendEmail(email)
                except Exception:
                    pass

            return redirect(constants.PAGES.THANK_YOU_PAGE)

        else:
            MSG.FIX_ERRORS(request)

    context: dict[str, Any] = {
        'person_form': person_form,
        'academic_form': academic_form,
        'address_form': address_form,
        'family_members_form': family_members_form,
    }
    return render(request, constants.TEMPLATES.MEMBER_FORM_TEMPLATE, context)


def detailMember(request: HttpRequest, pk: str) -> HttpResponse:
    person: Person = get_object_or_404(Person, id=pk)
    partners: FamilyMembersWife = FamilyMembersWife.filter(
        family_members=person.family_members)
    children: FamilyMembersChild = FamilyMembersChild.filter(
        family_members=person.family_members)

    if request.method == constants.POST_METHOD:
        if person.is_validated:
            MSG.SOMETHING_WRONG(request)
            return redirect(constants.PAGES.LOGOUT)

        passport_number: str = request.POST.get("passportNumber")
        if "generate" in request.POST:
            membership_type: int = None
            if request.POST.get('membership') != "1":
                MSG.ACCEPT_MEMBERSHIP(request)
                return redirect(constants.PAGES.DETAIL_MEMBER_PAGE, person.id)

            try:
                membership_type = int(
                    request.POST.get('membership_type'))
                constants.MEMBERSHIP_TYPE_AR[membership_type]
            except IndexError:
                MSG.SOMETHING_WRONG(request)
                return redirect(constants.PAGES.DETAIL_MEMBER_PAGE, person.id)
            except ValueError:
                MSG.SOMETHING_WRONG(request)
                return redirect(constants.PAGES.DETAIL_MEMBER_PAGE, person.id)

            idNum: str = str(person.id)
            membership: Membership = Membership()
            membership.card_number = getParameterValue(
                constants.PARAMETERS.THREE_CHARACTER_PREFIX_FOR_MEMBERSHIP) + ('0' * (7 - len(idNum))) + idNum
            membership.membership_type = membership_type
            membership.expire_date = (timezone.now().date().replace(year=timezone.now(
            ).year + getParameterValue(constants.PARAMETERS.MEMBERSHIP_EXPIRE_PERIOD)))
            try:
                image_io: bytes = ImageProcessor.generateMembershipCardImage(
                    person.photograph,
                    person.name_ar,
                    person.name_en,
                    person.address.getCityAr,
                    person.address.city,
                    membership.getMembershipType,
                    membership.getMembershipTypeEnglish,
                    str(timezone.now().date()),
                    str(membership.expire_date),
                    membership.card_number
                )
                membership.membership_card = ContentFile(
                    image_io, "membership.jpg")
            except ImageProcessingError as error:
                MSG.SOMETHING_WRONG(request)
                MSG.ERROR_MESSAGE(request, str(error))
                MSG.SCREENSHOT(request)
                return redirect(constants.PAGES.DETAIL_MEMBER_PAGE, person.id)

            if person.membership:
                person.membership.delete()

            membership.save()
            person.membership = membership
            person.save()

            return redirect(constants.PAGES.DETAIL_MEMBER_PAGE, person.id)

        elif "approve" in request.POST:
            try:
                int(passport_number)
            except ValueError:
                MSG.PASSPORT_NUMBER_ERROR(request)
                return redirect(constants.PAGES.DETAIL_MEMBER_PAGE, person.id)

            if Person.isExists(passport_number=passport_number) and person.passport_number != passport_number:
                MSG.PASSPORT_NUMBER_EXISTS(request)
                return redirect(constants.PAGES.DETAIL_MEMBER_PAGE, person.id)

            if request.POST.get('membership') == "1":
                if not person.membership:
                    MSG.MEMBERSHIP_MUST_GENERATED(request)
                    return redirect(constants.PAGES.DETAIL_MEMBER_PAGE, person.id)
            elif person.membership:
                membership = person.membership
                person.membership = None
                person.save()
                membership.delete()

            if passport_number != None:
                person.passport_number = passport_number
                person.is_validated = True
                person.account = User.objects.create_user(
                    username=passport_number,
                    password=str(person.date_of_birth).replace('-', ''),
                    first_name=person.name_ar.split(' ')[0],
                    last_name=person.name_ar.split(' ')[-1])
                person.save()

                if settings.MAILING_IS_ACTIVE:
                    email: EmailMessage = EmailMessage(
                        "قَبُول تسجيل الجالية اليمنية في إندونيسيا",
                        render_to_string(
                            constants.TEMPLATES.APPROVE_MEMBER_EMAIL_TEMPLATE,
                            {
                                "name": person.name_ar,
                                "hasMembership": True if person.membership else False,
                                "username": person.passport_number,
                                "password": str(person.date_of_birth).replace('-', '')
                            }
                        ),
                        settings.EMAIL_HOST_USER,
                        [person.email]
                    )
                    email.fail_silently = False
                    if person.membership:
                        email.attach(
                            person.membership.card_number + '.jpg',
                            person.membership.membership_card.file.read(),
                            'image/jpeg'
                        )
                    sendEmail(email)
                    MSG.APPROVE_RECORD(request)
                    logUserActivity(request, constants.ACTION.ACCEPT_MEMBER,
                                    f"اعتماد سجل العضو ({person.name_ar}) "
                                    + f"من قِبل {request.user.get_full_name()}")
                return redirect(constants.PAGES.MEMBERS_PAGE, "Approve")
            else:
                MSG.PASSPORT_NUMBER_ERROR(request)
                return redirect(constants.PAGES.DETAIL_MEMBER_PAGE, person.id)
        elif "decline" in request.POST:
            try:
                int(passport_number)
            except ValueError:
                MSG.PASSPORT_NUMBER_ERROR(request)
                return redirect(constants.PAGES.DETAIL_MEMBER_PAGE, person.id)

            if int(passport_number) == person.id:
                person.delete()
                logUserActivity(request, constants.ACTION.DENY_MEMBER,
                                f"رفض وحذف سجل العضو ({person.name_ar}) "
                                + f"من قِبل {request.user.get_full_name()}")
                MSG.REJECT_RECORD(request)
                return redirect(constants.PAGES.MEMBERS_PAGE, "Approve")
            else:
                MSG.PASSPORT_NUMBER_ERROR(request)
                return redirect(constants.PAGES.DETAIL_MEMBER_PAGE, person.id)

    context: dict[str, Any] = {
        'person': person,
        'partners': partners,
        'children': children
    }
    return render(request, constants.TEMPLATES.DETAIL_MEMBER_TEMPLATE, context)


def thankYou(request: HttpRequest) -> HttpResponse:
    try:
        AuditEntry.get(
            ip=getClientIp(request),
            action=constants.ACTION.MEMBER_FORM_POST,
            created__range=(timezone.now() - timezone.timedelta(minutes=5),
                            timezone.now())
        )
    except AuditEntry.DoesNotExist:
        return redirect(constants.PAGES.INDEX_PAGE)
    return render(request, constants.TEMPLATES.THANK_YOU_TEMPLATE,)


def membershipCardPage(request: HttpRequest) -> HttpResponse:
    context: dict[str, Any] = {}
    return render(request, constants.TEMPLATES.MEMBERSHIP_CARD_PAGE_TEMPLATE, context)


def getMembershipData(request: HttpRequest, pk: str) -> HttpResponse:
    response_data: dict = {}
    try:
        membership: dict[str, Any] = Membership.objects.select_related("Person").values(
            "card_number", "last_month_paid").annotate(
                member_name=Subquery(
                    Person.objects.filter(
                        membership=OuterRef('id')).values('name_ar')[:1]
                )).get(card_number=pk)
        response_data["status"] = "200"
        response_data["membership"] = membership
    except Membership.DoesNotExist:
        response_data["card_number"] = pk
        response_data["status"] = "404"

    json_data = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
    return HttpResponse(json_data, content_type='application/json; charset=utf-8')
