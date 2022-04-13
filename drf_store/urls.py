"""drf_store URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from drf_store import settings

router = DefaultRouter()

schema_view = get_schema_view(
    title="Book store",
    description="API for book store",
    version="1.0.0"
)

urlpatterns = [
    path('account/', include('accounts.urls', namespace='accounts')),
    path('service/', include('services.urls', namespace='services')),
    path('api-auth/', include('rest_framework.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('items/', include('items.urls', namespace='items')),
    path('openapi', schema_view, name='openapi-schema'),
    path('swagger-ui/', TemplateView.as_view(
            template_name='swagger/swagger-ui.html',
            extra_context={'schema_url': 'openapi-schema'}
        ), name='swagger-ui'),  # TODO:
    path('', include(router.urls))
]

# Add prefix api for url
urlpatterns = [path(settings.API_PREFIX_URL, include(urlpatterns))]

urlpatterns += [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
]
