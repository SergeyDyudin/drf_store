from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'services'

router = routers.DefaultRouter()
router.register(r'history', views.HistoryViewSet, basename='history')
router.register(r'cart', views.CartViewSet, basename='cart')

router.routes[0].mapping['patch'] = 'pay_the_cart'
router.routes[0].mapping['put'] = 'pay_the_cart'

urlpatterns = [
    path('', include(router.urls)),
    # path('cart/', views.CartView.as_view(), name='cart'),
    # path('purchase/<int:pk>', views.PurchaseView.as_view(), name='purchase'),
    # path('rent/<int:pk>', views.RentView.as_view(), name='rent'),
    # path('cart/delete/<str:service>/<int:pk>', views.delete_service, name='delete_service'),
    # path('history/', views.HistoryListView.as_view(), name='history_services'),
]
