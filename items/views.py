import rest_framework.exceptions
from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from items.filters import ItemFilter
from items.models import (Author, Brand, Category, Genre, Item, Language,
                          Publisher)
from items.serializers import (AuthorSerializer, BrandSerializer,
                               CategorySerializer, GenreSerializer,
                               GetBookSerializer, GetFigureSerializer,
                               GetMagazineSerializer, ItemSerializer,
                               LanguageSerializer, PostBookSerializer,
                               PostFigureSerializer, PostMagazineSerializer,
                               PublisherSerializer)


class LanguageViewSet(viewsets.ModelViewSet):
    """Отображение доступных языков"""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


class CategoryViewSet(viewsets.ModelViewSet):
    """Отображение доступных категорий"""
    # queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        return Category.objects.adult_control(self.request.user)


class AuthorViewSet(viewsets.ModelViewSet):
    """Отображение доступных авторов"""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


class GenreViewSet(viewsets.ModelViewSet):
    """Отображение доступных жанров"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


class PublisherViewSet(viewsets.ModelViewSet):
    """Отображение доступных издателей"""
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


class BrandViewSet(viewsets.ModelViewSet):
    """Отображение доступных брендов"""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Доступные товары с учетом возрастных ограничений"""
    serializer_class = ItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ItemFilter
    search_fields = ['title']
    ordered_fields = ['price']

    def get_queryset(self):
        queryset = Item.objects.adult_control(self.request.user).prefetch_related('categories')
        return queryset

    def get_object(self, queryset=None):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        queryset = queryset.select_related(*self.serializer_class.Meta.model.get_children_list())
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class ItemChildMixin:
    """Получение queryset и serializer в соответствии с классом"""
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ItemFilter
    search_fields = ['title']
    ordered_fields = ['price']

    def get_queryset(self):
        self.model = self.get_model()
        queryset = self.model.objects.adult_control(self.request.user).prefetch_related('categories')
        if self.request.query_params.get('cat'):
            queryset = self.filter_category(queryset, self.request.query_params.get('cat'))
        return queryset

    def get_serializer_class(self):
        return self.MAP_ACTION_TO_SERIALIZER.get(self.action, self.serializer_class)

    def get_model(self):
        return ContentType.objects.get(app_label='items', model=self.basename).model_class()

    @staticmethod
    def filter_category(queryset, category_id):
        """Фильтрация queryset по указанной категории товаров"""
        if category_id.isdigit() and Category.objects.filter(pk=category_id).exists():
            return queryset.filter(categories__pk=category_id)
        raise rest_framework.exceptions.NotFound()


class BookViewSet(ItemChildMixin, viewsets.ModelViewSet):
    """Доступные книги с учетом возрастных ограничений"""
    serializer_class = PostBookSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]

    MAP_ACTION_TO_SERIALIZER = {
        'list': GetBookSerializer,
        'create': PostBookSerializer,
        'retrieve': GetBookSerializer,
    }


class FigureViewSet(ItemChildMixin, viewsets.ModelViewSet):
    """Доступные фигурки с учетом возрастных ограничений"""
    serializer_class = PostFigureSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]

    MAP_ACTION_TO_SERIALIZER = {
        'list': GetFigureSerializer,
        'create': PostFigureSerializer,
        'retrieve': GetFigureSerializer,
    }


class MagazineViewSet(ItemChildMixin, viewsets.ModelViewSet):
    """Доступные фигурки с учетом возрастных ограничений"""
    serializer_class = PostMagazineSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]

    MAP_ACTION_TO_SERIALIZER = {
        'list': GetMagazineSerializer,
        'create': PostMagazineSerializer,
        'retrieve': GetMagazineSerializer,
    }
