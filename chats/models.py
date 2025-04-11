from django.db import models
from account.models import User
from django.db import models


class Chat(models.Model):

    name = models.CharField(max_length=255, blank=True, null=True) 
    is_group = models.BooleanField(default=False)
    participants = models.ManyToManyField(User, related_name='chats')
    
    hidden_for = models.ManyToManyField(User, related_name='hidden_chat', blank=True)
    
    async def adelete_room(self,user):
        await self.hidden_for.aadd(user)
        return True
    def delete_room(self,user):
        self.hidden_for.add(user)
        return True
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

    is_deleted_for_everyone = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, 
                                    related_name='deleted_messages')

    hidden_for = models.ManyToManyField(User, related_name='hidden_messages', blank=True)

    
    async def adelete_for_everyone(self, user,mesg_id):
        message_to_be_deleted=await Message.objects.select_related('sender').aget(id=mesg_id)
        
        if message_to_be_deleted.sender == user:
            self.is_deleted_for_everyone = True
            self.deleted_by = user
            await self.asave()
            return True
        return False
        
    async def adelete_for_me(self, user):
        await self.hidden_for.aadd(user)
        return True

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


