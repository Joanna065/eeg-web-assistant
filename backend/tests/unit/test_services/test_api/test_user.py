import random
import string
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from eeg_web_assistant import settings
from eeg_web_assistant.models.user import UserInDB
from eeg_web_assistant.services.api import API
from eeg_web_assistant.services.database import Database
from eeg_web_assistant.utils.exceptions import CredentialsError
from eeg_web_assistant.utils.security import get_current_user


class TestUserRouter(unittest.TestCase):
    @staticmethod
    def _get_current_valid_user_mock():
        return UserInDB(first_name='Jan', last_name='Kowalski', email='jkowalski@gmail.com',
                        username='jankowalski', password='securepassword')

    @staticmethod
    def _get_current_invalid_user_mock():
        raise CredentialsError()

    @classmethod
    def setUpClass(cls) -> None:
        api = API.create(config=settings.APIConfig())
        cls.client = TestClient(api.app)

    def test_create_user__return_201(self):
        # GIVEN
        db = MagicMock()
        db.users.find_one_by_username = MagicMock(return_value=None)
        db.users.find_one_by_email = MagicMock(return_value=None)
        db.users.insert_one = MagicMock(return_value=123456)
        self.client.app.dependency_overrides[Database] = lambda: db

        # WHEN
        response = self.client.post(
            '/user',
            json={'first_name': 'Alicja',
                  'last_name': 'Nowak',
                  'email': 'anowak@gmail.com',
                  'username': 'alicja_nowak',
                  'password': 'alicja_password'},
        )

        # THEN
        self.assertEqual(201, response.status_code)
        self.assertEqual(123456, response.json())

    def test_create_user__return_400_duplicate_username(self):
        # GIVEN
        db = MagicMock()
        db.users.find_one_by_username = MagicMock(return_value=...)
        self.client.app.dependency_overrides[Database] = lambda: db

        # WHEN
        response = self.client.post(
            '/user',
            json={'first_name': 'Alicja',
                  'last_name': 'Nowak',
                  'email': 'anowak@gmail.com',
                  'username': 'alicja_nowak',
                  'password': 'alicja_password'},
        )

        # THEN
        self.assertEqual(400, response.status_code)
        self.assertEqual({
            'detail': 'Username is already occupied'
        }, response.json())

    def test_create_user__return_400_duplicate_email(self):
        # GIVEN
        db = MagicMock()
        db.users.find_one_by_username = MagicMock(return_value=None)
        db.users.find_one_by_email = MagicMock(return_value=...)
        self.client.app.dependency_overrides[Database] = lambda: db

        # WHEN
        response = self.client.post(
            '/user',
            json={'first_name': 'Alicja',
                  'last_name': 'Nowak',
                  'email': 'anowak@gmail.com',
                  'username': 'alicja_nowak',
                  'password': 'alicja_password'},
        )

        # THEN
        self.assertEqual(400, response.status_code)
        self.assertEqual({
            'detail': 'Email is already occupied'
        }, response.json())

    def test_create_user__return_422_wrong_email(self):
        # GIVEN
        db = MagicMock()
        db.users.find_one_by_username = MagicMock(return_value=None)
        db.users.find_one_by_email = MagicMock(return_value=None)
        self.client.app.dependency_overrides[Database] = lambda: db

        # WHEN
        response = self.client.post(
            '/user',
            json={'first_name': 'Alicja',
                  'last_name': 'Nowak',
                  'email': 'anowak@g',
                  'username': 'alicja_nowak',
                  'password': 'alicja_password'},
        )

        # THEN
        self.assertEqual(422, response.status_code)
        self.assertIn("['body', 'email']", str(response.json()))

    def test_create_user__return_422_too_short_password(self):
        # GIVEN
        db = MagicMock()
        db.users.find_one_by_username = MagicMock(return_value=None)
        db.users.find_one_by_email = MagicMock(return_value=None)
        self.client.app.dependency_overrides[Database] = lambda: db

        # WHEN
        response = self.client.post(
            '/user',
            json={'first_name': 'Alicja',
                  'last_name': 'Nowak',
                  'email': 'anowak@gmail.com',
                  'username': 'alicja_nowak',
                  'password': '12345'},
        )

        # THEN
        self.assertEqual(422, response.status_code)
        self.assertIn("['body', 'password']", str(response.json()))

    def test_create_user__return_422_too_long_username(self):
        # GIVEN
        db = MagicMock()
        self.client.app.dependency_overrides[Database] = lambda: db

        # WHEN
        response = self.client.post(
            '/user',
            json={'first_name': 'Alicja',
                  'last_name': 'Nowak',
                  'email': 'anowak@gmail.com',
                  'username': ''.join(random.choice(string.ascii_lowercase) for x in range(51)),
                  'password': 'alicja_password'},
        )

        # THEN
        self.assertEqual(422, response.status_code)
        self.assertIn("['body', 'username']", str(response.json()))

    def test_create_user__return_422_not_enough_data(self):
        # GIVEN
        db = MagicMock()
        self.client.app.dependency_overrides[Database] = lambda: db

        # WHEN
        response = self.client.post('/user', json={'first_name': 'Alicja'})

        # THEN
        self.assertEqual(422, response.status_code)
        print(response.json())
        self.assertIn("field required", str(response.json()))

    def test_get_user__return_200(self):
        # GIVEN
        self.client.app.dependency_overrides[get_current_user] = self._get_current_valid_user_mock

        # WHEN
        response = self.client.get('/user')

        # THEN
        self.assertEqual(200, response.status_code)
        self.assertEqual({
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jkowalski@gmail.com',
            'username': 'jankowalski'
        }, response.json())

    def test_get_user__return_401(self):
        # GIVEN
        self.client.app.dependency_overrides[get_current_user] = self._get_current_invalid_user_mock

        # WHEN
        response = self.client.get('/user')

        # THEN
        self.assertEqual(401, response.status_code)
        self.assertEqual({'detail': 'Unable to validate credentials'}, response.json())

    def test_delete_user__return_200(self):
        # GIVEN
        db = MagicMock()
        db.users.find_one_and_delete = MagicMock(return_value={'username': 'jankowalski'})
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_valid_user_mock

        # WHEN
        response = self.client.delete('/user')

        # THEN
        self.assertEqual(200, response.status_code)

    def test_delete_user__return_401(self):
        # GIVEN
        db = MagicMock()
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_invalid_user_mock

        # WHEN
        response = self.client.delete('/user')

        # THEN
        self.assertEqual(401, response.status_code)

    def test_delete_user__return_404(self):
        # GIVEN
        db = MagicMock()
        db.users.find_one_and_delete = MagicMock(return_value=None)
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_valid_user_mock

        # WHEN
        response = self.client.delete('/user')

        # THEN
        self.assertEqual(404, response.status_code)

    def test_update_user_personal_info__return_200(self):
        # GIVEN
        db = MagicMock()
        db.users.find_one_by_email = MagicMock(return_value=None)
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_valid_user_mock

        # WHEN
        response = self.client.patch(
            '/user/personal_info',
            json={'first_name': 'Adam',
                  'last_name': 'Nowak',
                  'email': 'nowak.adam@gmail.com'}
        )

        # THEN
        self.assertEqual(200, response.status_code)

    def test_update_user_personal_info__return_400_duplicated_email(self):
        # GIVEN
        db = MagicMock()
        db.users.find_one_by_email = MagicMock(return_value=...)
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_valid_user_mock

        # WHEN
        response = self.client.patch(
            '/user/personal_info',
            json={'first_name': 'Adam',
                  'last_name': 'Nowak',
                  'email': 'nowak.adam@gmail.com'}
        )

        # THEN
        self.assertEqual(400, response.status_code)
        self.assertEqual({'detail': 'Email is already occupied'}, response.json())

    def test_update_user_personal_info__return_401(self):
        # GIVEN
        db = MagicMock()
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_invalid_user_mock

        # WHEN
        response = self.client.patch('/user/personal_info', json={'first_name': 'Adam'})

        # THEN
        self.assertEqual(401, response.status_code)

    def test_update_user_personal_info__return_404(self):
        # GIVEN
        db = MagicMock()
        db.users.find_one_by_email = MagicMock(return_value=None)
        db.users.find_one_and_update = MagicMock(return_value=None)
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_valid_user_mock

        # WHEN
        response = self.client.patch('/user/personal_info', json={'first_name': 'Adam'})

        # THEN
        self.assertEqual(404, response.status_code)

    def test_update_user_personal_info__return_422_wrong_email(self):
        # GIVEN
        db = MagicMock()
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_valid_user_mock

        # WHEN
        response = self.client.patch('/user/personal_info', json={'email': 'nowak.adam@g'})

        # THEN
        self.assertEqual(422, response.status_code)
        self.assertIn("['body', 'email']", str(response.json()))

    def test_update_user_personal_info__return_422_too_long_first_name(self):
        # GIVEN
        db = MagicMock()
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_valid_user_mock

        # WHEN
        response = self.client.patch(
            '/user/personal_info',
            json={'first_name': ''.join(random.choice(string.ascii_lowercase) for x in range(256))}
        )

        # THEN
        self.assertEqual(422, response.status_code)
        self.assertIn("['body', 'first_name']", str(response.json()))

    @patch('eeg_web_assistant.services.api.routers.user.verify_password',
           MagicMock(return_value=True))
    def test_update_user_password__return_200(self):
        # GIVEN
        db = MagicMock()
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_valid_user_mock

        # WHEN
        response = self.client.patch(
            '/user/password',
            json={'current_password': 'securepassword',
                  'new_password': 'newsecurepassword'}
        )

        # THEN
        self.assertEqual(200, response.status_code)

    @patch('eeg_web_assistant.services.api.routers.user.verify_password',
           MagicMock(return_value=False))
    def test_update_user_password__return_400_not_valid_current_password(self):
        # GIVEN
        db = MagicMock()
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_valid_user_mock

        # WHEN
        response = self.client.patch(
            '/user/password',
            json={'current_password': 'securepassword',
                  'new_password': 'newsecurepassword'}
        )

        # THEN
        self.assertEqual(400, response.status_code)
        self.assertEqual({'detail': 'Current password is not valid'}, response.json())

    def test_update_user_password__return_422_too_short_new_password(self):
        # GIVEN
        db = MagicMock()
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_valid_user_mock

        # WHEN
        response = self.client.patch(
            '/user/password',
            json={'current_password': 'securepassword',
                  'new_password': 'short'}
        )

        # THEN
        self.assertEqual(422, response.status_code)
        self.assertIn("['body', 'new_password']", str(response.json()))
        self.assertIn("'type': 'value_error.any_str.min_length'", str(response.json()))

    def test_update_user_password__return_422_too_long_new_password(self):
        # GIVEN
        db = MagicMock()
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_valid_user_mock

        # WHEN
        response = self.client.patch(
            '/user/password',
            json={'current_password': 'securepassword',
                  'new_password': ''.join(random.choice(string.ascii_lowercase) for x in range(256))
                  }
        )

        # THEN
        self.assertEqual(422, response.status_code)
        self.assertIn("['body', 'new_password']", str(response.json()))
        self.assertIn("'type': 'value_error.any_str.max_length'", str(response.json()))

    def test_update_user_password__return_422_not_enough_data(self):
        # GIVEN
        db = MagicMock()
        self.client.app.dependency_overrides[Database] = lambda: db
        self.client.app.dependency_overrides[get_current_user] = self._get_current_valid_user_mock

        # WHEN
        response = self.client.patch('/user/password', json={'current_password': 'securepassword'})

        # THEN
        print(response.json())
        self.assertEqual(422, response.status_code)
        self.assertIn("['body', 'new_password']", str(response.json()))
        self.assertIn("field required", str(response.json()))
