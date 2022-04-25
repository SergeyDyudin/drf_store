from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from .views import (AuthorViewSet, BookViewSet, BrandViewSet, CategoryViewSet,
                    FigureViewSet, GenreViewSet, ItemViewSet, LanguageViewSet,
                    MagazineViewSet, PublisherViewSet)

app_name = 'items'

router = routers.DefaultRouter()
router.register(r'languages', LanguageViewSet)
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'authors', AuthorViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'publishers', PublisherViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'items', ItemViewSet, basename='item')
router.register(r'books', BookViewSet, basename='book')
router.register(r'magazines', MagazineViewSet, basename='magazine')
router.register(r'figures', FigureViewSet, basename='figure')

urlpatterns = [
    path('', include(router.urls)),
    # path('', views.ItemsListView.as_view(), name='home'),
    # path('category/<str:cat>', views.CategoryListView.as_view(), name='category'),
    # path('type/<str:type>', views.TypeListView.as_view(), name='type'),
    # path('<slug:slug>/', views.ItemDetailView.as_view(), name='item')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
