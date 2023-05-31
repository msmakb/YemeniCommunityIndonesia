from dataclasses import dataclass
from typing import Set, Optional

from django.http import HttpRequest

from main import constants
from company_user.models import CompanyUser


@dataclass
class MenuItem:
    name: str
    page: str
    is_active: str
    icon: Optional[str | None] = None
    arg: Optional[str | None] = None


def getUserMenus(request: HttpRequest) -> list[MenuItem]:
    if request.user.is_staff:
        company_user: CompanyUser | None = None
        try:
            company_user = CompanyUser.get(user=request.user)
        except CompanyUser.DoesNotExist:
            pass

        if company_user:
            groups: Set[str] = company_user.role.groups.all(
            ).values_list('name', flat=True)

        if request.user.is_superuser:
            groups = constants.GROUPS

        userMenu: list[MenuItem] = []

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

        if constants.GROUPS.PARAMETER in groups:
            menu_item: MenuItem = MenuItem(
                name=constants.GROUPS_AR[constants.GROUPS.PARAMETER],
                page=constants.PAGES.SETTINGS_PAGE,
                is_active=True if "Settings" in request.path else False,
                icon="svg/settings.svg",
            )
            userMenu.append(menu_item)

    return userMenu
