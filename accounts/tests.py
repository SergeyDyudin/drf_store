import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser, Profile, Region


class TestCreateCustomUser(APITestCase):
    def test_create_user(self):
        url = reverse('accounts:user-list')
        data = {
                'first_name': 'test',
                'last_name': 'user',
                'email': 'foo@bar.com',
                'password': 'Qw789456',
                'password2': 'Qw789456',
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().email, 'foo@bar.com')

    def test_custom_registration_action(self):
        url = reverse('accounts:user-registration')
        data = {
            'email': 'foo@bar.com',
            'password': 'Qw789456',
            'password2': 'Qw789456',
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().email, 'foo@bar.com')


class TestCustomUser(APITestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(email='foo@bar.com', password='Qw789456')
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token

    def test_change_password_without_auth(self):
        url = reverse('accounts:user-change-password', kwargs={'pk': self.user.pk})
        data = {
            'old_password': 'Qw789456',
            'new_password1': 'Qw7894567',
            'new_password2': 'Qw7894567'
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password(self):
        url = reverse('accounts:user-change-password', kwargs={'pk': self.user.pk})
        data = {
            'old_password': 'Qw789456',
            'new_password1': 'Qw7894567',
            'new_password2': 'Qw7894567'
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Qw7894567'))

    def test_update_account_data(self):
        url = reverse('accounts:user-detail', kwargs={'pk': self.user.pk})
        data = {
            'first_name': 'test',
            'last_name': 'user',
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.patch(url, data, format='json')
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, 'test')
        self.assertEqual(self.user.last_name, 'user')

    def test_update_account_data_without_auth(self):
        url = reverse('accounts:user-detail', kwargs={'pk': self.user.pk})
        data = {
            'first_name': 'test',
            'last_name': 'user',
        }
        response = self.client.patch(url, data, format='json')
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.user.first_name, '')
        self.assertEqual(self.user.last_name, '')

    def test_update_account_data_wrong_user(self):
        url = reverse('accounts:user-detail', kwargs={'pk': self.user.pk})
        data = {
            'first_name': 'test',
            'last_name': 'user',
        }

        user = CustomUser.objects.create_user(email='evil@bar.com', password='Qw789456')
        access_token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.patch(url, data, format='json')
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.user.first_name, '')
        self.assertEqual(self.user.last_name, '')

    def test_get_account_data(self):
        url = reverse('accounts:user-detail', kwargs={'pk': self.user.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profile', response.data)

    def test_get_account_data_without_auth(self):
        url = reverse('accounts:user-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_account_data_wrong_user(self):
        """Try to get data of different user"""
        url = reverse('accounts:user-detail', kwargs={'pk': self.user.pk})

        user = CustomUser.objects.create_user(email='evil@bar.com', password='Qw789456')
        access_token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_list_with_perm(self):
        """Required permission is_staff"""
        self.user.is_staff = True
        self.user.save()

        CustomUser.objects.create_user(email='evil@bar.com', password='Qw789456')

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.get(reverse('accounts:user-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_user_list_without_perm(self):
        """Access denied without is_staff permission"""
        CustomUser.objects.create_user(email='evil@bar.com', password='Qw789456')

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.get(reverse('accounts:user-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_list_without_auth(self):
        """Access available only with auth and is_staff perm"""
        CustomUser.objects.create_user(email='evil@bar.com', password='Qw789456')

        response = self.client.get(reverse('accounts:user-list'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.post(reverse('accounts:user-logout'))

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer abc')

        response = self.client.post(reverse('accounts:user-logout'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_auth(self):
        response = self.client.post(reverse('accounts:user-logout'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestProfile(APITestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(email='foo@bar.com', password='Qw789456')
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token

    def test_get_profile(self):
        """Check that profile creates with account"""
        self.assertTrue(Profile.objects.filter(user__pk=self.user.pk).exists())

    def test_get_profile_data(self):
        url = reverse('accounts:profile-detail', kwargs={'pk': self.user.profile.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile_data_without_auth(self):
        url = reverse('accounts:profile-detail', kwargs={'pk': self.user.profile.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_data_wrong_user(self):
        """Try to get data of different user"""
        url = reverse('accounts:profile-detail', kwargs={'pk': self.user.profile.pk})

        user = CustomUser.objects.create_user(email='evil@bar.com', password='Qw7894567')
        access_token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_profile_data(self):
        url = reverse('accounts:user-detail', kwargs={'pk': self.user.pk})
        data = {
            'profile':
                {
                    'phone': '89999999999',
                    'birthday': '2000-02-02',
                }
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.patch(url, data, format='json')

        print(response.json())
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.profile.phone, '89999999999')
        self.assertEqual(self.user.profile.birthday,  datetime.date(2000, 2, 2))

    def test_update_profile_data_without_auth(self):
        url = reverse('accounts:user-detail', kwargs={'pk': self.user.pk})
        data = {
            'profile':
                {
                    'phone': '89999999999',
                    'birthday': '2000-02-02',
                }
        }
        response = self.client.patch(url, data, format='json')
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.user.profile.phone, '')
        self.assertIsNone(self.user.profile.birthday)

    def test_update_profile_data_wrong_user(self):
        url = reverse('accounts:user-detail', kwargs={'pk': self.user.pk})
        data = {
            'profile':
                {
                    'phone': '89999999999',
                    'birthday': '2000-02-02',
                }
        }

        user = CustomUser.objects.create_user(email='evil@bar.com', password='Qw7894567')
        access_token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.patch(url, data, format='json')
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.user.profile.phone, '')
        self.assertIsNone(self.user.profile.birthday)

    def test_email_not_confirmed(self):
        """Email isn't confirm for a new user"""
        self.assertFalse(self.user.profile.email_confirmed)

    def test_empty_currency(self):
        """Currency must be empty for a new user"""
        self.assertEqual(self.user.profile.currency, 0)

    def test_get_list_profiles_with_perm(self):
        self.user.is_staff = True
        self.user.save()

        url = reverse('accounts:profile-list')

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_profiles_without_perm(self):
        url = reverse('accounts:profile-list')

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_list_profiles_without_auth(self):
        url = reverse('accounts:profile-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestRegion(APITestCase):
    def test_uploading_regions_from_csv(self):
        """Checking work to_python migration"""
        self.assertTrue(Region.objects.exists())


class TestTokens(APITestCase):
    @classmethod
    def setUpTestData(cls):
        CustomUser.objects.create_user(email='foo@bar.com', password='Qw789456')

    def setUp(self) -> None:
        self.url = reverse('token_obtain_pair')
        self.data = {'email': 'foo@bar.com', 'password': 'Qw789456'}

    def test_get_tokens(self):
        response = self.client.post(self.url, self.data, format='json').json()
        self.assertIn('refresh', response)
        self.assertIn('access', response)

    def test_refresh_access_token(self):
        refresh_token = self.client.post(self.url, self.data, format='json').json()['refresh']

        response = self.client.post(reverse('token_refresh'), {'refresh': refresh_token})
        self.assertIn('access', response.json())
