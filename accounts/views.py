import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets

from accounts.forms import SendEmailForm
from accounts.models import CustomUser, Profile
from accounts.permissions import UserPermission
from accounts.serializers import GetCustomUserSerializer, PostCustomUserSerializer, \
    PostProfileSerializer, GetProfileSerializer

logger = logging.getLogger(__name__)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = PostCustomUserSerializer
    permission_classes = [UserPermission]

    MAP_ACTION_TO_SERIALIZER = {
        'list': GetCustomUserSerializer,
        'create': PostCustomUserSerializer,
        'retrieve': GetCustomUserSerializer,
    }

    def get_serializer_class(self):
        return self.MAP_ACTION_TO_SERIALIZER.get(self.action, self.serializer_class)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = PostProfileSerializer
    permission_classes = [UserPermission]

    MAP_ACTION_TO_SERIALIZER = {
        'list': GetProfileSerializer,
        'create': PostProfileSerializer,
        'retrieve': GetProfileSerializer,
    }

    def get_serializer_class(self):
        return self.MAP_ACTION_TO_SERIALIZER.get(self.action, self.serializer_class)


class SendEmailView(SuccessMessageMixin, PermissionRequiredMixin, FormView):
    model = CustomUser
    template_name = 'admin/accounts/customuser/change_form.html'
    model_admin = None
    form_class = SendEmailForm
    success_url = reverse_lazy('admin:accounts_customuser_changelist')
    permission_required = ('accounts.view_customuser',)

    success_message = _('Email sended to %(email)s.')

    def get_object(self, request, **kwargs):
        user_id = self.kwargs['user_id']
        return CustomUser.objects.get(id=user_id)

    def get(self, request, **kwargs):
        user_id = self.kwargs['user_id']
        obj = self.get_object(request, **kwargs)
        context = self.get_context_data()
        form = SendEmailForm(instance=obj, initial={'body': f'Dear {obj.first_name}, ', 'subject': '[DJANGO ADMIN]'})
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        obj = self.get_object(request, **kwargs)
        form = self.get_form()
        if form.is_valid():
            obj.email_user(subject=form.cleaned_data['subject'], message=form.cleaned_data['body'])
            logger.info(f'Email sent {request.user.email}')
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        return {
            **self.model_admin.admin_site.each_context(self.request),
            **super().get_context_data(**kwargs),
            'opts': CustomUser._meta,
            'has_view_permission': self.model_admin.has_view_permission(self.request),
            'title': _('Send email'),
            'add': '',
            'change': '',
            'save_as': '',
            'has_add_permission': False,
            'has_change_permission': False,
            'has_editable_inline_admin_formsets': False,
            'has_delete_permission': False,
        }