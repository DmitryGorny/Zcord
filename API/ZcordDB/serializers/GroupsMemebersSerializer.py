from rest_framework import serializers

from .UserSerializer import UserSerializer
from ..models import GroupsMembers


class GroupsMembersDetailSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source="user.nickname", read_only=True)
    user_id = serializers.CharField(source="user.id", read_only=True)

    class Meta:
        model = GroupsMembers
        fields = ['nickname', 'user_id']

