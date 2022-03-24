import logging

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.response import Response

from services.models import Invoice, Purchase, Rent
from services.serializers import InvoiceSerializer

logger = logging.getLogger(__name__)

MAPPING_SERVICES_TO_MODELS = {
        'purchase': Purchase,
        'rent': Rent,
    }


class CartViewSet(viewsets.GenericViewSet, ListModelMixin):
    """Корзина покупателя"""
    serializer_class = InvoiceSerializer
    permission_classes = [DjangoObjectPermissions]
    queryset = Invoice.objects.all()

    def get_object(self):
        invoice = get_object_or_404(
            self.get_queryset(),
            user_id=self.request.user.id,
            status=Invoice.InvoiceStatuses.UNPAID.value
        )
        self.check_object_permissions(self.request, invoice)
        return invoice

    # @action(methods=['GET'], detail=False, url_path='get')
    def list(self, request, *args, **kwargs):
        """Вывести корзину пользователя"""
        invoice = self.get_object()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    # @action(methods=['PUT', 'PATCH'], detail=False)
    def pay_the_cart(self, request, *args):
        """Оплата корзины"""
        instance = self.get_object()
        data = {
            'status': Invoice.InvoiceStatuses.PAID.value,
            'status_updated': timezone.now()
        }

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(methods=['DELETE'], detail=False, url_path=r'delete_service/(?P<pk>\d+)')
    def delete_service(self, request, pk=None):
        """Удалить сервис по id из корзины"""
        service_type = request.query_params.get('service')
        model = MAPPING_SERVICES_TO_MODELS.get(service_type)
        if model is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            model.objects.get(id=pk).delete()
        except Purchase.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class HistoryViewSet(viewsets.GenericViewSet, ListModelMixin):
    """История покупок пользователя"""
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.\
            filter(user_id=self.request.user.id).\
            exclude(status=Invoice.InvoiceStatuses.CANCELED.value).\
            order_by('-status_updated')
