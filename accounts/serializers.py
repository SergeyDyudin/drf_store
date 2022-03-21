from django.contrib.auth import password_validation
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from accounts.models import CustomUser, Profile, Region
from accounts.services import send_activation_email

from utils.validators import validate_phone


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = [
            'id',
            'region',
            'country',
        ]


class GetProfileSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = Profile
        fields = [
            'id',
            'phone',
            'birthday',
            'region',
            'currency',
            'email_confirmed',
            'age',
            'user',
        ]


class PostProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(validators=[validate_phone])
    region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())

    class Meta:
        model = Profile
        fields = [
            'phone',
            'birthday',
            'region',
        ]


class GetCustomUserSerializer(serializers.ModelSerializer):
    profile = GetProfileSerializer()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_active',
            'date_joined',
            'last_login',
            'profile',
            'password',
        ]


class PostCustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    profile = PostProfileSerializer()

    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
            'password2',
            'profile',
        ]

    def validate(self, attrs):
        # Если задано только одно поле для пароля
        if bool(attrs.get('password')) ^ bool(attrs.get('password2')):
            raise serializers.ValidationError({"password": "Password and password2 fields are required."})

        if attrs.get('password') and attrs.get('password2'):  # оба поля заданы
            if attrs['password'] != attrs['password2']:
                raise serializers.ValidationError({"password": "Password fields didn't match."})
            del attrs['password2']

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)

        user = CustomUser.objects.create(**validated_data)
        user.is_active = False
        user.set_password(password)
        user.save()

        if profile_data:
            Profile.objects.update_or_create(user=user, defaults=profile_data)
            user.refresh_from_db()

        send_activation_email(request=self.context['request'], user=user)
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()

        if profile_data:
            profile = Profile.objects.get(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        instance.refresh_from_db()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _('Your old password was entered incorrectly. Please enter it again.')
            )
        return value

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password2': _("The two password fields didn't match.")})
        password_validation.validate_password(attrs['new_password1'], self.context['request'].user)
        return attrs

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = kwargs.get('user')
        if user:
            user.set_password(password)
            user.save()
        return user
