from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from items.models import Language, Item, Book, Magazine, Figure, Category, Author, Genre, Publisher, Brand
from items.serializers import LanguageSerializer, ItemSerializer, GetBookSerializer, PostBookSerializer, \
    PostFigureSerializer, GetFigureSerializer, GetMagazineSerializer, PostMagazineSerializer, CategorySerializer, \
    AuthorSerializer, GenreSerializer, PublisherSerializer, BrandSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    """Отображение доступных языков"""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


class CategoryViewSet(viewsets.ModelViewSet):
    """Отображение доступных категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


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

# TODO: Сделать что-то с дублирующимися классами Book, Magazine, Figure (Item)
class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Доступные товары с учетом возрастных ограничений"""
    serializer_class = ItemSerializer

    def get_queryset(self):
        queryset = Item.objects.adult_control(self.request.user).prefetch_related('categories')
        if self.request.query_params.get('search_item', False):
            queryset = queryset.filter(title__icontains=self.request.query_params['search_item'])
        elif self.request.query_params.get('cat') and \
                (not self.request.query_params.get('cat') == 'Все'):
            return queryset.filter(categories__name=self.request.query_params.get('cat'))
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


class BookViewSet(viewsets.ModelViewSet):
    """Доступные книги с учетом возрастных ограничений"""
    serializer_class = PostBookSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]

    MAP_ACTION_TO_SERIALIZER = {
        'list': GetBookSerializer,
        'create': PostBookSerializer,
        'retrieve': GetBookSerializer,
    }

    def get_queryset(self):
        queryset = Book.objects.adult_control(self.request.user).prefetch_related('categories')
        if self.request.query_params.get('cat') and (not self.request.query_params.get('cat') == 'Все'):
            return queryset.filter(categories__name=self.request.query_params.get('cat'))
        return queryset

    def get_serializer_class(self):
        return self.MAP_ACTION_TO_SERIALIZER.get(self.action, self.serializer_class)


class FigureViewSet(viewsets.ModelViewSet):
    """Доступные фигурки с учетом возрастных ограничений"""
    serializer_class = PostFigureSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]

    MAP_ACTION_TO_SERIALIZER = {
        'list': GetFigureSerializer,
        'create': PostFigureSerializer,
        'retrieve': GetFigureSerializer,
    }

    def get_queryset(self):
        queryset = Figure.objects.adult_control(self.request.user).prefetch_related('categories')
        if self.request.query_params.get('cat') and (not self.request.query_params.get('cat') == 'Все'):
            return queryset.filter(categories__name=self.request.query_params.get('cat'))
        return queryset

    def get_serializer_class(self):
        return self.MAP_ACTION_TO_SERIALIZER.get(self.action, self.serializer_class)


class MagazineViewSet(viewsets.ModelViewSet):
    """Доступные фигурки с учетом возрастных ограничений"""
    serializer_class = PostMagazineSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]

    MAP_ACTION_TO_SERIALIZER = {
        'list': GetMagazineSerializer,
        'create': PostMagazineSerializer,
        'retrieve': GetMagazineSerializer,
    }

    def get_queryset(self):
        queryset = Magazine.objects.adult_control(self.request.user).prefetch_related('categories')
        if self.request.query_params.get('cat') and (not self.request.query_params.get('cat') == 'Все'):
            return queryset.filter(categories__name=self.request.query_params.get('cat'))
        return queryset

    def get_serializer_class(self):
        return self.MAP_ACTION_TO_SERIALIZER.get(self.action, self.serializer_class)
