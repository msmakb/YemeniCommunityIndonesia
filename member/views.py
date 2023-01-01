from typing import Any

from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from main import constants
from main import messages as MSG
from main.utils import Pagination

from .models import Academic, Address, Membership, FamilyMembers, Person, FamilyMembersChild, FamilyMembersWife
from .forms import AddPersonForm, AcademicForm, AddressForm, FamilyMembersForm


def dashboard(request: HttpRequest) -> HttpResponse:
    waiting: int = Person.countFiltered(is_validated=False)

    page: str = request.GET.get('page')
    pagination = Pagination(Person.filter(
        is_validated=False), int(page) if page is not None else 1)
    page_obj: QuerySet[Person] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {
        'waiting': waiting,
        'page_obj': page_obj,
        'is_paginated': is_paginated,
    }
    return render(request, constants.TEMPLATES.DASHBOARD_TEMPLATE, context)


def memberPage(request: HttpRequest, pk: str) -> HttpResponse:
    return render(request, constants.TEMPLATES.MEMBER_PAGE_TEMPLATE)


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

    context: dict[str, Any] = {
        'person': person,
        'partners': partners,
        'children': children
    }
    return render(request, constants.TEMPLATES.DETAIL_MEMBER_TEMPLATE, context)
