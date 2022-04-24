import pytest
from random import randint
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser
from items.models import Book, Author, Genre, Language, Publisher, Category, Brand


@pytest.fixture
def api_client():
    return APIClient


@pytest.fixture
def adult_user(db):
    user = CustomUser.objects.create_user(
        email='foo@bar.com',
        password='Qw789456'
    )
    user.profile.birthday = '2000-02-02'
    user.save()
    return user


@pytest.fixture
def admin_user(db):
    user = CustomUser.objects.create_user(
        email='admin@bar.com',
        password='Qw789456'
    )
    user.is_superuser = True
    user.save()
    return user


@pytest.fixture
def access_token_adult_user(db, adult_user):
    return RefreshToken.for_user(adult_user).access_token


@pytest.fixture
def access_token_admin(db, admin_user):
    return RefreshToken.for_user(admin_user).access_token


@pytest.fixture
def language_factory(db):
    def create_languages(quantity: int = 1):
        languages = [
            Language(code=f'C{i}', name=f'Language {i}')
            for i in range(quantity)
        ]
        return Language.objects.bulk_create(languages)
    return create_languages


@pytest.fixture
def publisher_factory(db):
    def create_publishers(quantity: int = 1):
        publishers = [
            Publisher(name=f'Publisher {i}', address=f'Address {i}')
            for i in range(quantity)
        ]
        return Publisher.objects.bulk_create(publishers)
    return create_publishers


@pytest.fixture
def author_factory(db):
    def create_authors(quantity: int = 1):
        authors = [
            Author(name=f'Author {i}', description=f'Description {i}')
            for i in range(quantity)
        ]
        return Author.objects.bulk_create(authors)
    return create_authors


@pytest.fixture
def genre_factory(db):
    def create_genres(quantity: int = 1):
        genres = [
            Genre(name=f'Genre {i}')
            for i in range(quantity)
        ]
        return Genre.objects.bulk_create(genres)
    return create_genres


@pytest.fixture
def category_factory(db):
    def create_categories(quantity: int = 1):
        categories = [
            Category(name=f'Category {i}', description=f'Category description {i}')
            for i in range(quantity)
        ]
        return Category.objects.bulk_create(categories)
    return create_categories


@pytest.fixture
def adult_category(db):
    return Category.objects.create(name=settings.ADULT_CATEGORIES[0], description='Adult category')


@pytest.fixture
def brand_factory(db):
    def create_brands(quantity: int = 1):
        brands = [
            Brand(name=f'Brand {i}', description=f'Brand description {i}')
            for i in range(quantity)
        ]
        return Brand.objects.bulk_create(brands)
    return create_brands


@pytest.fixture
def book_factory(db, language_factory, publisher_factory):
    def create_books(quantity: int = 1):
        languages = language_factory(3)
        publishers = publisher_factory(5)
        books = []
        for i in range(quantity):
            books.append(Book.objects.create(
                    title=f'Title {i}',
                    price=randint(100, 5000),
                    year=f'{randint(1000, 2022)}-{randint(1, 12)}-{randint(1, 28)}',
                    language=languages[randint(0, 2)],
                    publisher=publishers[randint(0, 4)],
                    slug=f'title-{i}'
            ))
        return books
    return create_books


