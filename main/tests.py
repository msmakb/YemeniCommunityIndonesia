import os

from django.conf import settings
from django.contrib.admin import site
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User, AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse, Http404
from django.test import RequestFactory, TestCase, Client, SimpleTestCase
from django.urls import reverse, resolve
from django.utils import timezone
from django.utils.timezone import timedelta, datetime

from member.models import Academic, Person

from . import constants, views
from .admin import AuditEntryAdmin, BlockedClientAdmin, ParameterAdmin
from .cron import setMagicNumber
from .middleware import AllowedClientMiddleware, AllowedUserMiddleware, LoginRequiredMiddleware
from .models import AuditEntry, BlockedClient, Parameter
from .parameters import getParameterValue
from .utils import getClientIp, getUserGroupe, getUserAgent


class TestInitialization(TestCase):

    def test_is_roles_created(self) -> None:
        for group in constants.GROUPS:
            group_in_database: str = Group.objects.get(name=group).name
            self.assertEquals(group_in_database, group)

    def test_is_default_parameters_inserted_to_database(self) -> None:
        num_of_param: int = Parameter.objects.all().count()
        self.assertGreater(num_of_param, 5)

    def test_is_superuser_ceo_created(self) -> None:
        users: QuerySet[User] = User.objects.all()
        self.assertEquals(users.count(), 1)
        self.assertTrue(users.first().is_superuser)


class TestCron(TestCase):

    def setUp(self) -> None:
        self.test_ip: str = "123.123.123.123"
        self.user_agent: str = "Python"

    def test_magic_number_reset_login_failed_attempts(self):
        for i in range(3):
            audit_entry: AuditEntry = AuditEntry.objects.create(
                ip=self.test_ip,
                user_agent=self.user_agent,
                action=constants.ACTION.LOGGED_FAILED
            )
            audit_entry.setCreated(timezone.now() - timedelta(days=10))
        audit_entry: AuditEntry = AuditEntry.objects.create(
            ip=self.test_ip,
            user_agent=self.user_agent,
            action=constants.ACTION.NORMAL_POST
        )
        setMagicNumber()
        self.assertEquals(getParameterValue(constants.PARAMETERS.MAGIC_NUMBER),
                          audit_entry.id)

    def test_magic_number_cleanup_unsuspicious_posts(self):
        for i in range(5):
            audit_entry: AuditEntry = AuditEntry.objects.create(
                ip=self.test_ip,
                user_agent=self.user_agent,
                action=constants.ACTION.NORMAL_POST
            )
            audit_entry.setCreated(timezone.now() - timedelta(days=10))
        AuditEntry.objects.create(
            ip=self.test_ip,
            user_agent=self.user_agent,
            action=constants.ACTION.NORMAL_POST
        )
        setMagicNumber()
        self.assertEquals(AuditEntry.objects.all().count(), 1)

    def tearDown(self) -> None:
        for row in AuditEntry.objects.all():
            try:
                row.delete("")
            except:
                row.delete()
        return super().tearDown()


class TestAllowedClientMiddleware(TestCase):

    def setUp(self) -> None:
        self.middleware = AllowedClientMiddleware(lambda request: None)
        self.client = RequestFactory()
        self.test_ip: str = "123.123.123.123"
        self.user_agent: str = "Python"
        self.client.defaults['REMOTE_ADDR'] = self.test_ip
        self.client.defaults['HTTP_USER_AGENT'] = self.user_agent
        self.anonymous_user = AnonymousUser()
        self.logged_superuser_admin: User = User.objects.first()
        self.logged_superuser_admin.last_login = datetime.now()

    def test_first_visit_recorded(self) -> None:
        request: HttpRequest = self.client.get(reverse("admin:index"))
        request.user = self.logged_superuser_admin
        self.assertIsNone(self.middleware.__call__(request))
        first_visit: QuerySet[AuditEntry] = AuditEntry.objects.filter(
            action=constants.ACTION.FIRST_VISIT)
        self.assertIsNotNone(first_visit)
        self.assertEquals(first_visit.first().ip, self.test_ip)

    def test_spam_post_request(self):
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.INDEX_PAGE))
        request.user = self.anonymous_user
        request.method = constants.POST_METHOD
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        session_middleware = SessionMiddleware(lambda request: None)
        session_middleware.process_request(request)
        request.session.save()
        self.middleware.__call__(request)
        response: HttpResponse = self.middleware.__call__(request)
        self.assertEquals(response.status_code, 302)
        for i in range(3):
            self.middleware.__call__(request)
        response.client = Client()
        self.assertEquals(response.status_code, 302)
        request.method = constants.GET_METHOD
        response: HttpResponse = self.middleware.__call__(request)
        self.assertEquals(response.status_code, 403)
        self.assertEquals(BlockedClient.objects.filter(ip=self.test_ip).last().block_type,
                          constants.BLOCK_TYPES.TEMPORARY)
        request.method = constants.POST_METHOD
        for i in range(3):
            self.middleware.__call__(request)
        self.assertEquals(BlockedClient.objects.filter(ip=self.test_ip).last().block_type,
                          constants.BLOCK_TYPES.INDEFINITELY)

    def test_blocked_client(self) -> None:
        BlockedClient.objects.create(
            ip=self.test_ip,
            user_agent=self.user_agent,
            block_type=constants.BLOCK_TYPES.TEMPORARY
        )
        request: HttpRequest = self.client.get(constants.PAGES.INDEX_PAGE)
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.__call__(request)
        self.assertEquals(response.status_code, 403)

    def test_blocked_client_and_allowed_to_be_unblocked(self) -> None:
        BlockedClient.objects.create(
            ip=self.test_ip,
            user_agent=self.user_agent,
            block_type=constants.BLOCK_TYPES.TEMPORARY
        )
        BlockedClient.objects.filter().update(
            updated=timezone.now() - timedelta(days=100))
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.ABOUT_PAGE))
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.__call__(request)
        response.client = Client()
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse(constants.PAGES.ABOUT_PAGE))

    def test_block_client_who_filed_to_login_many_times(self) -> None:
        for i in range(5):
            AuditEntry.objects.create(
                ip=self.test_ip,
                user_agent=self.user_agent,
                action=constants.ACTION.LOGGED_FAILED
            )
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.INDEX_PAGE))
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.__call__(request)
        response.client = Client()
        self.assertEquals(response.status_code, 302)
        response: HttpResponse = self.middleware.__call__(request)
        self.assertEquals(response.status_code, 403)

    def tearDown(self) -> None:
        for row in AuditEntry.objects.all():
            try:
                row.delete("")
            except:
                row.delete()
        for row in BlockedClient.objects.all():
            try:
                row.delete("")
            except:
                row.delete()
        return super().tearDown()


class TestLoginRequiredMiddleware(TestCase):

    def setUp(self) -> None:
        self.middleware = LoginRequiredMiddleware(lambda request: None)
        self.client = RequestFactory()
        self.test_ip: str = "123.123.123.123"
        self.user_agent: str = "Python"
        self.client.defaults['REMOTE_ADDR'] = self.test_ip
        self.client.defaults['HTTP_USER_AGENT'] = self.user_agent
        self.anonymous_user = AnonymousUser()
        self.logged_superuser_admin: User = User.objects.first()
        self.logged_superuser_admin.last_login = datetime.now()

    def test_anonymous_user_trying_to_access_admin_site(self) -> None:
        request: HttpRequest = self.client.get(reverse("admin:index"))
        request.user = self.anonymous_user
        self.assertRaises(Http404, self.middleware.process_view, request)

    def test_superuser_trying_to_access_admin_site(self):
        request: HttpRequest = self.client.get(reverse("admin:index"))
        request.user = self.logged_superuser_admin
        self.assertIsNone(self.middleware.process_view(request))

    def test_access_login_required_page(self) -> None:
        user = User.objects.create_user(
            username='TestMemberUSer',
            password='TestPass'
        )
        group = Group.objects.get(name=constants.GROUPS.MEMBER)
        user.groups.add(group)
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.MEMBER_PAGE))
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.process_view(request)
        response.client = Client()
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse(
            constants.PAGES.UNAUTHORIZED_PAGE))

        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.DASHBOARD, args=['list']))
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.process_view(request)
        response.client = Client()
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse(
            constants.PAGES.UNAUTHORIZED_PAGE))

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
        )
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.DETAIL_MEMBER_PAGE, args=[person.id]))
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.process_view(request)
        response.client = Client()
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse(
            constants.PAGES.UNAUTHORIZED_PAGE))

    def test_access_excluded_pages_from_login(self) -> None:
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.INDEX_PAGE))
        request.user = self.anonymous_user
        self.assertIsNone(self.middleware.process_view(request))

        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.ABOUT_PAGE))
        request.user = self.anonymous_user
        self.assertIsNone(self.middleware.process_view(request))

    def test_is_user_session_timeout(self) -> None:
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.INDEX_PAGE))
        request.user = self.logged_superuser_admin
        self.assertIsNone(self.middleware.process_view(request))

        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.INDEX_PAGE))
        request.user = self.logged_superuser_admin
        request.user.last_login = timezone.now() - timedelta(minutes=1500)
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        session_middleware = SessionMiddleware(lambda request: None)
        session_middleware.process_request(request)
        request.session.save()
        response: HttpResponse = self.middleware.process_view(request)
        response.client = Client()
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse(constants.PAGES.INDEX_PAGE))


class TestAllowedUserMiddleware(TestCase):

    def setUp(self) -> None:
        self.middleware = AllowedUserMiddleware(lambda request: None)
        self.client = RequestFactory()
        self.test_ip: str = "123.123.123.123"
        self.user_agent: str = "Python"
        self.client.defaults['REMOTE_ADDR'] = self.test_ip
        self.client.defaults['HTTP_USER_AGENT'] = self.user_agent
        self.anonymous_user = AnonymousUser()
        self.logged_superuser_admin: User = User.objects.first()
        self.logged_non_superuser: User = User.objects.create_user(
            username="TestUser",
            password="TestPass"
        )
        self.logged_non_superuser.username = "NonSuperuser"
        self.logged_non_superuser.save()
        group = Group.objects.get(name=constants.GROUPS.MEMBER)
        self.logged_non_superuser.groups.add(group)
        self.logged_superuser_admin.last_login = datetime.now()
        self.logged_non_superuser.last_login = datetime.now()
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
            account=self.logged_non_superuser
        )

    def test_is_allowed_to_access_admin(self) -> None:
        request: HttpRequest = self.client.get(reverse("admin:index"))
        request.user = self.logged_superuser_admin
        self.assertTrue(self.middleware.isAllowedToAccessAdmin(request))
        request: HttpRequest = self.client.get(reverse("admin:index"))
        request.user = self.anonymous_user
        self.assertFalse(self.middleware.isAllowedToAccessAdmin(request))
        request: HttpRequest = self.client.get(reverse("admin:index"))
        group = Group.objects.get(name=constants.GROUPS.MEMBER)
        user = User.objects.create(username='testuser')
        user.groups.add(group)
        request.user = user
        self.assertEquals(request.user.groups.first().name,
                          constants.GROUPS.MEMBER)
        self.assertFalse(self.middleware.isAllowedToAccessAdmin(request))

    def test_doing_nothing_if_user_is_not_authenticated(self) -> None:
        """This middleware for authenticated users only"""
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.ABOUT_PAGE))
        request.user = self.anonymous_user
        self.assertIsNone(self.middleware.process_view(request))

    def test_allowed_user_to_access_page(self) -> None:
        self.logged_superuser_admin.username = "allowed-user"
        self.logged_superuser_admin.save()

        def process_session(request: HttpRequest) -> HttpRequest:
            setattr(request, 'session', 'session')
            setattr(request, '_messages', FallbackStorage(request))
            session_middleware = SessionMiddleware(lambda request: None)
            session_middleware.process_request(request)
            request.session.save()
            return request

        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.DASHBOARD, args=['list']))
        request = process_session(request)
        request.user = self.logged_superuser_admin
        self.assertIsNone(self.middleware.process_view(request))

        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.DETAIL_MEMBER_PAGE, args=[self.person.pk]))
        request = process_session(request)
        request.user = self.logged_superuser_admin
        self.assertIsNone(self.middleware.process_view(request))

        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.MEMBER_PAGE))
        request = process_session(request)
        request.user = self.logged_non_superuser
        self.assertEquals(request.user.groups.first().name,
                          constants.GROUPS.MEMBER)
        self.assertIsNone(self.middleware.process_view(request))

    def test_not_allowed_user_to_access_page(self) -> None:
        self.logged_superuser_admin.username = "allowed-user"
        self.logged_superuser_admin.save()

        def process_session_request_and_response(request: HttpRequest, user: User) -> tuple[HttpRequest, HttpResponse]:
            setattr(request, 'session', 'session')
            setattr(request, '_messages', FallbackStorage(request))
            session_middleware = SessionMiddleware(lambda request: None)
            session_middleware.process_request(request)
            request.session.save()
            request.user = user
            response: HttpResponse = self.middleware.process_view(request)
            response.client = Client()
            return request, response

        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.MEMBER_PAGE))
        request, response = process_session_request_and_response(
            request, self.logged_superuser_admin)
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse(
            constants.PAGES.UNAUTHORIZED_PAGE))

        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.DETAIL_MEMBER_PAGE, args=[self.person.pk]))
        request, response = process_session_request_and_response(
            request, self.logged_non_superuser)
        self.assertEquals(request.user.groups.first().name,
                          constants.GROUPS.MEMBER)
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse(
            constants.PAGES.UNAUTHORIZED_PAGE))

        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.DASHBOARD, args=['list']))
        request, response = process_session_request_and_response(
            request, self.logged_non_superuser)
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse(
            constants.PAGES.UNAUTHORIZED_PAGE))

        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.DASHBOARD, args=['approve']))
        request, response = process_session_request_and_response(
            request, self.logged_non_superuser)
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse(
            constants.PAGES.UNAUTHORIZED_PAGE))

    def test_non_superuser_trying_to_access_admin(self) -> None:
        request: HttpRequest = self.client.get(reverse("admin:index"))
        request.user = self.logged_non_superuser
        self.assertRaises(Http404, self.middleware.process_view, request)

    def test_user_is_in_unauthenticated_page_error(self) -> None:
        """
        If user in the page error that the system redirected
        him after trying to access unauthenticated page.
        """
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.UNAUTHORIZED_PAGE))
        request.user = self.logged_non_superuser
        self.assertIsNone(self.middleware.process_view(request))

    def test_user_has_no_groups(self) -> None:
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.INDEX_PAGE))
        request.user = self.logged_non_superuser
        request.user.groups.clear()
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        session_middleware = SessionMiddleware(lambda request: None)
        session_middleware.process_request(request)
        request.session.save()
        response: HttpResponse = self.middleware.process_view(request)
        response.client = Client()
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse(constants.PAGES.LOGOUT),
                             target_status_code=302)


class TestModels(TestCase):

    def setUp(self) -> None:
        self.test_model = Academic.objects.create(
            academic_qualification="1"
        )

    def test_base_model_create(self) -> None:
        test_model = Academic.create(
            academic_qualification="2"
        )
        self.assertEquals(test_model.academic_qualification, "2")

    def test_base_model_delete(self) -> None:
        id: int = self.test_model.id
        self.test_model.delete()
        try:
            test_model = Academic.objects.get(id=id)
        except Academic.DoesNotExist:
            test_model = None
        self.assertIsNone(test_model)

    def test_base_model_get(self) -> None:
        id: int = self.test_model.id
        test_model = Academic.get(id=id)
        self.assertEquals(self.test_model, test_model)
        for i in range(5):
            Academic.objects.create(academic_qualification="3")
        test_model = Academic.get(academic_qualification="3")
        self.assertIsNone(test_model)

    def test_base_model_get_all(self) -> None:
        existing_objects_count: int = Academic.objects.all().count()
        for i in range(5):
            Academic.objects.create(academic_qualification=f"{i}")
        objects: QuerySet[Academic] = Academic.getAll()
        self.assertEquals(objects.count(), existing_objects_count + 5)

    def test_base_model_get_all_ordered(self) -> None:
        for i in Academic.objects.all():
            i.delete()
        for i in range(5):
            Academic.objects.create(academic_qualification=str(chr(97 + i)))
        object: QuerySet[Academic] = Academic.getAllOrdered(
            "academic_qualification", reverse=True).reverse()
        for i in range(5):
            self.assertEquals(
                object[i].academic_qualification, str(chr(97 + i)))

    def test_base_model_get_last_inserted_object(self) -> None:
        Academic.objects.create(academic_qualification="5")
        test_model: Academic = Academic.getLastInsertedObject()
        self.assertEquals(test_model.academic_qualification, "5")
        for i in range(3):
            Academic.objects.create(
                academic_qualification=str(i + 6), school="Test")
        objects: QuerySet[Academic] = Academic.objects.filter(
            school="Test").reverse()
        test_model: Academic = Academic.getLastInsertedObject(objects)
        self.assertEquals(test_model.academic_qualification, "6")

    def test_base_model_filter(self) -> None:
        for i in Academic.objects.all():
            i.delete()
        for i in range(5):
            Academic.objects.create(academic_qualification="1")
        objects: QuerySet[Academic] = Academic.filter(
            academic_qualification="1")
        self.assertEquals(objects.count(), 5)
        self.assertEquals(objects.first().academic_qualification, "1")

    def test_base_model_count_all(self) -> None:
        self.assertEquals(Academic.objects.all().count(), Academic.countAll())

    def test_base_model_count_filtered(self) -> None:
        Academic.objects.create(academic_qualification="1")
        for i in range(5):
            Academic.objects.create(academic_qualification="2")
        self.assertEquals(Academic.countFiltered(
            academic_qualification="2"), 5)

    def test_base_model_is_exists(self) -> None:
        Academic.objects.create(academic_qualification="9")
        self.assertTrue(Academic.isExists(academic_qualification="9"))
        self.assertFalse(Academic.isExists(academic_qualification="8"))


class AuditEntryAdminTest(TestCase):

    def setUp(self):
        self.admin = AuditEntryAdmin(AuditEntry, None)
        self.user = User.objects.create_superuser(username='testuser')
        self.audit_entry = AuditEntry.objects.create(
            ip='1.2.3.4', username='testuser', action='test action')

    def test_list_display(self):
        self.assertEqual(self.admin.list_display, ('action', 'user_agent', 'username', 'ip',
                                                   'created', 'updated'))

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter, ('action', 'created'))

    def test_search_fields(self):
        self.assertEqual(self.admin.search_fields,
                         ('action', 'user_agent', 'username', 'ip'))

    def test_exclude(self):
        self.assertEqual(self.admin.exclude, ('created', 'updated'))

    def test_has_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(None))

    def test_has_change_permission(self):
        self.assertFalse(self.admin.has_change_permission(None))


class BlockedClientAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.blocked_client = BlockedClient.objects.create(
            user_agent='Test User Agent',
            ip='127.0.0.1',
            block_type=constants.BLOCK_TYPES.TEMPORARY,
            blocked_times=5
        )
        self.admin = BlockedClientAdmin(BlockedClient, self.admin_site)

    def test_blockType_method(self):
        self.assertEqual(self.admin.blockType(self.blocked_client), 'مؤقت')

    def test_has_add_permission_method(self):
        request = self.factory.get('/')
        self.assertFalse(self.admin.has_add_permission(request))


class ParameterAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = ParameterAdmin(Parameter, site)
        self.user = User.objects.get(username='admin')

    def test_parameter_list_view(self):
        request = self.factory.get(reverse('admin:main_parameter_changelist'))
        request.user = self.user
        response = self.admin.changelist_view(request)
        self.assertEqual(response.status_code, 200)

    def test_parameter_detail_view(self):
        parameter = Parameter.objects.create(
            name='testparam',
            value='testvalue',
            access_type=constants.ACCESS_TYPE.ADMIN_ACCESS
        )
        request = self.factory.get(
            reverse('admin:main_parameter_change', args=(parameter.pk,)))
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = self.admin.change_view(request, str(parameter.pk))
        self.assertEqual(response.status_code, 200)

    def test_parameter_detail_view_no_admin_access(self):
        parameter = Parameter.objects.create(
            name='testparam',
            value='testvalue',
            access_type=constants.ACCESS_TYPE.No_ACCESS
        )
        request = self.factory.get(
            reverse('admin:main_parameter_change', args=(parameter.pk,)))
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = self.admin.change_view(request, str(parameter.pk))
        response.client = Client()
        self.assertEqual(response.status_code, 302)


class TestParameter(TestCase):

    def test_non_exciting_parameter(self) -> None:
        self.assertRaises(KeyError, getParameterValue,
                          "NON_EXISTING_PARAMETER")

    def test_string_type_parameter(self) -> None:
        string_param: Parameter = Parameter.objects.create(
            name="TEST_PARAM_STRING",
            value="TEST_STRING",
            parameter_type=constants.DATA_TYPE.STRING,
        )
        self.assertIsInstance(getParameterValue("TEST_PARAM_STRING"), str)
        self.assertEquals(getParameterValue("TEST_PARAM_STRING"),
                          "TEST_STRING")
        string_param.value = "1"
        string_param.save()
        self.assertIsInstance(getParameterValue("TEST_PARAM_STRING"), str)

    def test_integer_type_parameter(self) -> None:
        integer_param: Parameter = Parameter.objects.create(
            name="TEST_PARAM_INTEGER",
            value="1",
            parameter_type=constants.DATA_TYPE.INTEGER,
        )
        self.assertIsInstance(getParameterValue("TEST_PARAM_INTEGER"), int)
        self.assertEquals(getParameterValue("TEST_PARAM_INTEGER"), 1)
        integer_param.value = "Wrong data type"
        integer_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_INTEGER")
        integer_param.value = "1.03"  # float
        integer_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_INTEGER")

    def test_float_type_parameter(self) -> None:
        float_param: Parameter = Parameter.objects.create(
            name="TEST_PARAM_FLOAT",
            value="1.05",
            parameter_type=constants.DATA_TYPE.FLOAT,
        )
        self.assertIsInstance(getParameterValue("TEST_PARAM_FLOAT"), float)
        self.assertEquals(getParameterValue("TEST_PARAM_FLOAT"), 1.05)
        float_param.value = "Wrong data type"
        float_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_FLOAT")

    def test_boolean_type_parameter(self) -> None:
        boolean_param: Parameter = Parameter.objects.create(
            name="TEST_PARAM_BOOLEAN",
            value="True",
            parameter_type=constants.DATA_TYPE.BOOLEAN,
        )
        self.assertIsInstance(getParameterValue("TEST_PARAM_BOOLEAN"), bool)
        self.assertTrue(getParameterValue("TEST_PARAM_BOOLEAN"), True)
        boolean_param.value = "true"
        boolean_param.save()
        self.assertTrue(getParameterValue("TEST_PARAM_BOOLEAN"))
        boolean_param.value = "YES"
        boolean_param.save()
        self.assertTrue(getParameterValue("TEST_PARAM_BOOLEAN"))
        boolean_param.value = "1"
        boolean_param.save()
        self.assertTrue(getParameterValue("TEST_PARAM_BOOLEAN"))
        boolean_param.value = "FaLsE"
        boolean_param.save()
        self.assertFalse(getParameterValue("TEST_PARAM_BOOLEAN"))
        boolean_param.value = "nO"
        boolean_param.save()
        self.assertFalse(getParameterValue("TEST_PARAM_BOOLEAN"))
        boolean_param.value = "0"
        boolean_param.save()
        self.assertFalse(getParameterValue("TEST_PARAM_BOOLEAN"))
        boolean_param.value = "Fales"  # Wrong spilling of False
        boolean_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_BOOLEAN")
        boolean_param.value = "-1"
        boolean_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_BOOLEAN")
        boolean_param.value = "2"
        boolean_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_BOOLEAN")
        boolean_param.value = "ya"
        boolean_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_BOOLEAN")

    def test_non_existing_param_in_database_but_exists_in_default_param(self) -> None:
        self.assertEquals(getParameterValue("TEST"), "TEST_PARAMETER")
        self.assertIsInstance(getParameterValue("TEST"), str)


class TestUtils(TestCase):

    def setUp(self) -> None:
        self.test_engine_name: str = "Test Engine"
        self.request = HttpRequest()
        self.request.user: User = User.objects.first()
        self.test_ip: str = "123.123.123.123"
        self.user_agent: str = "Python"
        self.request.META["REMOTE_ADDR"] = self.test_ip
        self.request.META["HTTP_USER_AGENT"] = self.user_agent

    def test_get_user_group(self) -> None:
        group: str = getUserGroupe(self.request.user)
        self.assertIsNotNone(group)
        self.assertIn(group, constants.GROUPS)

    def test_get_client_ip(self) -> None:
        self.assertEquals(getClientIp(self.request), self.test_ip)

    def test_get_user_agent(self) -> None:
        self.assertEquals(getUserAgent(self.request), self.user_agent)


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )
        group = Group.objects.get(name=constants.GROUPS.MANAGER)
        self.user.groups.add(group)

    def test_login_success(self):
        request = self.factory.post(reverse(constants.PAGES.LOGIN_PAGE), {
            'user_name': 'testuser',
            'password': 'testpassword'
        })
        request.user = self.user
        response = views.loginPage(request)
        response.client = Client()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            constants.PAGES.DASHBOARD, args=['list']), target_status_code=302)

    def test_login_failure(self):
        request = self.factory.post(reverse(constants.PAGES.LOGIN_PAGE), {
            'user_name': 'testuser',
            'password': 'wrongPassword'
        })
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = views.loginPage(request)
        self.assertIsInstance(response, HttpResponseRedirect)

    def test_membership_terms_view(self):
        response = self.client.get(
            reverse(constants.PAGES.MEMBERSHIP_TERMS_PAGE))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, constants.TEMPLATES.MEMBERSHIP_TERMS_TEMPLATE)

    def test_about_view(self):
        response = self.client.get(reverse(constants.PAGES.ABOUT_PAGE))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, constants.TEMPLATES.ABOUT_TEMPLATE)

    def test_logout_user_view(self):
        request = self.factory.get(reverse(constants.PAGES.LOGOUT))
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = views.logoutUser(request)
        response.client = Client()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(constants.PAGES.LOGIN_PAGE))

    def test_unauthorized_view(self):
        response = self.client.get(reverse(constants.PAGES.UNAUTHORIZED_PAGE))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, constants.TEMPLATES.UNAUTHORIZED_TEMPLATE)


class UrlsTestCase(TestCase):
    def test_index_url(self):
        url = reverse(constants.PAGES.INDEX_PAGE)
        self.assertEqual(url, '/')
        self.assertEqual(resolve(url).func, views.index)

    def test_login_url(self):
        url = reverse(constants.PAGES.LOGIN_PAGE)
        self.assertEqual(url, '/Login/')
        self.assertEqual(resolve(url).func, views.loginPage)

    def test_unauthorized_url(self):
        url = reverse(constants.PAGES.UNAUTHORIZED_PAGE)
        self.assertEqual(url, '/Error/')
        self.assertEqual(resolve(url).func, views.unauthorized)

    def test_membership_terms_url(self):
        url = reverse(constants.PAGES.MEMBERSHIP_TERMS_PAGE)
        self.assertEqual(url, '/MembershipTerms/')
        self.assertEqual(resolve(url).func, views.membershipTerms)

    def test_about_url(self):
        url = reverse(constants.PAGES.ABOUT_PAGE)
        self.assertEqual(url, '/About/')
        self.assertEqual(resolve(url).func, views.about)

    def test_logout_url(self):
        url = reverse(constants.PAGES.LOGOUT)
        self.assertEqual(url, '/Logout/')
        self.assertEqual(resolve(url).func, views.logoutUser)


class ImageFilesExistsTest(SimpleTestCase):

    def test_membership_template_exists(self):
        path = os.path.join(settings.MEDIA_ROOT,
                            "templates/membership_template.jpg")
        self.assertTrue(os.path.exists(path))

    def test_female_no_image_exists(self):
        path = os.path.join(settings.MEDIA_ROOT,
                            "templates/female_no_image.jpg")
        self.assertTrue(os.path.exists(path))

    def test_logo_exists(self):
        path = os.path.join(settings.STATICFILES_DIRS[0],
                            "img/logo.jpg")
        self.assertTrue(os.path.exists(path))

    def test_photo_roles_exists(self):
        path = os.path.join(settings.STATICFILES_DIRS[0],
                            "img/photo_roles.jpg")
        self.assertTrue(os.path.exists(path))
