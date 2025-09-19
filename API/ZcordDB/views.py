from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework import generics, status
from rest_framework.response import Response

from .Paginations import LimitPagination
from .models import Users, Friendship, Message, FriendsAdding
from .serializers.UserSerializer import UserSerializer
from .serializers.FriendshipSerializer import FriendshipSerializer
from .serializers.MessageSerializer import MessageSerializer, MessageBulkSerializer, MessageBulkUpdateSerializer
from .serializers.FriendsAddingSerializer import FriendsAddingSerializer
from django.db.models import Q


class UserView(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nickname']


class FriendshipView(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user1_id__nickname', 'user2_id__nickname']  # Поиск по никнеймам

    def get_queryset(self):
        queryset = super().get_queryset()
        user1_nick = self.request.query_params.get('user1')
        user2_nick = self.request.query_params.get('user2')

        if user1_nick and user2_nick:
            return queryset.filter(
                Q(user1_id__nickname=user1_nick, user2_id__nickname=user2_nick) |
                Q(user1_id__nickname=user2_nick, user2_id__nickname=user1_nick)
            )
        return queryset


class FriendsAddingView(viewsets.ModelViewSet):
    queryset = FriendsAdding.objects.all()
    serializer_class = FriendsAddingSerializer


class MessageView(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["chat__id"]
    pagination_class = LimitPagination

    def get_serializer_class(self):
        if self.action == 'bulk_create':
            return MessageBulkSerializer
        if self.action == 'bulk_update':
            return MessageBulkUpdateSerializer
        return MessageSerializer

    @action(detail=False, methods=['post'], url_path='messages-bulk/')
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data)
        print(serializer)
        serializer.is_valid(raise_exception=True)
        messages_data = serializer.validated_data.get('messages', [])
        messages_to_create = [
            Message(
                chat=msg['chat'],
                sender=msg['sender'],
                message=msg['message'],
                was_seen=msg.get('was_seen', False)
            ) for msg in messages_data
        ]
        Message.objects.bulk_create(messages_to_create)

        return Response({
            "status": "success",
            "count": len(messages_to_create)
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='messages-bulk-update/')
    def bulk_update(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        messages = []
        for mes_id in request.data["ids"]:
            message = Message.objects.get(id=mes_id["id"])
            message.was_seen = True
            messages.append(message)

        count = Message.objects.bulk_update(messages, ["was_seen"], 15)

        return Response({
            "status": "success",
            "count": count
        }, status=status.HTTP_201_CREATED)

