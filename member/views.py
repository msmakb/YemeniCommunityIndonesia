from typing import Any

from django.contrib.auth.models import Group, User
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.utils import timezone

from main import constants
from main import messages as MSG
from main.models import AuditEntry
from main.parameters import getParameterValue
from main.utils import Pagination, getClientIp, getUserAgent

from .models import (Academic, Address, Membership,
                     FamilyMembers, FamilyMembersChild,
                     FamilyMembersWife, Person)
from .forms import (AddPersonForm, AcademicForm,
                    AddressForm, FamilyMembersForm)


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

    page: str = request.GET.get('page')
    pagination = Pagination(Person.filter(
        is_validated=is_validated), int(page) if page is not None else 1)
    page_obj: QuerySet[Person] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {
        'waiting': waiting,
        'page_obj': page_obj,
        'is_paginated': is_paginated,
        'currentPage': currentPage,
    }
    return render(request, constants.TEMPLATES.DASHBOARD_TEMPLATE, context)


def memberPage(request: HttpRequest, pk: str) -> HttpResponse:
    person: Person = Person.get(account=int(pk))

    context: dict[str, Any] = {
        'person': person
    }
    return render(request, constants.TEMPLATES.MEMBER_PAGE_TEMPLATE, context)


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

            return redirect(constants.PAGES.INDEX_PAGE)

    context: dict[str, Any] = {
        'person_form': person_form,
        'academic_form': academic_form,
        'address_form': address_form,
        'family_members_form': family_members_form,
    }
    return render(request, constants.TEMPLATES.MEMBER_FORM_TEMPLATE, context)


def detailMember(request: HttpRequest, pk: str) -> HttpResponse:
    person: Person = Person.get(id=pk)
    partners: FamilyMembersWife = FamilyMembersWife.filter(
        family_members=person.family_members)
    children: FamilyMembersChild = FamilyMembersChild.filter(
        family_members=person.family_members)

    if request.method == constants.POST_METHOD:
        if person.is_validated:
            MSG.SOMETHING_WRONG(request)
            return redirect(constants.PAGES.LOGOUT)
        passport_number: str = request.POST.get("passportNumber")
        if "approve" in request.POST:
            if passport_number != None:
                if request.POST.get('membership') == "1":
                    membership_type: int = None
                    try:
                        membership_type = int(
                            request.POST.get('membership_type'))
                        constants.MEMBERSHIP_TYPE_AR[membership_type]
                    except IndexError:
                        MSG.SOMETHING_WRONG(request)
                        return redirect(constants.PAGES.DASHBOARD, "Approve")
                    except ValueError:
                        MSG.SOMETHING_WRONG(request)
                        return redirect(constants.PAGES.DASHBOARD, "Approve")
                    idNum: str = str(person.id)
                    person.membership = Membership.create(
                        card_number=getParameterValue(constants.PARAMETERS.THREE_CHARACTER_PREFIX_FOR_MEMBERSHIP
                                                      ) + ('0' * (7 - len(idNum))) + idNum,
                        membership_type=membership_type,
                        expire_date=timezone.now().replace(
                            year=timezone.now().year + getParameterValue(constants.PARAMETERS.MEMBERSHIP_EXPIRE_PERIOD))
                    )
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
        elif "decline" in request.POST:
            try:
                if int(passport_number) == person.id:
                    # Clean up (Danger Zone)
                    for temp in FamilyMembersWife.filter(family_members=person.family_members):
                        temp.delete()
                    for temp in FamilyMembersChild.filter(family_members=person.family_members):
                        temp.delete()
                    temp = person.address
                    temp.delete()
                    temp = person.academic
                    temp.delete()
                    temp = person.family_members
                    temp.delete()
                    person.delete()
                    return redirect(constants.PAGES.DASHBOARD, "Approve")
                else:
                    MSG.PASSPORT_NUMBER_ERROR(request)
            except ValueError:
                MSG.PASSPORT_NUMBER_ERROR(request)

    context: dict[str, Any] = {
        'person': person,
        'partners': partners,
        'children': children
    }
    return render(request, constants.TEMPLATES.DETAIL_MEMBER_TEMPLATE, context)
