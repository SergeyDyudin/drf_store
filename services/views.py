import logging

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.permissions import DjangoObjectPermissions, IsAuthenticated
from rest_framework.response import Response

from services.models import Invoice, Purchase, Rent
from services.serializers import InvoiceSerializer, AlterPurchaseSerializer, CreateRentSerializer
from services.services import pay_the_cart, create_purchase, create_rent, get_data_for_rent

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

    def list(self, request, *args, **kwargs):
        """Вывести корзину пользователя"""
        invoice = self.get_object()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @transaction.atomic
    def update(self, request, *args):
        """Оплата корзины"""
        instance = self.get_object()

        try:
            pay_the_cart(request, instance)
        except Exception:
            logger.error('Оплата не прошла', exc_info=True)
            return Response({'error': 'Payment failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        instance.refresh_from_db()
        serializer = self.get_serializer(instance)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.\
            filter(user_id=self.request.user.id).\
            exclude(status=Invoice.InvoiceStatuses.CANCELED.value).\
            order_by('-status_updated')


class PurchaseViewSet(viewsets.GenericViewSet, CreateModelMixin):
    """Покупка товара"""
    serializer_class = AlterPurchaseSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            create_purchase(request, serializer.data)
            return Response({'create': 'OK'}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)


class RentViewSet(viewsets.GenericViewSet, CreateModelMixin):
    """Аренда товара"""
    serializer_class = CreateRentSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        data, daily_payment = get_data_for_rent(pk)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        result = serializer.data
        result.update(daily_payment)
        return Response(result)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            create_rent(request, serializer.data)
            return Response({'create': 'OK'}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
