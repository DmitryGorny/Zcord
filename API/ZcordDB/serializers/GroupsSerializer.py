from rest_framework import serializers
from rest_framework.response import Response

from .GroupsMemebersSerializer import GroupsMembersDetailSerializer
from ..models import Groups, GroupsMembers


class GroupsSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Groups
        exclude = ["members"]

    def get_users(self, group):
        members = GroupsMembers.objects.filter(group=group)

        if members.exists():
            members_list = members if members.count() > 1 else list(members)  # Ensure it's a list
            serializer = GroupsMembersDetailSerializer(members_list, many=True)
            return serializer.data

        return []
