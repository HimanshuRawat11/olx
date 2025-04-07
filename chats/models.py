from django.db import models
from account.models import User

# Create your models here.

# class RoomInfo(models.Model):
#     room_name=models.CharField(max_length=255)
#     class Meta:
#         db_table="rooms"

# class RoomMembers(models.Model):
#     user=models.ForeignKey(User,on_delete=models.CASCADE)
#     room=models.ForeignKey(RoomInfo,on_delete=models.CASCADE)
#     class Meta:
#         db_table="room_members"



# class Messages(models.Model):
#     sender=models.ForeignKey(User,on_delete=models.CASCADE)
#     room=models.ForeignKey(RoomInfo,on_delete=models.CASCADE)
#     message=models.TextField()
#     created_at=models.DateTimeField(auto_now_add=True)
#     class Meta:
#         db_table="messages"



from django.db import models

class Chat(models.Model):

    name = models.CharField(max_length=255, blank=True, null=True) 
    is_group = models.BooleanField(default=False)
    participants = models.ManyToManyField(User, related_name='chats')

    class Meta:
        db_table="chats"
    def __str__(self):
        return self.name if self.is_group else f"Chat between {', '.join([user.username for user in self.participants.all()])}"


class Message(models.Model):
    
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table="messages"

    def __str__(self):
        return f"Message from {self.sender.username} in {self.chat}"


class GroupAdmin(models.Model):
    
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="group_admins")
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="admin_groups")
    
    class Meta:
        db_table="group_details"
        unique_together = ('chat', 'admin')  

    def __str__(self):
        return f"{self.admin.username} is admin of {self.chat.name}"


