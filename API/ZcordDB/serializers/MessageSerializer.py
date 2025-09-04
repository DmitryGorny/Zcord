from rest_framework import serializers
from ..models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class MessageBulkSerializer(serializers.Serializer):
    messages = MessageSerializer(many=True)
