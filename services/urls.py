from django.urls import path

from . import views

app_name = 'services'

urlpatterns = [
    path('history/', views.HistoryViewSet.as_view(actions={
        'get': 'list'
    }), name='history'),
    path('cart/', views.CartViewSet.as_view(actions={
        'get': 'list',
        'patch': 'update',
        'put': 'update',
        'delete': 'delete_service',
    }), name='cart'),
    path('cart/<int:pk>/', views.CartViewSet.as_view(actions={
        'delete': 'delete_service'
    }), name='cart-delete-service'),
    path('purchase/', views.PurchaseViewSet.as_view(actions={
        'post': 'create',
    }), name='purchase')
    # path('cart/', views.CartView.as_view(), name='cart'),
    # path('purchase/<int:pk>', views.PurchaseView.as_view(), name='purchase'),
    # path('rent/<int:pk>', views.RentView.as_view(), name='rent'),
    # path('cart/delete/<str:service>/<int:pk>', views.delete_service, name='delete_service'),
    # path('history/', views.HistoryListView.as_view(), name='history_services'),
]
