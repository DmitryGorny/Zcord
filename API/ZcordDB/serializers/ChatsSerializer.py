from rest_framework import serializers

from .FriendshipSerializer import FriendshipSerializer
from .GroupsSerializer import GroupsSerializer
from ..models import Chats


class ChatsSerializer(serializers.ModelSerializer):
    group = GroupsSerializer(read_only=True)
    DM = FriendshipSerializer(read_only=True)

    class Meta:
        model = Chats
        fields = ['id', 'is_group', 'group', 'DM']
