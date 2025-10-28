from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework import generics, status
from rest_framework.response import Response

from .Paginations import LimitPagination
from .models import Users, Friendship, Message, FriendsAdding, Chats
from .serializers.ChatsSerializer import ChatsSerializer
from .serializers.UserSerializer import UserSerializer
from .serializers.FriendshipSerializer import FriendshipSerializer
from .serializers.MessageSerializer import MessageSerializer, MessageBulkSerializer, MessageBulkUpdateSerializer
from .serializers.FriendsAddingSerializer import FriendsAddingSerializer
from django.db.models import Q, Count


class UserView(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=nickname']


class FriendshipView(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=user1_id__nickname', '=user2_id__nickname']  # Поиск по никнеймам

    def get_queryset(self):
        queryset = super().get_queryset()

        user1_nick = self.request.query_params.get('user1')
        user2_nick = self.request.query_params.get('user2')
        user1_id = self.request.query_params.get('user1_id')
        user2_id = self.request.query_params.get('user2_id')

        if user1_nick and user2_nick:
            queryset = queryset.filter(
                Q(user1_id__nickname=user1_nick, user2_id__nickname=user2_nick) |
                Q(user1_id__nickname=user2_nick, user2_id__nickname=user1_nick)
            )

        if user1_id and user2_id:
            queryset = queryset.filter(
                Q(user1_id=user1_id, user2_id=user2_id) |
                Q(user1_id=user2_id, user2_id=user1_id)
            )

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        user1 = data['user1']
        user2 = data['user2']

        existing_obj = Friendship.objects.filter(Q(user1__id=user1, user2__id=user2)
                                                 | Q(user2__id=user2, user1__id=user1)).exists()
        if existing_obj:
            serializer = self.get_serializer(existing_obj)
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={"user1": user1, "user2": user2, 'status': 1})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            return super().destroy(request, *args, **kwargs)

        user1_id = kwargs.get('user1_id')
        user2_id = kwargs.get('user2_id')

        if user1_id and user2_id:
            Friendship.objects.get(Q(user1_id=user1_id, user2_id=user2_id) |
                                   Q(user1_id=user2_id, user2_id=user1_id)).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class FriendsAddingView(viewsets.ModelViewSet):
    queryset = FriendsAdding.objects.all()
    serializer_class = FriendsAddingSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['sender__id', 'receiver__id']

    def create(self, request, *args, **kwargs):
        data = request.data
        sender = data['sender']
        receiver = data['receiver']
        friendship = data['friendship_id']

        if sender == receiver:  # Вообще не должно, но пусть будет
            return Response(
                {"detail": "Нельзя отправить заявку самому себе."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data={"sender": sender, "receiver": receiver, 'friendship': friendship})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = super(FriendsAddingView, self).get_queryset()
        sender_id = self.request.query_params.get('sender_id')
        receiver_id = self.request.query_params.get('receiver_id')

        if sender_id and receiver_id:
            return queryset.filter(receiver__id=receiver_id, sender__id=sender_id)

        if sender_id:
            return queryset.filter(sender__id=sender_id)

        if receiver_id:
            return queryset.filter(receiver__id=receiver_id)

    def destroy(self, request, *args, **kwargs):
        data = request.data
        sender = data['sender']
        receiver = data['receiver']
        friendship_id = data['friendship_id']

        if sender == receiver:
            return Response(
                {"detail": "Неверные данные."},
                status=status.HTTP_400_BAD_REQUEST
            )

        friend_adding = get_object_or_404(
            FriendsAdding,
            friendship_id=friendship_id,
            sender_id=sender,
            receiver_id=receiver
        )

        self.perform_destroy(friend_adding)
        return Response(request.data, status=status.HTTP_200_OK)


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

    @action(detail=False, methods=['get'], url_path='messages-unseen-count/')
    def get_unseen_count(self, request):
        chat_id = request.query_params.get('id')
        user_id = request.query_params.get('user_id')

        messages = Message.objects.filter(chat__id=chat_id, was_seen=False).exclude(sender=user_id)[:99]
        result = messages.aggregate(count=Count('id'))

        return Response(result)

    @action(detail=False, methods=['post'], url_path='messages-bulk/')
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data)

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


class ChatsView(viewsets.ModelViewSet):
    queryset = Chats.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["DM_id", 'group_id']
    serializer_class = ChatsSerializer

    def get_queryset(self):
        queryset = super(ChatsView, self).get_queryset()
        user_id = self.request.query_params.get('user_id')
        is_group = self.request.query_params.get('is_group')

        if user_id and is_group:
            is_group = bool(int(is_group))
            if not is_group:
                return queryset.filter(Q(DM__user1=user_id) | Q(DM__user2=user_id), is_group=is_group)
            return queryset.filter(group__members__id=user_id, is_group=is_group)

        return queryset

    def destroy(self, request, *args, **kwargs):
        dm_id = kwargs.get('DM_id')
        group_id = kwargs.get('group_id')

        obj = Chats.objects.filter(DM_id=dm_id).first()
        if not obj and group_id:
            obj = Chats.objects.filter(group_id=group_id).first()

        if not obj:
            return Response({'detail': 'Объект не найден'}, status=status.HTTP_404_NOT_FOUND)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

