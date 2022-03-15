from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from accounts.models import CustomUser, Profile, Region

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
            'user',
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

    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
            'password2',
            # 'profile',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.save()
        return instance

