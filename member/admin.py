from django.contrib.admin import ModelAdmin, register

from main.constants import BASE_MODEL_FIELDS, ROWS_PER_PAGE

from .models import Academic, Address, Membership, FamilyMembers, FamilyMembersChild, FamilyMembersWife, Person


@register(Academic)
class AcademicAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('id', 'academic_qualification', 'school', 'major', 'semester',
                                     *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('academic_qualification',)
    search_fields: tuple[str, ...] = (
        'id', 'academic_qualification', 'school', 'major', 'semester')
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS


@register(Address)
class AddressAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('id', 'street_address', 'district', 'city', 'province',
                                     'postal_code', *BASE_MODEL_FIELDS)
    search_fields: tuple[str, ...] = (
        'id', 'city', 'district', 'province', 'street_address')
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS


@register(Membership)
class MembershipAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('card_number', 'membership_type', 'issue_date',
                                     'expire_date', *BASE_MODEL_FIELDS)
    search_fields: tuple[str, ...] = (
        'card_number',)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS


@register(FamilyMembers)
class FamilyMembersAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('id', 'family_name', 'member_count',
                                     *BASE_MODEL_FIELDS)
    search_fields: tuple[str, ...] = (
        'id',)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS


@register(FamilyMembersChild)
class FamilyMembersChildAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('id', 'family_members', 'name', 'age',
                                     *BASE_MODEL_FIELDS)
    search_fields: tuple[str, ...] = (
        'id',)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS


@register(FamilyMembersWife)
class FamilyMembersWifeAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('id', 'family_members', 'name', 'age',
                                     *BASE_MODEL_FIELDS)
    search_fields: tuple[str, ...] = (
        'id',)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS


@register(Person)
class PersonAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('name_ar', 'name_en', 'gender', 'place_of_birth',
                                     'date_of_birth', 'call_number', 'whatsapp_number',
                                     'email', 'job_title', 'period_of_residence', 'photograph',
                                     'passport_photo', 'residency_photo', 'academic', 'address',
                                     'membership', 'family_members', 'account',
                                     *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('gender', 'job_title',
                                    'period_of_residence')
    search_fields: tuple[str, ...] = ('name_ar', 'name_en', 'place_of_birth', 'call_number',
                                      'whatsapp_number')
    ordering: tuple[str, ...] = ('-created',)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS
