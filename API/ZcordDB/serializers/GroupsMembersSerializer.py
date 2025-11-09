from rest_framework import serializers
from ..models import GroupsMembers


class GroupsMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupsMembers
        fields = '__all__'
