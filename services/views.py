import logging
from itertools import chain

from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, ListModelMixin
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.response import Response

from services.models import Invoice, Purchase, Rent
from services.serializers import InvoiceSerializer

logger = logging.getLogger(__name__)


class CartViewSet(viewsets.GenericViewSet, RetrieveModelMixin, CreateModelMixin):
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

    @action(methods=['GET'], detail=False, url_path='get')
    def cart(self, request, *args, **kwargs):
        invoice = self.get_object()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)


class HistoryViewSet(viewsets.GenericViewSet, ListModelMixin):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.\
            filter(user_id=self.request.user.id).\
            exclude(status=Invoice.InvoiceStatuses.CANCELED.value).\
            order_by('-status_updated')
