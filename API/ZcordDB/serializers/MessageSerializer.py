from rest_framework import serializers
from ..models import Message
from .UserSerializer import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    was_seen_display = serializers.CharField(source='get_was_seen_display', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat_id', 'sender', 'message', 'created_at', 'updated_at', 'was_seen', 'was_seen_display']
