from rest_framework import viewsets, filters
from .models import Users, Friendship, Message, FriendsAdding
from .serializers.UserSerializer import UserSerializer
from .serializers.FriendshipSerializer import FriendshipSerializer
from .serializers.MessageSerializer import MessageSerializer
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
    serializer_class = MessageSerializer
