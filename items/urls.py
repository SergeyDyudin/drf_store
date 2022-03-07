from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = 'items'

urlpatterns = [
    path('', views.ItemsListView.as_view(), name='home'),
    path('category/<str:cat>', views.CategoryListView.as_view(), name='category'),
    path('type/<str:type>', views.TypeListView.as_view(), name='type'),
    path('<slug:slug>/', views.ItemDetailView.as_view(), name='item')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
