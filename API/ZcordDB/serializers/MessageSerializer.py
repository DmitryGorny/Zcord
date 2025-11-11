from rest_framework import serializers
from ..models import Message, MessageType


class BaseMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'created_at', 'was_seen', 'type']


class VoiceMessageSerializer(BaseMessageSerializer):
    class Meta(BaseMessageSerializer.Meta):
        fields = BaseMessageSerializer.Meta.fields + ['voice_file']


class ImageMessageSerializer(BaseMessageSerializer):
    class Meta(BaseMessageSerializer.Meta):
        fields = BaseMessageSerializer.Meta.fields + ['image_url']


class ServiceMessageSerializer(BaseMessageSerializer):
    class Meta(BaseMessageSerializer.Meta):
        fields = BaseMessageSerializer.Meta.fields + ['service_message']


class TextMessageSerializer(BaseMessageSerializer):
    class Meta(BaseMessageSerializer.Meta):
        fields = BaseMessageSerializer.Meta.fields + ['message']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

    def to_representation(self, instance):
        if instance.type == MessageType.VOICE:
            return VoiceMessageSerializer(instance).data
        if instance.type == MessageType.IMAGE:
            return ImageMessageSerializer(instance).data
        if instance.type == MessageType.TEXT:
            return TextMessageSerializer(instance).data
        if instance.type == MessageType.SERVICE:
            return ServiceMessageSerializer(instance).data
        return super(MessageSerializer, self).to_representation(instance)


class MessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id']


class MessageBulkSerializer(serializers.Serializer):
    messages = MessageSerializer(many=True)


class MessageBulkUpdateSerializer(serializers.Serializer):
    ids = MessageUpdateSerializer(many=True)
