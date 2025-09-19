from django.db import models


class Users(models.Model):
    nickname = models.CharField(max_length=10, unique=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    secondname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    last_online = models.DateTimeField(auto_now_add=True, null=True)
    password = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.secondname} {self.firstname} {self.lastname}"


class FriendsAdding(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='received_friend_requests')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка в друзья'
        verbose_name_plural = 'Заявки в друзья'


class Friendship(models.Model):
    REQUESTED = 1
    CONFIRMED = 2
    BLOCKED = 3

    STATUS_CHOICES = (
        (REQUESTED, 'Requested'),
        (CONFIRMED, 'Confirmed'),
        (BLOCKED, 'Blocked'),
    )

    user1 = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friendships_initiated')
    user2 = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='friendships_received')
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Друг'
        verbose_name_plural = 'Друзья'
        unique_together = ('user1', 'user2')


class Message(models.Model):
    UNSEEN = False
    SEEN = True

    CHOICES = (
        (UNSEEN, 'UNSEEN'),
        (SEEN, 'SEEN'),
    )

    chat = models.ForeignKey(Friendship, on_delete=models.CASCADE)
    sender = models.ForeignKey(Users, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    was_seen = models.BooleanField(choices=CHOICES, default=UNSEEN)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-id']

    def __str__(self):
        return f"{self.sender}: {self.message}"
