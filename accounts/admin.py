from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import render
from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views
from .forms import ProfileChangeForm, ProfileCreationForm
from .models import CustomUser, Profile, Region


class RegionAdmin(admin.ModelAdmin):
    model = Region
    verbose_name = _('region')
    verbose_name_plural = _('regions')
    ordering = ['region']

    def get_urls(self):
        urls = super().get_urls()
        upload_url = [
            path(
                'upload/',
                self.admin_site.admin_view(self.upload_regions),
                name='upload_from_csv'
            ),
        ]
        return upload_url + urls

    def upload_regions(self, request):
        """
        Upload regions to database from csv-file
        :param request:
        :return:
        """
        messages = Region.import_from_csv('accounts/region.csv')
        context = super().changelist_view(request).context_data
        context['messages'] = messages
        return render(request, 'admin/change_list.html', context)


# admin.site.register(CustomUser)
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name = _('profile')
    verbose_name_plural = _('profiles')
    readonly_fields = [
        'email_confirmed',
    ]

    def get_formset(self, request, obj=None, **kwargs):
        if not request.user.is_staff:
            self.readonly_fields = [
                'currency'
            ]
        if obj is None:
            self.form = ProfileCreationForm
        else:
            self.form = ProfileChangeForm
        return super().get_formset(request, obj, **kwargs)


# Define a new User admin
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('password',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'get_email_confirmed')
    search_fields = ('first_name', 'last_name', 'email')
    inlines = (ProfileInline,)

    def get_urls(self):
        urls = super().get_urls()
        upload_url = [
            path(
                '<user_id>/send-email/',
                self.admin_site.admin_view(views.SendEmailView.as_view(model_admin=self)),
                name='send_email'
            ),
        ]
        return upload_url + urls

    @display(description=_('Email confirmed'))
    def get_email_confirmed(self, obj):
        return obj.profile.email_confirmed

    get_email_confirmed.boolean = True


class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'full_name',
        'region',
    ]
    readonly_fields = [
        'email_confirmed',
    ]

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not request.user.is_staff:
            self.readonly_fields = [
                'currency'
            ]
        if obj is None:
            self.form = ProfileCreationForm
        else:
            self.form = ProfileChangeForm
        return super().get_form(request, obj, change, **kwargs)


# Re-register UserAdmin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Region, RegionAdmin)
