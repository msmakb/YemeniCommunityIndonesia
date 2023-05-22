from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase, Client
from django.urls import reverse

from main import constants

from .admin import ParameterAdmin
from .models import Parameter
from .service import getParameterValue


class TestInitialization(TestCase):

    def test_is_default_parameters_inserted_to_database(self) -> None:
        num_of_param: int = Parameter.objects.all().count()
        self.assertGreater(num_of_param, 5)


class ParameterAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = ParameterAdmin(Parameter, site)
        self.user = User.objects.get(username='admin')

    def test_parameter_list_view(self):
        request = self.factory.get(reverse('admin:parameter_parameter_changelist'))
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
            reverse('admin:parameter_parameter_change', args=(parameter.pk,)))
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
            reverse('admin:parameter_parameter_change', args=(parameter.pk,)))
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
