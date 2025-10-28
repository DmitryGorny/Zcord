from rest_framework import serializers

from .FriendshipSerializer import FriendshipSerializer
from .GroupsSerializer import GroupsSerializer
from ..models import Chats, Groups, Friendship


class ChatsSerializer(serializers.ModelSerializer):
    group = GroupsSerializer(read_only=True)
    DM = FriendshipSerializer(read_only=True)

    def create(self, validated_data):
        DM_id = self.initial_data.get('DM_id')
        group_id = self.initial_data.get('group_id')
        is_group = self.initial_data.get('is_group', False)

        dm = Friendship.objects.filter(id=DM_id).first() if DM_id else None
        group = Groups.objects.filter(id=group_id).first() if group_id else None

        return Chats.objects.create(
            is_group=is_group,
            DM=dm,
            group=group
        )

    class Meta:
        model = Chats
        fields = ['id', 'is_group', 'group', 'DM', 'group_id', 'DM_id']
