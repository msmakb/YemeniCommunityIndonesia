from dataclasses import dataclass
from typing import Any, Set, Optional

from django.http import HttpRequest

from main import constants
from company_user.models import CompanyUser
from member.models import Person


@dataclass
class MenuItem:
    name: str
    page: str
    is_active: bool
    submenu: Optional[int | None] = None
    icon: Optional[str | None] = None
    arg: Optional[str | None] = None


def getUserMenus(request: HttpRequest) -> list[MenuItem]:
    userMenu: list[MenuItem] = []

    if not request.user.is_authenticated:
        return userMenu

    # Company User Menu
    if request.user.is_staff:
        company_user: CompanyUser | None = None
        try:
            company_user = CompanyUser.getCompanyUserByUserObject(
                request.user)
        except CompanyUser.DoesNotExist:
            pass

        if company_user:
            groups: Set[str] = company_user.role.groups.all(
            ).values_list('name', flat=True)

        if request.user.is_superuser:
            groups = constants.GROUPS

        if constants.GROUPS.MEMBERS in groups:
            menu_item: MenuItem = MenuItem(
                name=constants.GROUPS_AR[constants.GROUPS.MEMBERS],
                page=constants.PAGES.MEMBERS_PAGE,
                is_active=True if "Members" in request.path else False,
                arg='list',
                icon="svg/members.svg",
            )
            userMenu.append(menu_item)

        if constants.GROUPS.BROADCAST in groups:
            menu_item: MenuItem = MenuItem(
                name=constants.GROUPS_AR[constants.GROUPS.BROADCAST],
                page=constants.PAGES.BROADCAST_PAGE,
                is_active=True if "Broadcast" in request.path else False,
                icon="svg/broadcast.svg",
            )
            userMenu.append(menu_item)

        if constants.GROUPS.MONITOR in groups:
            menu_item: MenuItem = MenuItem(
                name=constants.GROUPS_AR[constants.GROUPS.MONITOR],
                page=constants.PAGES.MONITOR_PAGE,
                is_active=True if "Monitor" in request.path else False,
                icon="svg/monitor.svg",
            )
            userMenu.append(menu_item)

        if constants.GROUPS.COMPANY_USER in groups:
            menu_item: MenuItem = MenuItem(
                name=constants.GROUPS_AR[constants.GROUPS.COMPANY_USER],
                page=constants.PAGES.COMPANY_USERS_PAGE,
                is_active=True if "User-Management" in request.path else False,
                icon="svg/user_management.svg",
            )
            userMenu.append(menu_item)

        if constants.GROUPS.ACCOUNTING in groups \
            or constants.GROUPS.DONATION in groups \
                or constants.GROUPS.PAYMENT in groups:
            menu_item: MenuItem = MenuItem(
                name=constants.GROUPS_AR[constants.GROUPS.ACCOUNTING],
                page=constants.PAGES.ACCOUNTING_PAGE,
                is_active=True if "/Accounting/" in request.path else False,
                icon="svg/accounting.svg",
            )
            userMenu.append(menu_item)

        if constants.GROUPS.ACCOUNTING in groups:
            menu_item: MenuItem = MenuItem(
                name="الحسابات البنكية",
                page=constants.PAGES.ACCOUNT_LIST_PAGE,
                submenu=constants.GROUPS.ACCOUNTING,
                is_active=True if "/Accounts/" in request.path else False,
                icon="svg/bank.svg",
            )
            userMenu.append(menu_item)

            menu_item: MenuItem = MenuItem(
                name="قائمة السندات",
                page=constants.PAGES.BOND_LIST_PAGE,
                submenu=constants.GROUPS.ACCOUNTING,
                is_active=True if "/Bond/" in request.path else False,
                icon="svg/bond.svg",
            )
            userMenu.append(menu_item)

        if constants.GROUPS.PAYMENT in groups:
            menu_item: MenuItem = MenuItem(
                name=constants.GROUPS_AR[constants.GROUPS.PAYMENT],
                page=constants.PAGES.MEMBERSHIP_PAYMENT_LIST_PAGE,
                submenu=constants.GROUPS.ACCOUNTING,
                is_active=True if "/Payment/" in request.path else False,
                icon="svg/payment_history.svg",
            )
            userMenu.append(menu_item)

        if constants.GROUPS.DONATION in groups:
            menu_item: MenuItem = MenuItem(
                name=constants.GROUPS_AR[constants.GROUPS.DONATION],
                page=constants.PAGES.DONATION_LIST_PAGE,
                submenu=constants.GROUPS.ACCOUNTING,
                is_active=True if "/Donation-List/" in request.path else False,
                icon="svg/donation.svg",
            )
            userMenu.append(menu_item)

        if constants.GROUPS.FORMS in groups:
            menu_item: MenuItem = MenuItem(
                name=constants.GROUPS_AR[constants.GROUPS.FORMS],
                page=constants.PAGES.FORMS_LIST_PAGE,
                is_active=True if "Forms" in request.path else False,
                icon="svg/forms.svg",
            )
            userMenu.append(menu_item)

        if constants.GROUPS.PARAMETER in groups:
            menu_item: MenuItem = MenuItem(
                name=constants.GROUPS_AR[constants.GROUPS.PARAMETER],
                page=constants.PAGES.SETTINGS_PAGE,
                is_active=True if "Settings" in request.path else False,
                icon="svg/settings.svg",
            )
            userMenu.append(menu_item)

    # Members Menus
    elif not request.user.is_staff:
        user_data: dict[str, Any] = Person.getUserData(request.user)
        if user_data.get('has_membership'):

            menu_item: MenuItem = MenuItem(
                name="بطاقة العضوية",
                page=constants.PAGES.MEMBERSHIP_CARD_PAGE,
                is_active=True if "Membership-Card" in request.path else False,
                icon="svg/membership_card.svg",
            )
            userMenu.append(menu_item)

            menu_item: MenuItem = MenuItem(
                name="دفع الإشتراك",
                page=constants.PAGES.MEMBERSHIP_PAYMENT_PAGE,
                is_active=True if "Membership-Payment" in request.path else False,
                icon="svg/pay.svg",
            )
            userMenu.append(menu_item)

            menu_item: MenuItem = MenuItem(
                name="مدفوعات العضوية",
                page=constants.PAGES.MEMBERSHIP_PAYMENT_HISTORY_PAGE,
                is_active=True if "Payment-History" in request.path else False,
                icon="svg/payment_history.svg",
            )
            userMenu.append(menu_item)

            menu_item: MenuItem = MenuItem(
                name="ادعمنا",
                page=constants.PAGES.DONATION_PAGE,
                is_active=True if "/Donation/" in request.path else False,
                icon="svg/donation.svg",
            )
            userMenu.append(menu_item)

    return userMenu
