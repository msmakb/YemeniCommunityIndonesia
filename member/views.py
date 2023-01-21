import os
from typing import Any

from django.contrib.auth.models import Group, User
from django.core.files.base import ContentFile
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from main import constants
from main import messages as MSG
from main.image_processing import ImageProcessor
from main.models import AuditEntry
from main.parameters import getParameterValue
from main.utils import Pagination, getClientIp, getUserAgent

from .models import (Academic, Address, Membership,
                     FamilyMembers, FamilyMembersChild,
                     FamilyMembersWife, Person)
from .forms import (AddPersonForm, AcademicForm,
                    AddressForm, FamilyMembersForm)
from .filters import PersonFilter


def dashboard(request: HttpRequest, currentPage: str) -> HttpResponse:
    waiting: int = Person.countFiltered(is_validated=False)
    is_validated: bool | None = None
    match currentPage.lower():
        case "list":
            is_validated = True
        case "approve":
            is_validated = False
        case _:
            raise Http404

    queryset: QuerySet[Person] = Person.filter(is_validated=is_validated)
    personFilter: PersonFilter = PersonFilter(request.GET, queryset=queryset)
    queryset = personFilter.qs
    page: str = request.GET.get('page')
    pagination = Pagination(queryset, int(page) if page is not None else 1)
    page_obj: QuerySet[Person] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {
        'waiting': waiting,
        'page_obj': page_obj,
        'is_paginated': is_paginated,
        'currentPage': currentPage,
        'personFilter': personFilter
    }
    return render(request, constants.TEMPLATES.DASHBOARD_TEMPLATE, context)


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


def downloadMembershipCard(request: HttpRequest, pk: str) -> HttpResponse:
    try:
        membership: Membership = Membership.get(id=pk)
    except Membership.DoesNotExist:
        raise Http404

    file_path = membership.membership_card.path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type="image/jpg")
            response['Content-Disposition'] = f'inline; filename={membership.card_number}.jpg'
            return response
    raise Http404


def memberFormPage(request: HttpRequest) -> HttpResponse:
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
                partner_list.append((name, int(age)))

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

            if person.membership:
                membership = person.membership
                person.membership = None
                person.save()
                membership.delete()

            idNum: str = str(person.id)
            membership: Membership = Membership.create(
                card_number=getParameterValue(constants.PARAMETERS.THREE_CHARACTER_PREFIX_FOR_MEMBERSHIP
                                              ) + ('0' * (7 - len(idNum))) + idNum,
                membership_type=membership_type,
                expire_date=(timezone.now().date().replace(
                    year=timezone.now().year + getParameterValue(constants.PARAMETERS.MEMBERSHIP_EXPIRE_PERIOD)))
            )

            person.membership = membership
            person.save()

            image_io: bytes = ImageProcessor.generateMembershipCardImage(
                person.photograph,
                person.name_ar,
                person.name_en,
                person.address.getCityAr,
                person.address.city,
                person.membership.getMembershipType,
                person.membership.getMembershipTypeEnglish,
                str(person.membership.issue_date),
                str(person.membership.expire_date),
                person.membership.card_number
            )

            membership.membership_card = ContentFile(
                image_io, "membership.jpg")
            membership.save()

            return redirect(constants.PAGES.DETAIL_MEMBER_PAGE, person.id)

        elif "approve" in request.POST:
            try:
                int(passport_number)
            except ValueError:
                MSG.PASSPORT_NUMBER_ERROR(request)
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
                Group.objects.get(name=constants.GROUPS.MEMBER).user_set.add(
                    person.account)

                return redirect(constants.PAGES.DASHBOARD, "Approve")
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
                return redirect(constants.PAGES.DASHBOARD, "Approve")
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
