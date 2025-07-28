from rest_framework import serializers
from ..models import Friendship
from .UserSerializer import UserSerializer


class FriendshipSerializer(serializers.ModelSerializer):
    user1_id = UserSerializer(read_only=True)
    user2_id = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Friendship
        fields = ['id', 'user1_id', 'user2_id', 'status', 'status_display', 'created_at', 'updated_at']
