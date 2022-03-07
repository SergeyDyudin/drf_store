import logging

from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View

from django.views.generic import FormView, DetailView, UpdateView
from django.utils.translation import gettext_lazy as _

from accounts.forms import SendEmailForm, LoginForm, ProfileChangeForm, RegistrationForm, AccountForm
from accounts.models import CustomUser, Profile, Region
from accounts.tokens import account_activation_token


logger = logging.getLogger(__name__)


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


class AccountView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = 'accounts/account.html'
    form_class = AccountForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AccountForm(instance=self.object,
                           initial={
                               'region': self.object.profile.region,
                               'birthday': self.object.profile.birthday,
                               'phone': self.object.profile.phone,
                               'currency': self.object.profile.currency,
                           })

        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(form_class=self.form_class)
        if form.is_valid():
            region = Region.objects.get(
                region=form.cleaned_data.get('region').region,
                country=form.cleaned_data.get('region').country
            )
            self.object.profile.region = region
            self.object.profile.birthday = form.cleaned_data.get('birthday')
            self.object.profile.phone = form.cleaned_data.get('phone')
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': _('Account page'),
        })
        return context

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )

        try:
            # Get the single item from the filtered queryset
            obj = queryset.select_related('profile').get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


class LoginView(View):
    def get(self, request):
        context = {
            'title': _('Войти'),
        }
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:account', args=[request.user.id]))
        context['form'] = LoginForm(initial={'email': '', 'password': ''})
        return render(request, 'accounts/login.html', context)

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None and user.is_active:
                login(request, user)
                logger.info(f'User {user} is login')
                # return HttpResponseRedirect(reverse('home'))
                redirect_to = request.GET.get('next', reverse('accounts:account', kwargs={'pk': user.id}))
                return HttpResponseRedirect(redirect_to)
        messages.error(request, 'Email or password is incorrect')
        return render(request, 'accounts/login.html')


class LogoutView(View):
    def get(self, request):
        logout(request)
        logger.info(f'User {request.user} is logout')
        return HttpResponseRedirect(reverse('items:home'))


class RegistrationView(View):
    def get(self, request):
        context = {}
        form = RegistrationForm()
        context.update({
            'form': form,
            'title': 'Registration',
        })
        return render(request, 'accounts/registration.html', context)

    @transaction.atomic
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            region = Region.objects.get(
                region=form.cleaned_data.get('region').split(',')[0].strip(),
                country=form.cleaned_data.get('region').split(',')[1].strip()
            )
            user.profile.region = region
            user.profile.birthday = form.cleaned_data.get('birthday')
            user.profile.phone = form.cleaned_data.get('phone')
            user.save()
            self.send_avtivation_email(request, user)
            return redirect('accounts:account_activation_sent')
        else:
            return render(request, 'accounts/account_activation_invalid.html')

    def send_avtivation_email(self, request, user):
        current_site = get_current_site(request)
        subject = 'Activate Your MySite Account'
        message = render_to_string('accounts/account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        user.email_user(subject, message)
        logger.info(f'Sent activation email to {user.email}')


def account_activation_sent(request):
    return render(request, 'accounts/account_activation_sent.html')


def activate_user(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
        logger.error(f'Invalid uid user for activation')

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        logger.info(f'Activate user {user}')
        login(request, user)
        return redirect('items:home')
    else:
        return render(request, 'accounts/account_activation_invalid.html')
