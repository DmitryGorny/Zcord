from rest_framework import serializers
from ..models import FriendsAdding


class FriendsAddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendsAdding
        fields = '__all__'
