from rest_framework import serializers
from ..models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class MessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id']

class MessageBulkSerializer(serializers.Serializer):
    messages = MessageSerializer(many=True)


class MessageBulkUpdateSerializer(serializers.Serializer):
    ids = MessageUpdateSerializer(many=True)
