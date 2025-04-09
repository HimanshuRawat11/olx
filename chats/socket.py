from olx.settings import sio
from asgiref.sync import sync_to_async
from account.models import User
from .models import Message,Chat,GroupAdmin
from django.db import transaction
from .utilites import authenticate_user
import json
from django.db.models import Count
# from channels 
from datetime import datetime


@sio.event
async def chat_homepage(sid,data):
    session_details=await sio.get_session(sid)
    user=await User.objects.aget(id=session_details["id"])
    chat_details=[]
    
    async for chat in Chat.objects.filter(participants__id=user.id).exclude(hidden_for=user):
        chat_items = {
            "chat_id": chat.id,
            "chat_name": chat.name,
            "is_group": chat.is_group,
        }

        unread = await Message.objects.filter(
            chat__id=chat.id,is_read=False,chat__participants__id=user.id).exclude(sender=user).values('chat_id').annotate(count=Count('text')).order_by('chat_id').afirst()
        chat_items["unread_message"] = unread.get("count", 0) if unread else 0
        last_msg = await Message.objects.filter(chat=chat).values('id','text', 'timestamp').order_by('timestamp').alast()

        if last_msg:
            chat_items["last_message"] = {
                "text": last_msg["text"],
                "timestamp": last_msg["timestamp"].isoformat()  
            }
            chat_items["last_message_id"] = last_msg["id"]

        else:
            chat_items["last_message"] = None
            chat_items["last_message_id"] = -1

        chat_details.append(chat_items)

    chat_details.sort(key=lambda x: x["last_message_id"], reverse=True)

    for chat in chat_details:
        chat.pop("last_message_id", None)
                
    await sio.emit("chat_homepage_display",{"data":chat_details},to=sid)



@sio.event
async def connect(sid, environ):
    user_authenticated=await authenticate_user(sid,environ)
    
    if not user_authenticated:
        print("Invalid user")
        await sio.disconnect(sid)
        return 
    
    print(f"User {user_authenticated.username} connected with socket ID {sid}")
    await sio.save_session(sid, {'id':user_authenticated.id,'username': user_authenticated.username,'email':user_authenticated.email})

    await sio.emit("auth_success", {"message": f"Welcome {user_authenticated.username}!"},to=sid)


@sio.event
async def create_room(sid,data):
        try:
            user=data["users"]
            is_group_or_not=data["is_group"]
            group_name=data["group_name"]
            if is_group_or_not:
                chat_room_created = await Chat.objects.acreate(name=group_name,is_group=is_group_or_not)
                group_admin=await GroupAdmin.objects.acreate(chat=chat_room_created,admin=await User.objects.aget(id=user[0]))
            else:
                user1_details=await User.objects.aget(id=user[0])
                user2_details=await User.objects.aget(id=user[1])
                room_name='-'.join([user1_details.username,user2_details.username])
                chat_room_created = await Chat.objects.acreate(name=room_name,is_group=is_group_or_not)

            for users in user:
                user_instance = await User.objects.aget(id=users)  
                await chat_room_created.participants.aadd(user_instance) 

        except Exception as innerException:
            print("inner exception  occured")
            if is_group_or_not:
                await group_admin.adelete()

            await chat_room_created.adelete()
            raise innerException
        

@sio.event
async def enter_room(sid,data):
    try:
        session_detail= await sio.get_session(sid)
        user=await User.objects.aget(id=session_detail["id"])
        chat_room=await Chat.objects.aget(id=data["room_id"])
        
        await Message.objects.filter(chat__id=chat_room.id).values('chat_id').exclude(sender=user).aupdate(is_read=True)

        messages=[]
        async for message in  Message.objects.select_related('sender').filter(chat=chat_room).order_by('timestamp').exclude(hidden_for=user).exclude(is_deleted_for_everyone=True):
            current_message={}
            current_message["message_id"]=message.id
            current_message["message"]=message.text
            current_message["sent_by"] = message.sender.id.hex
            current_message["sent_on"]=message.timestamp.isoformat()
            messages.append(current_message)
        await sio.enter_room(sid,chat_room.name)
        await sio.emit("room_message_display",{"data":messages},to=sid)
        return "Joined room"
    except Exception as e:
        print(f"Error occured{e}")


@sio.event
async def delete_for_me(sid,data):
    session_detail=await sio.get_session(sid)
    message_to_be_deleted=await Message.objects.aget(id=data["message_id"])
    try:
        user=await User.objects.aget(id=session_detail["id"])
        is_deleted=await message_to_be_deleted.adelete_for_me(user)
    
        if is_deleted:
            print(f"Message Deleted for user {user.username}")
        else:
            print(f"Message not Deleted")    
    except Exception as e:
        print(f"Error Occured {e}")




@sio.event
async def delete_for_everyone(sid,data):
    session_detail=await sio.get_session(sid)
    message_to_be_deleted=await Message.objects.aget(id=data["message_id"])
    try:
        user=await User.objects.aget(id=session_detail["id"])
        is_deleted=await message_to_be_deleted.adelete_for_everyone(user,data["message_id"])

        if is_deleted:
            print(f"Message Deleted for user")
        else:
            print(f"Message not Deleted:Only the sender can perform this action")    
    except Exception as e:
        print(f"Error Occured {e}")


@sio.event
async def delete_room(sid,data):
    try:
        session_detail=await sio.get_session(sid)
        room_to_be_deleted=await Chat.objects.aget(id=data["room_id"])
        try:
            user=await User.objects.aget(id=session_detail["id"])
            is_deleted=await room_to_be_deleted.adelete_room(user)
            if is_deleted:
                await Message.objects.filter(chat__id=room_to_be_deleted.id).a
                await sio.emit("room_deleted",{"message":"Room was deleted"},to=sid)
            else:
                print("room was not deleted")
        except Exception as e:
            print(f"An error occured while deleting:{e.with_traceback}")
    except Exception as e:
        print(f"Error Occured insufficient data :{e.with_traceback}")


@sio.event
async def exit_room(sid,data):
    room=data["room"]
    await sio.leave_room(sid,room)
    return "leaving room"


async def store_message(sid, data,session_detail):
    try:
        room=await Chat.objects.aget(id=data["room_id"])
        user=await User.objects.aget(id=session_detail["id"])

        await Message.objects.acreate(chat=room,sender=user, text=data["message"])
    except Exception as e:
        print(e)


@sio.event
async def send_message(sid, data):
    session_detail= await sio.get_session(sid)
    message = data["message"]
    print(data)
    room=await Chat.objects.aget(id=data["room_id"])
    print(f"{message}  in room {room.name}")
    await store_message(sid, data,session_detail)

    await sio.emit('get_message', {"message": message}, room=room)



@sio.event
async def get_room_members(sid, data):
    room = data['room']
    members = sio.manager.rooms.get('/', {}).get(room, set()) 
    members_list = list(members)
    print(f"Members in room {room}: {members_list}")
    await sio.emit('room_members', {'room': room, 'members': members_list}, to=sid)


@sio.event
def disconnect(sid):
    print("Disconnected")
