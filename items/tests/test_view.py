from random import randint

import pytest
from rest_framework import status
from rest_framework.reverse import reverse


class TestBookViewSet:
    @pytest.fixture(autouse=True)
    def initial(self, api_client, book_factory, author_factory, genre_factory):
        self.client = api_client()
        self.books = book_factory(5)
        self.authors = author_factory(5)
        self.genres = genre_factory(5)

    @pytest.mark.parametrize('token, expected_status', [
        (pytest.lazy_fixture('access_token_admin'), status.HTTP_201_CREATED),
        (pytest.lazy_fixture('access_token_adult_user'), status.HTTP_403_FORBIDDEN),
        ('invalid', status.HTTP_401_UNAUTHORIZED),
        (None, status.HTTP_401_UNAUTHORIZED)
    ])
    def test_create_book(self, token, expected_status):
        url = reverse('items:book-list')
        data = {
            'title': 'Test title',
            'price': randint(100, 5000),
            'year': f'{randint(1000, 2022)}-{randint(1, 12)}-{randint(1, 28)}',
            'language': self.books[0].language_id,
            'publisher': self.books[0].publisher_id,
            'author': [self.authors[0].id, ],
            'genre': [self.genres[0].id, ],
            'slug': 'test-title'
        }
        if token:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(url, data)

        assert response.status_code == expected_status
        if response.status_code == status.HTTP_201_CREATED:
            for item in data:
                assert item in response.data

    def test_get_list_books(self):
        url = reverse('items:book-list')
        response = self.client.get(url)

        assert len(response.data) == 5

    @pytest.mark.parametrize('token, expected_status, quantity', [
        (pytest.lazy_fixture('access_token_admin'), status.HTTP_200_OK, 5),
        (pytest.lazy_fixture('access_token_adult_user'), status.HTTP_200_OK, 5),
        (None, status.HTTP_200_OK, 4)
    ])
    def test_get_list_adult_book(self, token, expected_status, quantity, adult_category):
        url = reverse('items:book-list')
        self.books[0].categories.add(adult_category)
        if token:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        print(self.books[0].categories)
        response = self.client.get(url)

        assert response.status_code == expected_status
        assert len(response.data) == quantity

    def test_get_book(self):
        url = reverse('items:book-detail', kwargs={'pk': self.books[0].pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize('token, expected_status', [
        (pytest.lazy_fixture('access_token_admin'), status.HTTP_200_OK),
        (pytest.lazy_fixture('access_token_adult_user'), status.HTTP_200_OK),
        (None, status.HTTP_404_NOT_FOUND)
    ])
    def test_get_adult_book(self, adult_category, token, expected_status):
        self.books[0].categories.add(adult_category)
        url = reverse('items:book-detail', kwargs={'pk': self.books[0].pk})

        if token:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get(url)

        assert response.status_code == expected_status

    def test_get_books_by_category(self, category_factory):
        url = reverse('items:book-list')
        categories = category_factory(2)
        self.books[0].categories.add(*categories)
        self.books[1].categories.add(*categories)
        self.books[2].categories.add(categories[0])

        response = self.client.get(url, data={'categories__name': categories[0]})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3


class TestCategories:

    @pytest.fixture(autouse=True)
    def initial(self, api_client, category_factory, adult_category):
        self.client = api_client()
        self.url = reverse('items:category-list')
        self.adult_category = adult_category
        self.categories = category_factory(5) + [self.adult_category]

    @pytest.mark.parametrize('token, expected_count', [
        (pytest.lazy_fixture('access_token_admin'), 6),
        (pytest.lazy_fixture('access_token_adult_user'), 6),
        (None, 5)
    ])
    def test_list_categories(self, token, expected_count):
        if token:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == expected_count


class TestAuthorViewSet:
    url_list = reverse('items:author-list')

    @pytest.fixture(autouse=True)
    def initial(self, author_factory, api_client):
        self.authors = author_factory(5)
        self.client = api_client()

    @pytest.mark.parametrize('token, expected_status', [
        (pytest.lazy_fixture('access_token_admin'), status.HTTP_201_CREATED),
        (pytest.lazy_fixture('access_token_adult_user'), status.HTTP_403_FORBIDDEN),
        ('invalid', status.HTTP_401_UNAUTHORIZED)
    ])
    def test_create_author(self, token, expected_status):
        data = {
            'name': 'New author',
            'description': 'New description'
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(self.url_list, data)

        assert response.status_code == expected_status

    def test_create_author_without_auth(self):
        data = {
            'name': 'New author',
            'description': 'New description'
        }
        response = self.client.post(self.url_list, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_authors(self):
        response = self.client.get(self.url_list)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_retrieve_author(self):
        url = reverse('items:author-detail', kwargs={'pk': self.authors[0].id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'Author' in response.data['name']

    @pytest.mark.parametrize('token, expected_status', [
        (pytest.lazy_fixture('access_token_admin'), status.HTTP_204_NO_CONTENT),
        (pytest.lazy_fixture('access_token_adult_user'), status.HTTP_403_FORBIDDEN),
        ('invalid', status.HTTP_401_UNAUTHORIZED)
    ])
    def test_delete_author(self, token, expected_status):
        url = reverse('items:author-detail', kwargs={'pk': self.authors[0].id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.delete(url)

        assert response.status_code == expected_status

    @pytest.mark.parametrize('token, expected_status', [
        (pytest.lazy_fixture('access_token_admin'), status.HTTP_200_OK),
        (pytest.lazy_fixture('access_token_adult_user'), status.HTTP_403_FORBIDDEN),
        ('invalid', status.HTTP_401_UNAUTHORIZED)
    ])
    def test_update_author(self, token, expected_status):
        url = reverse('items:author-detail', kwargs={'pk': self.authors[0].id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        data = {
            'id': self.authors[0].id,
            'name': 'New name',
            'description': 'New test description',
            'photo': None
        }

        response = self.client.put(url, data)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.json() == data

    @pytest.mark.parametrize('token, data, expected_status', [
        (pytest.lazy_fixture('access_token_admin'), {'name': 'New name'}, status.HTTP_200_OK),
        (pytest.lazy_fixture('access_token_adult_user'), {'name': 'New name'}, status.HTTP_403_FORBIDDEN),
        ('invalid', {'name': 'New name'}, status.HTTP_401_UNAUTHORIZED)
    ])
    def test_partial_update_author(self, token, data, expected_status):
        url = reverse('items:author-detail', kwargs={'pk': self.authors[0].id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.patch(url, data)

        assert response.status_code == expected_status
        if response.status_code == status.HTTP_200_OK:
            assert response.data['name'] == 'New name'
