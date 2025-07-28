from rest_framework import serializers
from ..models import FriendsAdding
from .UserSerializer import UserSerializer


class FriendsAddingSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    friend = UserSerializer(read_only=True)

    class Meta:
        model = FriendsAdding
        fields = ['id', 'sender', 'friend', 'date']
