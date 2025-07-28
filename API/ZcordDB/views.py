from rest_framework import viewsets
from .models import Users, Friendship, Message, FriendsAdding
from .serializers.UserSerializer import UserSerializer
from .serializers.FriendshipSerializer import FriendshipSerializer
from .serializers.MessageSerializer import MessageSerializer
from .serializers.FriendsAddingSerializer import FriendsAddingSerializer


class UserView(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer


class FriendshipView(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer


class FriendsAddingView(viewsets.ModelViewSet):
    queryset = FriendsAdding.objects.all()
    serializer_class = FriendsAddingSerializer


class MessageView(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
