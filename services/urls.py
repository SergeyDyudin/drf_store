from django.urls import path

from . import views

app_name = 'services'

urlpatterns = [
    path('history/', views.HistoryViewSet.as_view(actions={
        'get': 'list'
    }), name='history'),
    path('cart/', views.CartViewSet.as_view(actions={
        'get': 'get_cart',
        'patch': 'partial_update',
        'put': 'update',
    }), name='cart'),
    path('cart/<int:pk>/', views.CartViewSet.as_view(actions={
        'delete': 'delete_service'
    }), name='cart-delete-service'),
    path('purchase/', views.PurchaseViewSet.as_view(actions={
        'post': 'create',
    }), name='purchase'),
    path('rent/', views.RentViewSet.as_view(actions={
        'post': 'create',
    }), name='rent'),
    path('rent/<int:pk>/', views.RentViewSet.as_view(actions={
        'get': 'retrieve',
    }), name='rent-get')
]
