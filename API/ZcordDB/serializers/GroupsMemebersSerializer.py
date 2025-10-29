from rest_framework import serializers

from .GroupsSerializer import GroupsSerializer
from ..models import GroupsMembers


class GroupsMembersSerializer(serializers.ModelSerializer):
    group = GroupsSerializer(read_only=True)

    class Meta:
        model = GroupsMembers
        fields = ['id', 'user', 'group']
