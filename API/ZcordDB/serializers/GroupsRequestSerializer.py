from rest_framework import serializers

from ZcordDB.models import GroupRequest
from ZcordDB.serializers.GroupsSerializer import GroupsSerializer


class GroupsRequestSerializer(serializers.ModelSerializer):
    group = GroupsSerializer(read_only=True)

    class Meta:
        model = GroupRequest
        fields = '__all__'
