from django.contrib.auth.hashers import make_password, check_password
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
            members_list = members if members.count() > 1 else list(members)
            serializer = GroupsMembersDetailSerializer(members_list, many=True)
            return serializer.data

        return []

    def validate_new_password(self, value):
        group = self.context["group"]

        if check_password(value, group.password):
            raise serializers.ValidationError(
                "Новый пароль должен отличаться от старого"
            )

        return value

    def create(self, validated_data):
        password = validated_data.get('password', None)
        group = Groups(**validated_data)
        group.password = make_password(password)
        group.save()
        return group

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        instance.password = make_password(password)
        instance.save()
        super().update(instance, validated_data)
        return instance
