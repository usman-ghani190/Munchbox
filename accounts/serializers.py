"""Serializers for user Registration and Login"""
from rest_framework import serializers
from core.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    keep_signed_in = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'password2', 'keep_signed_in']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Passwords must match."})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data.pop('keep_signed_in', None)
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],  # Use email as username
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        Token.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    keep_signed_in = serializers.BooleanField(default=False, required=False)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        # Use email as username for authentication
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({"non_field_errors": "Invalid email or password."})
        data['user'] = user
        return data