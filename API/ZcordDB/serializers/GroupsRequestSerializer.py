from rest_framework import serializers

from ZcordDB.models import GroupRequest, Groups, Users
from ZcordDB.serializers.GroupsSerializer import GroupsSerializer


class GroupsRequestSerializer(serializers.ModelSerializer):
    group = GroupsSerializer(read_only=True)
    group_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = GroupRequest
        fields = '__all__'

    def create(self, validated_data):
        group_id = self.initial_data.get('group_id')
        sender_id = self.initial_data.get('sender')
        receiver_id = self.initial_data.get('receiver')

        group = Groups.objects.filter(id=group_id).first() if group_id else None
        receiver = Users.objects.get(id=receiver_id)
        sender = Users.objects.get(id=sender_id)

        return GroupRequest.objects.create(
            sender=sender,
            receiver=receiver,
            group=group
        )
