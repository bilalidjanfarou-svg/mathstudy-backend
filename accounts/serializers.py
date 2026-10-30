from django.contrib.auth import password_validation
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    plan_label = serializers.CharField(source='get_plan_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'nom_complet', 'role',
            'plan', 'plan_label', 'universite', 'filiere', 'niveau',
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['nom_complet', 'email', 'password', 'universite', 'filiere', 'niveau']
        extra_kwargs = {
            'email': {'validators': []},
            'nom_complet': {'required': True},
            'universite': {'required': True},
            'filiere': {'required': True},
            'niveau': {'required': True},
        }

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Un compte existe déjà avec cet e-mail.')
        return value

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(username=validated_data['email'], **validated_data)
        user.set_password(password)  # le mot de passe est enregistré chiffré, jamais en clair
        user.save()
        return user