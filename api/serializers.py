""" Serializers for Api app """

from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Entry

class EntrySerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Entry
        fields = ('id', 'user_id', 'text', 'notes', 'date_created', 'date_modified')
        read_only_fields = ('date_created', 'date_modified')


class CreateUserSerializer(serializers.ModelSerializer):
    """ Serializer to create a User """
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        None,
                                        validated_data['password'])
        return user


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for User Model """
    class Meta:
        model = User
        fields = ('id', 'username')
