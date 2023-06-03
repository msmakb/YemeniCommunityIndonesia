from django.core.files.base import ContentFile
from io import BytesIO
import os
from PIL import Image

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, Client, RequestFactory
from django.http import HttpResponse, HttpRequest, Http404
from django.urls import reverse, resolve
from django.utils import timezone
from django.utils.timezone import datetime, timedelta

from main import constants
from main.models import AuditEntry
from main.utils import getClientIp

from .admin import (AcademicAdmin, AddressAdmin, MembershipAdmin,
                    FamilyMembersAdmin, FamilyMembersWifeAdmin,
                    FamilyMembersChildAdmin)
from .filters import PersonFilter
from .forms import (AddressForm, FamilyMembersForm,
                    AcademicForm, AddPersonForm)
from .models import (Academic, Address, Membership,
                     FamilyMembers, FamilyMembersWife,
                     FamilyMembersChild, Person)
from . import views


class AcademicAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.academic_admin = AcademicAdmin(Academic, self.site)
        self.academic = Academic.objects.create(
            academic_qualification='Bachelors',
            school='University of Test',
            major='Test',
            semester=1)

    def test_list_display(self):
        self.assertEqual(self.academic_admin.list_display, (
            'id', 'academic_qualification', 'school', 'major', 'semester',
            *constants.BASE_MODEL_FIELDS))

    def test_list_filter(self):
        self.assertEqual(self.academic_admin.list_filter,
                         ('academic_qualification',))

    def test_search_fields(self):
        self.assertEqual(self.academic_admin.search_fields, ('id',
                         'academic_qualification', 'school', 'major', 'semester'))

    def test_list_per_page(self):
        self.assertEqual(self.academic_admin.list_per_page,
                         constants.ROWS_PER_PAGE)

    def test_exclude(self):
        self.assertEqual(self.academic_admin.exclude,
                         constants.BASE_MODEL_FIELDS)


class AddressAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.address_admin = AddressAdmin(Address, self.site)
        self.address = Address.objects.create(
            street_address='123 Test St',
            district='Test District',
            city='Test City',
            province='Test Province',
            postal_code='12345')

    def test_list_display(self):
        self.assertEqual(self.address_admin.list_display, (
            'id', 'street_address', 'district', 'city', 'province',
            'postal_code', *constants.BASE_MODEL_FIELDS))

    def test_search_fields(self):
        self.assertEqual(self.address_admin.search_fields,
                         ('id', 'city', 'district', 'province', 'street_address'))

    def test_list_per_page(self):
        self.assertEqual(self.address_admin.list_per_page,
                         constants.ROWS_PER_PAGE)

    def test_exclude(self):
        self.assertEqual(self.address_admin.exclude,
                         constants.BASE_MODEL_FIELDS)


class MembershipAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.membership_admin = MembershipAdmin(Membership, self.site)
        self.membership = Membership.objects.create(
            card_number='12345',
            membership_type='regular',
            issue_date=datetime.now(),
            expire_date=datetime.now() + timedelta(days=365))

    def test_list_display(self):
        self.assertEqual(self.membership_admin.list_display, (
            'card_number', 'membership_type', 'issue_date', 'expire_date',
            *constants.BASE_MODEL_FIELDS))

    def test_search_fields(self):
        self.assertEqual(self.membership_admin.search_fields, ('card_number',))

    def test_list_per_page(self):
        self.assertEqual(self.membership_admin.list_per_page,
                         constants.ROWS_PER_PAGE)

    def test_exclude(self):
        self.assertEqual(self.membership_admin.exclude,
                         constants.BASE_MODEL_FIELDS)


class FamilyMembersChildAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.family_members_child_admin = FamilyMembersChildAdmin(
            FamilyMembersChild, self.site)
        self.family_members_child = FamilyMembersChild.objects.create(
            family_members=FamilyMembers.objects.create(
                family_name="Test Name",
                member_count=2
            ),
            name='Child Test',
            age='5')

    def test_list_display(self):
        self.assertEqual(self.family_members_child_admin.list_display,
                         ('id', 'family_members', 'name', 'age',
                          *constants.BASE_MODEL_FIELDS))

    def test_search_fields(self):
        self.assertEqual(
            self.family_members_child_admin.search_fields, ('id',))

    def test_list_per_page(self):
        self.assertEqual(
            self.family_members_child_admin.list_per_page, constants.ROWS_PER_PAGE)

    def test_exclude(self):
        self.assertEqual(
            self.family_members_child_admin.exclude, constants.BASE_MODEL_FIELDS)


class FamilyMembersWifeAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.family_members_wife_admin = FamilyMembersWifeAdmin(
            FamilyMembersWife, self.site)
        self.family_members_wife = FamilyMembersWife.objects.create(
            family_members=FamilyMembers.objects.create(
                family_name="Test Name",
                member_count=2
            ),
            name='Wife Test',
            age='30')

    def test_list_display(self):
        self.assertEqual(self.family_members_wife_admin.list_display,
                         ('id', 'family_members', 'name', 'age', *constants.BASE_MODEL_FIELDS))

    def test_search_fields(self):
        self.assertEqual(self.family_members_wife_admin.search_fields, ('id',))

    def test_list_per_page(self):
        self.assertEqual(
            self.family_members_wife_admin.list_per_page, constants.ROWS_PER_PAGE)

    def test_exclude(self):
        self.assertEqual(
            self.family_members_wife_admin.exclude, constants.BASE_MODEL_FIELDS)


class FamilyMembersAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.family_members_admin = FamilyMembersAdmin(
            FamilyMembers, self.site)
        self.family_members = FamilyMembers.objects.create(
            family_name='Test Family', member_count='5')

    def test_list_display(self):
        self.assertEqual(self.family_members_admin.list_display, (
            'id', 'family_name', 'member_count', *constants.BASE_MODEL_FIELDS))

    def test_search_fields(self):
        self.assertEqual(self.family_members_admin.search_fields, ('id',))

    def test_list_per_page(self):
        self.assertEqual(self.family_members_admin.list_per_page,
                         constants.ROWS_PER_PAGE)

    def test_exclude(self):
        self.assertEqual(self.family_members_admin.exclude,
                         constants.BASE_MODEL_FIELDS)


class UrlTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.person = Person.objects.create(
            name_ar="Test Person,",
            name_en="Test Person,",
            gender="1",
            place_of_birth="Test",
            date_of_birth=timezone.now(),
            call_number="123123123123",
            whatsapp_number="123123123123",
            email="tset@test.te",
            job_title="1",
            period_of_residence="1",
        )

    def test_members_page_is_resolved(self):
        url = reverse(constants.PAGES.MEMBERS_PAGE, args=['currentPage'])
        self.assertEquals(resolve(url).func, views.dashboard)

    def test_detail_member_is_resolved(self):
        url = reverse(constants.PAGES.DETAIL_MEMBER_PAGE, args=['pk'])
        self.assertEquals(resolve(url).func, views.detailMember)

    def test_member_dashboard_is_resolved(self):
        url = reverse(constants.PAGES.MEMBER_DASHBOARD)
        self.assertEquals(resolve(url).func, views.memberPage)

    def test_member_form_page_is_resolved(self):
        url = reverse(constants.PAGES.MEMBER_FORM_PAGE)
        self.assertEquals(resolve(url).func, views.memberFormPage)

    def test_thank_you_page_is_resolved(self):
        url = reverse(constants.PAGES.THANK_YOU_PAGE)
        self.assertEquals(resolve(url).func, views.thankYou)


class PersonFilterTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # create some test data in the database
        Person.objects.create(
            name_ar='أحمد',
            name_en='Ahmed',
            gender=constants.GENDER.MALE,
            job_title='1',
            period_of_residence='1',
            passport_number='1234567',
            date_of_birth='1970-01-01',
            address=Address.objects.create(
                street_address='123 Main St.',
                district='Downtown',
                city="Surabaya",
                province='Province1',
                postal_code='12345'
            ),
            academic=Academic.objects.create(
                academic_qualification='1'
            ),
            membership=Membership.objects.create(
                membership_type='1',
                card_number='13579',
                issue_date='2022-01-01',
                expire_date='2022-12-31'
            )
        )
        Person.objects.create(
            name_ar='أنس',
            name_en='Anas',
            gender=constants.GENDER.MALE,
            job_title='2',
            period_of_residence='2',
            passport_number='7654321',
            date_of_birth='1985-05-12',
            address=Address.objects.create(
                street_address='456 Park Ave.',
                district='Uptown',
                city="Jakarta",
                province='Province2',
                postal_code='67890'
            ),
            academic=Academic.objects.create(
                academic_qualification='2'
            ),
            membership=Membership.objects.create(
                card_number='67890',
                membership_type='2',
                issue_date='2022-01-01',
                expire_date='2022-12-31'
            )
        )
        Person.objects.create(
            name_ar='ألين',
            name_en='Alina',
            gender=constants.GENDER.FEMALE,
            job_title='3',
            period_of_residence='3',
            passport_number='24680',
            date_of_birth='2000-09-30',
            address=Address.objects.create(
                street_address='789 Elm St.',
                district='Midtown',
                city="Jakarta",
                province='Province3',
                postal_code='09876'
            ),
            academic=Academic.objects.create(
                academic_qualification='3'
            ),
            membership=Membership.objects.create(
                card_number='1234567890',
                membership_type='3',
                issue_date='2022-01-01',
                expire_date='2022-12-31'
            )
        )

    def test_name_ar_filter(self):
        # create an instance of the filter
        f = PersonFilter({'name_ar': 'أحمد'})
        # check that the queryset is filtered correctly
        self.assertEqual(len(f.qs), 1)
        self.assertEqual(f.qs[0].name_ar, 'أحمد')

    def test_name_en_filter(self):
        f = PersonFilter({'name_en': 'Anas'})
        self.assertEqual(len(f.qs), 1)
        self.assertEqual(f.qs[0].name_en, 'Anas')

    def test_gender_filter(self):
        f = PersonFilter({'gender': constants.GENDER.MALE})
        self.assertEqual(len(f.qs), 2)
        self.assertEqual(f.qs[0].gender, constants.GENDER.MALE)
        self.assertEqual(f.qs[1].gender, constants.GENDER.MALE)

    def test_job_title_filter(self):
        f = PersonFilter({'job_title': '1'})
        self.assertEqual(len(f.qs), 1)
        self.assertEqual(f.qs[0].job_title, '1')

    def test_period_of_residence_filter(self):
        f = PersonFilter({'period_of_residence': '1'})
        self.assertEqual(len(f.qs), 1)
        self.assertEqual(f.qs[0].period_of_residence, '1')

    def test_address__city_filter(self):
        f = PersonFilter({'address__city': 'Jakarta'})
        self.assertEqual(len(f.qs), 2)
        self.assertEqual(f.qs[0].address.city, 'Jakarta')

    def test_academic__academic_qualification_filter(self):
        f = PersonFilter({'academic__academic_qualification': '1'})
        self.assertEqual(len(f.qs), 1)
        self.assertEqual(f.qs[0].academic.academic_qualification, '1')

    def test_membership__membership_type_filter(self):
        f = PersonFilter({'membership__membership_type': '1'})
        self.assertEqual(len(f.qs), 1)
        self.assertEqual(f.qs[0].membership.membership_type, '1')

    def test_membership__card_number_filter(self):
        f = PersonFilter({'membership__card_number': '1234567890'})
        self.assertEqual(len(f.qs), 1)
        self.assertEqual(f.qs[0].membership.card_number, '1234567890')

    def test_passport_number_filter(self):
        f = PersonFilter({'passport_number': '1234567'})
        self.assertEqual(len(f.qs), 1)
        self.assertEqual(f.qs[0].passport_number, '1234567')


class AddressFormTest(TestCase):
    def test_form_valid(self):
        form_data = {
            'street_address': '123 Main St.',
            'district': 'Downtown',
            'city': 'Surabaya',
            'province': 'Province1',
            'postal_code': '12345'
        }
        form = AddressForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form_data = {
            'street_address': '',
            'district': '',
            'city': '',
            'province': '',
            'postal_code': ''
        }
        form = AddressForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('street_address', form.errors)
        self.assertIn('district', form.errors)
        self.assertIn('city', form.errors)
        self.assertIn('province', form.errors)

    def test_form_save(self):
        form_data = {
            'street_address': '123 Main St.',
            'district': 'Downtown',
            'city': 'Surabaya',
            'province': 'Province1',
            'postal_code': '12345'
        }
        form = AddressForm(data=form_data)
        self.assertTrue(form.is_valid())
        address = form.save()
        self.assertEqual(address.street_address, '123 Main St.')
        self.assertEqual(address.district, 'Downtown')
        self.assertEqual(address.city, 'Surabaya')
        self.assertEqual(address.province, 'Province1')
        self.assertEqual(address.postal_code, '12345')

    def test_invalid_city(self):
        form_data = {
            'street_address': '123 Main St.',
            'district': 'Downtown',
            'city': 'Invalid City',
            'province': 'Province1',
            'postal_code': '12345'
        }
        form = AddressForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('city', form.errors)


class FamilyMembersFormTest(TestCase):
    def test_form_valid(self):
        form_data = {
            'family_name': 'آل ..',
            'member_count': 3,
        }
        form = FamilyMembersForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form_data = {
            'family_name': '',
            'member_count': '',
        }
        form = FamilyMembersForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('family_name', form.errors)
        self.assertIn('member_count', form.errors)

    def test_form_save(self):
        form_data = {
            'family_name': 'آل ..',
            'member_count': 3,
        }
        form = FamilyMembersForm(data=form_data)
        self.assertTrue(form.is_valid())
        family_members = form.save()
        self.assertEqual(family_members.family_name, 'آل ..')
        self.assertEqual(family_members.member_count, 3)

    def test_negative_member_count(self):
        form_data = {
            'family_name': 'آل ..',
            'member_count': -1,
        }
        form = FamilyMembersForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'member_count': ['تحقق من أن تكون هذه القيمة أكثر من 0 أو مساوية لها.'],
        })

    def test_decimal_member_count(self):
        form_data = {
            'family_name': 'آل ..',
            'member_count': 2.5,
        }
        form = FamilyMembersForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'member_count': ['أدخل رقما صحيحا.'],
        })

    def test_large_member_count(self):
        form_data = {
            'family_name': 'آل ..',
            'member_count': 25,
        }
        form = FamilyMembersForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'member_count': ['أدخل رقما صحيحا.'],
        })


class AcademicFormTest(TestCase):
    def test_form_valid(self):
        form_data = {
            'academic_qualification': '1',
            'school': 'Yemeni University',
            'major': 'IT',
            'semester': 4,
        }
        form = AcademicForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form_data = {
            'academic_qualification': '',
            'school': '',
            'major': '',
            'semester': '',
        }
        form = AcademicForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('academic_qualification', form.errors)

    def test_form_save(self):
        form_data = {
            'academic_qualification': '1',
            'school': 'Yemeni University',
            'major': 'IT',
            'semester': 4,
        }
        form = AcademicForm(data=form_data)
        self.assertTrue(form.is_valid())
        academic = form.save()
        self.assertEqual(academic.academic_qualification, '1')
        self.assertEqual(academic.school, 'Yemeni University')
        self.assertEqual(academic.major, 'IT')
        self.assertEqual(academic.semester, 4)

    def test_negative_semester(self):
        form_data = {
            'academic_qualification': '1',
            'school': 'Yemeni University',
            'major': 'IT',
            'semester': -1,
        }
        form = AcademicForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('semester', form.errors)


class AddPersonFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_image_path = os.path.join(
            settings.MEDIA_ROOT / "templates/female_no_image.jpg")
        test_image = Image.open(test_image_path)
        # Convert to bytes
        image_io: BytesIO = BytesIO()
        test_image = test_image.convert('RGB')
        test_image.save(image_io, format="JPEG", quality=100)
        test_image = ContentFile(image_io.getvalue(), "no_image.jpg")

        cls.files = {
            'photograph': None,
            'passport_photo': test_image,
            'residency_photo': test_image,
        }
        cls.data = {
            'name_ar': 'ساره عبدالله',
            'name_en': 'Sarah Abdullah',
            'gender': constants.GENDER.FEMALE,
            'place_of_birth': 'اليمن',
            'date_of_birth': '1970-01-01',
            'country_code1': '62',
            'call_number': '08123456789',
            'country_code2': '62',
            'whatsapp_number': '08123456789',
            'email': 'sarah@example.com',
            'job_title': constants.JOB_TITLE.STUDENT,
            'period_of_residence': constants.PERIOD_OF_RESIDENCE.TWO_YEARS_TO_THREE_YEARS,
        }

    def test_form_valid_data(self):
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid())

    def test_form_name_ar_too_short(self):
        self.data['name_ar'] = 'ساره'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get('name_ar'), [
                         "يجب أن يحتوي الاسم على 10 أحرف على الأقل"])

    def test_form_name_ar_with_non_arabic_chars(self):
        self.data['name_ar'] = 'أحمد 123'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get('name_ar'), [
                         "يجب أن يحتوي هذا الحقل على أحرف عربية فقط"])

    def test_form_name_ar_with_english_chars(self):
        self.data['name_ar'] = 'أحمد abc'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get('name_ar'), [
                         "يجب أن يحتوي هذا الحقل على أحرف عربية فقط"])

    def test_form_name_en_with_non_english_chars(self):
        form = AddPersonForm(
            data={'name_en': 'Sarah Abdullah123'}, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("name_en"), [
                         "يجب أن يحتوي هذا الحقل على أحرف إنجليزية فقط"])

    def test_form_name_en_length(self):
        form = AddPersonForm(data={'name_en': 'Sarah'}, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("name_en"), [
                         "يجب أن يحتوي الاسم على 10 أحرف على الأقل"])

    def test_form_invalid_if_the_photograph_is_None_and_the_gender_is_male(self):
        self.data['gender'] = constants.GENDER.MALE
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get('__all__'), ["هذا الحقل مطلوب"])

    def test_form_place_of_birth_with_english_chars(self):
        self.data['place_of_birth'] = 'Yemen123'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("place_of_birth"), [
                         "يجب كتابة مكان الميلاد باللغة العربية"])

    def test_form_place_of_birth_with_arabic_chars_and_comma(self):
        self.data['place_of_birth'] = 'صنعاء, اليمن'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid())

    def test_form_place_of_birth_with_arabic_chars_and_dash(self):
        self.data['place_of_birth'] = 'صنعاء - اليمن'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid())

    def test_form_place_of_birth_with_arabic_chars_and_space(self):
        self.data['place_of_birth'] = 'صنعاء اليمن'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid())

    def test_form_date_of_birth_under_18_years(self):
        self.data['date_of_birth'] = '2008-01-01'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get('date_of_birth'), [
            "يجب أن يكون عمرك 18 عامًا على الأقل"])

    def test_form_date_of_birth_valid_age(self):
        self.data['date_of_birth'] = '1970-01-01'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid())
        self.data['date_of_birth'] = '2005-01-01'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid())

    def test_form_call_number_with_international_key(self):
        self.data['call_number'] = '+966123456789'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("call_number"), [
            "يجب عدم إدخال المفتاح الدولي في هذا الحقل"])

    def test_form_call_number_with_too_few_digits(self):
        self.data['call_number'] = '1234567'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("call_number"), [
            "رقم الهاتف غير صحيح"])

    def test_form_call_number_validation_success(self):
        self.data['call_number'] = '1234567890'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid())

    def test_form_whatsapp_number_with_international_key(self):
        self.data['whatsapp_number'] = '+966123456789'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("whatsapp_number"), [
            "يجب عدم إدخال المفتاح الدولي في هذا الحقل"])

    def test_form_whatsapp_number_with_too_few_digits(self):
        self.data['whatsapp_number'] = '1234567'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("whatsapp_number"), [
            "رقم الهاتف غير صحيح"])

    def test_form_whatsapp_number_validation_success(self):
        self.data['whatsapp_number'] = '1234567890'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid())

    def test_form_email_validation_success(self):
        self.data['email'] = 'yemeni@indonesia.com'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid())

    def test_form_email_validation_failure(self):
        self.data['email'] = 'yemeniindonesia.com'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())

    def test_form_valid_job_title(self):
        self.data['job_title'] = constants.JOB_TITLE.STUDENT
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid())

    def test_form_invalid_job_title(self):
        self.data['job_title'] = 'invalid_job_title'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())

    def test_form_valid_period_of_residence(self):
        self.data['period_of_residence'] = constants.PERIOD_OF_RESIDENCE.TWO_YEARS_TO_THREE_YEARS
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid())

    def test_form_invalid_period_of_residence(self):
        self.data['period_of_residence'] = 'invalid_period_of_residence'
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())

    def test_form_photograph_required_for_male(self):
        self.data['gender'] = constants.GENDER.MALE
        self.files['photograph'] = None
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get('__all__'), ["هذا الحقل مطلوب"])

    def test_form_photograph_not_required_for_female(self):
        self.data['gender'] = constants.GENDER.FEMALE
        self.files['photograph'] = None
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid())

    def test_form_missing_passport_photo(self):
        self.files['passport_photo'] = None
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get(
            'passport_photo'), ["هذا الحقل مطلوب."])

    def test_form_missing_residency_photo(self):
        self.files['residency_photo'] = None
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get(
            'residency_photo'), ["هذا الحقل مطلوب."])

    def test_form_save_data(self):
        form = AddPersonForm(data=self.data, files=self.files)
        form.save()
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(Person.objects.get().name_ar, 'ساره عبدالله')

    def test_form_invalid_data(self):
        self.data['name_ar'] = ''
        form = AddPersonForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name_ar'], ['هذا الحقل مطلوب.'])

    def tearDown(self) -> None:
        try:
            for person in Person.objects.all():
                person.delete()
        except AttributeError:
            pass
        return super().tearDown()


class SignalsTest(TestCase):

    def setUp(self) -> None:
        test_image_path = os.path.join(
            settings.MEDIA_ROOT / "templates/female_no_image.jpg")
        test_image = Image.open(test_image_path)
        # Convert to bytes
        image_io: BytesIO = BytesIO()
        test_image = test_image.convert('RGB')
        test_image.save(image_io, format="JPEG", quality=100)
        test_image = ContentFile(image_io.getvalue(), "no_image.jpg")
        family_members: FamilyMembers = FamilyMembers.objects.create(
            family_name="Test",
            member_count=1
        )
        for i in range(4):
            if i % 2 == 0:
                FamilyMembersWife.objects.create(
                    family_members=family_members,
                    name="Test",
                    age=23
                )
            else:
                FamilyMembersChild.objects.create(
                    family_members=family_members,
                    name="Test",
                    age=23
                )
        self.person: Person = Person.objects.create(
            name_ar='ساره عبدالله',
            name_en='Sarah Abdullah',
            gender=constants.GENDER.FEMALE,
            place_of_birth='اليمن',
            date_of_birth='1970-01-01',
            call_number='(+62) 08123456789',
            whatsapp_number='(+62) 08123456789',
            email='sarah@example.com',
            job_title=constants.JOB_TITLE.STUDENT,
            period_of_residence=constants.PERIOD_OF_RESIDENCE.TWO_YEARS_TO_THREE_YEARS,
            address=Address.objects.create(
                street_address='789 Elm St.',
                district='Midtown',
                city="Jakarta",
                province='Province3',
                postal_code='09876'
            ),
            academic=Academic.objects.create(
                academic_qualification='3'
            ),
            membership=Membership.objects.create(
                membership_card=test_image,
                card_number='1234567890',
                membership_type='3',
                issue_date='2022-01-01',
                expire_date='2022-12-31'
            ),
            account=User.objects.create_user(
                username="testUst",
                password="test"
            ),
            family_members=family_members,
            photograph=test_image,
            passport_photo=test_image,
            residency_photo=test_image
        )
        return super().setUp()

    def test_clean_up_person_data_deletes_photograph(self):
        photograph_path = self.person.photograph.path
        self.person.delete()
        self.assertFalse(os.path.exists(photograph_path))

    def test_clean_up_person_data_deletes_residency_photo(self):
        residency_photo_path = self.person.residency_photo.path
        self.person.delete()
        self.assertFalse(os.path.exists(residency_photo_path))

    def test_clean_up_person_data_deletes_passport_photo(self):
        passport_photo_path = self.person.passport_photo.path
        self.person.delete()
        self.assertFalse(os.path.exists(passport_photo_path))

    def test_delete_membership_card_membership_card(self):
        membership_card_path = self.person.membership.membership_card.path
        self.person.delete()
        self.assertFalse(os.path.exists(membership_card_path))

    def test_clean_up_person_data_deletes_account(self):
        account_id = self.person.account.id
        self.person.delete()
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=account_id)

    def test_clean_up_person_data_deletes_membership(self):
        membership_id = self.person.membership.id
        self.person.delete()
        with self.assertRaises(Membership.DoesNotExist):
            Membership.objects.get(id=membership_id)

    def test_clean_up_person_data_deletes_family_members_wife(self):
        wife_count = FamilyMembersWife.objects.filter(
            family_members=self.person.family_members).count()
        self.assertEqual(wife_count, 2)
        self.person.delete()
        self.assertEqual(FamilyMembersWife.objects.filter(
            family_members=self.person.family_members).count(), 0)

    def test_clean_up_person_data_deletes_family_members_child(self):
        child_count = FamilyMembersChild.objects.filter(
            family_members=self.person.family_members).count()
        self.assertEqual(child_count, 2)
        self.person.delete()
        self.assertEqual(FamilyMembersChild.objects.filter(
            family_members=self.person.family_members).count(), 0)

    def test_clean_up_person_data_deletes_family_members(self):
        family_members_id = self.person.family_members.id
        self.person.delete()
        with self.assertRaises(FamilyMembers.DoesNotExist):
            FamilyMembers.objects.get(id=family_members_id)

    def test_clean_up_person_data_deletes_address(self):
        address_id = self.person.address.id
        self.person.delete()
        with self.assertRaises(Address.DoesNotExist):
            Address.objects.get(id=address_id)

    def test_clean_up_person_data_deletes_academic(self):
        self.person.delete()
        with self.assertRaises(Academic.DoesNotExist):
            Academic.objects.get(pk=self.person.academic.pk)

    def test_on_update_person_deletes_old_photograph(self):
        test_image_path = os.path.join(
            settings.MEDIA_ROOT / "templates/membership_template.jpg")
        new_image = Image.open(test_image_path)
        # Convert to bytes
        image_io: BytesIO = BytesIO()
        new_image = new_image.convert('RGB')
        new_image.save(image_io, format="JPEG", quality=100)
        new_image = ContentFile(image_io.getvalue(), "no_image.jpg")
        old_photograph_path = self.person.photograph.path
        self.person.photograph = new_image
        self.assertTrue(os.path.exists(old_photograph_path))
        self.person.save()
        self.assertFalse(os.path.exists(old_photograph_path))

    def test_on_update_person_deletes_old_passport_photo(self):
        test_image_path = os.path.join(
            settings.MEDIA_ROOT / "templates/membership_template.jpg")
        new_image = Image.open(test_image_path)
        # Convert to bytes
        image_io: BytesIO = BytesIO()
        new_image = new_image.convert('RGB')
        new_image.save(image_io, format="JPEG", quality=100)
        new_image = ContentFile(image_io.getvalue(), "no_image.jpg")
        old_passport_photo_path = self.person.passport_photo .path
        self.person.passport_photo = new_image
        self.assertTrue(os.path.exists(old_passport_photo_path))
        self.person.save()
        self.assertFalse(os.path.exists(old_passport_photo_path))

    def test_on_update_person_deletes_old_residency_photo(self):
        test_image_path = os.path.join(
            settings.MEDIA_ROOT / "templates/membership_template.jpg")
        new_image = Image.open(test_image_path)
        # Convert to bytes
        image_io: BytesIO = BytesIO()
        new_image = new_image.convert('RGB')
        new_image.save(image_io, format="JPEG", quality=100)
        new_image = ContentFile(image_io.getvalue(), "no_image.jpg")
        old_residency_photo_path = self.person.residency_photo .path
        self.person.residency_photo = new_image
        self.assertTrue(os.path.exists(old_residency_photo_path))
        self.person.save()
        self.assertFalse(os.path.exists(old_residency_photo_path))

    def test_on_update_person_does_not_delete_photograph_if_photo_not_changed(self):
        photograph_path = self.person.photograph.path
        self.person.name_en = "Test Name"
        self.person.save()
        self.assertTrue(os.path.exists(photograph_path))

    def test_on_update_person_does_not_delete_passport_photo_if_photo_not_changed(self):
        passport_photo_path = self.person.passport_photo.path
        self.person.name_en = "Test Name"
        self.person.save()
        self.assertTrue(os.path.exists(passport_photo_path))

    def test_on_update_person_does_not_delete_residency_photo_if_photo_not_changed(self):
        residency_photo_path = self.person.residency_photo.path
        self.person.name_en = "Test Name"
        self.person.save()
        self.assertTrue(os.path.exists(residency_photo_path))

    def tearDown(self) -> None:
        try:
            for person in Person.objects.all():
                person.delete()
        except AttributeError:
            pass
        return super().tearDown()


class TestViews(TestCase):

    def setUp(self):
        test_image_path = os.path.join(
            settings.MEDIA_ROOT / "templates/female_no_image.jpg")
        self.test_image = Image.open(test_image_path)
        # Convert to bytes
        image_io: BytesIO = BytesIO()
        self.test_image = self.test_image.convert('RGB')
        self.test_image.save(image_io, format="JPEG", quality=100)
        self.test_image = ContentFile(image_io.getvalue(), "no_image.jpg")
        self.client = Client()
        self.factory = RequestFactory()
        self.test_ip: str = "123.123.123.123"
        self.user_agent: str = "Python"
        self.factory.defaults['REMOTE_ADDR'] = self.test_ip
        self.factory.defaults['HTTP_USER_AGENT'] = self.user_agent
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )
        group = Group.objects.get(name=constants.GROUPS.MANAGER)
        self.user.groups.add(group)

    def test_dashboard_list_view(self):
        request: HttpRequest = self.factory.get('/')
        request.user = self.user
        response: HttpResponse = views.dashboard(request, "List")
        response.client = self.client
        self.assertEqual(response.status_code, 200)

    def test_detail_member_view(self):
        person = Person.objects.create(
            name_ar="Test Person,",
            name_en="Test Person,",
            gender="1",
            place_of_birth="Test",
            date_of_birth=timezone.now(),
            call_number="123123123123",
            whatsapp_number="123123123123",
            email="tset@test.te",
            job_title="1",
            period_of_residence="1",
            account=self.user,
            passport_photo=self.test_image,
            residency_photo=self.test_image
        )
        request: HttpRequest = self.factory.get('/')
        request.user = self.user
        response: HttpResponse = views.detailMember(request, person.pk)
        response.client = self.client
        self.assertEqual(response.status_code, 200)

    def test_dashboard_approve_view(self):
        request: HttpRequest = self.factory.get('/')
        request.user = self.user
        response: HttpResponse = views.dashboard(request, "Approve")
        response.client = self.client
        self.assertEqual(response.status_code, 200)

    def test_member_view(self):
        request: HttpRequest = self.factory.get('/')
        group = Group.objects.get(name=constants.GROUPS.MEMBER)
        self.user.groups.add(group)
        request.user = self.user
        Person.objects.create(
            name_ar="Test Person,",
            name_en="Test Person,",
            gender="1",
            place_of_birth="Test",
            date_of_birth=timezone.now(),
            call_number="123123123123",
            whatsapp_number="123123123123",
            email="tset@test.te",
            job_title="1",
            period_of_residence="1",
            account=self.user
        )
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response: HttpResponse = views.memberPage(request)
        response.client = self.client
        self.assertEqual(response.status_code, 200)

    def test_member_view_with_no_person_object(self):
        request: HttpRequest = self.factory.get('/')
        group = Group.objects.get(name=constants.GROUPS.MEMBER)
        self.user.groups.add(group)
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response: HttpResponse = views.memberPage(request)
        response.client = self.client
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            constants.PAGES.LOGOUT), target_status_code=302)

    def test_member_view_not_accessible_by_manager(self):
        request: HttpRequest = self.factory.get('/')
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response: HttpResponse = views.memberPage(request)
        response.client = self.client
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            constants.PAGES.LOGOUT), target_status_code=302)

    def test_download_membership_card_success(self):
        membership = Membership.objects.create(
            membership_card=self.test_image,
            card_number='1234567890',
            membership_type='3',
            issue_date='2022-01-01',
            expire_date='2022-12-31'
        )
        request: HttpRequest = self.factory.get('/')
        group = Group.objects.get(name=constants.GROUPS.MEMBER)
        self.user.groups.add(group)
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response: HttpResponse = views.downloadMembershipCard(
            request, membership.id)
        response.client = self.client
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'],
                         f'inline; filename={membership.card_number}.jpg')
        membership.delete()

    def test_download_membership_card_with_image_not_found(self):
        membership = Membership.objects.create(
            membership_card="path/to/image/not/found",
            card_number='1234567890',
            membership_type='3',
            issue_date='2022-01-01',
            expire_date='2022-12-31'
        )
        request: HttpRequest = self.factory.get('/')
        group = Group.objects.get(name=constants.GROUPS.MEMBER)
        self.user.groups.add(group)
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        self.assertRaises(Http404, views.downloadMembershipCard,
                          request, membership.id)
        membership.delete()

    def test_download_membership_card_with_membership_dose_not_exist(self):
        request: HttpRequest = self.factory.get('/')
        group = Group.objects.get(name=constants.GROUPS.MEMBER)
        self.user.groups.add(group)
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        self.assertRaises(Http404, views.downloadMembershipCard,
                          request, 0)

    def test_member_form_view(self):
        response = self.client.get(
            reverse(constants.PAGES.MEMBER_FORM_PAGE))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, constants.TEMPLATES.MEMBER_FORM_TEMPLATE)

    def test_thank_you_view_success(self):
        AuditEntry.objects.create(
            ip=self.test_ip,
            user_agent=self.user_agent,
            action=constants.ACTION.MEMBER_FORM_POST,
            username=self.user,
            created=timezone.now()
        )
        request: HttpRequest = self.factory.get('/')
        response: HttpResponse = views.thankYou(request)
        self.assertEqual(response.status_code, 200)

    def test_thank_you_view_failed(self):
        request: HttpRequest = self.factory.get('/')
        response: HttpResponse = views.thankYou(request)
        response.client = self.client
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            constants.PAGES.INDEX_PAGE))

    def tearDown(self) -> None:
        try:
            for person in Person.objects.all():
                person.delete()
        except AttributeError:
            pass
        return super().tearDown()
