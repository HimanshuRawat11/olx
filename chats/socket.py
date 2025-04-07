from olx.settings import sio
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from account.models import User
from .models import Message,Chat,GroupAdmin
from django.db import transaction
from .utilites import authenticate_user
import json
from asgiref.sync import sync_to_async


async def chat_homepage(sid):
    session_details=await sio.get_session(sid)
    user=await User.objects.aget(id=session_details["id"])
    chat_details=[]
    async for chat in Chat.objects.filter(participants__id=user.id):
            chat_items={}
            chat_items["Chat_name"]=chat.name
            chat_items["Is_group"]=chat.is_group
            
            chat_details.append(chat_items)
    return chat_details



@sio.event
async def connect(sid, environ):
    user_authenticated=await authenticate_user(sid,environ)
    
    if not user_authenticated:
        print("Invalid user")
        await sio.disconnect(sid)
        return 
    
    print(f"User {user_authenticated.username} connected with socket ID {sid}")
    await sio.save_session(sid, {'id':user_authenticated.id,'username': user_authenticated.username,'email':user_authenticated.email})
    chat_room_data=await chat_homepage(sid)
    chat_room_data=json.dumps(chat_room_data)
    print(chat_room_data)

    await sio.emit("auth_success", {"message": f"Welcome {user_authenticated.username}!","chat_room":chat_room_data},to=sid)


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
    room=data["room"]
    await sio.enter_room(sid,room)
    return "Joined room"


@sio.event
async def exit_room(sid,data):
    room=data["room"]
    await sio.leave_room(sid,room)
    return "leaving room"


async def store_message(sid, data,session_detail):
    try:
        room=await Chat.objects.aget(id=data["room_id"])
        user= await User.objects.aget(id=session_detail["id"])

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


# @sio.event
# async def messageSent(sid,data):
#     room=data["room"]
#     message=data["message"]
#     room_members = sio.rooms(sid)
#     await sio.emit("messageRecieved",{"user":sid,"message":message,"members":room_members},room=room)



@sio.event
def disconnect(sid):
    print("Disconnected")
