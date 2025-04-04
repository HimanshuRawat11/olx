from olx.settings import sio
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from account.models import User
from .models import Message,Chat,GroupAdmin
from django.db import transaction



@sio.event
async def connect(sid, environ):
    query_string = environ.get("QUERY_STRING", "")
    params = dict(q.split("=") for q in query_string.split("&") if "=" in q)
    token = params.get("token")
    if not token:
        print("No token provided")
        await sio.disconnect(sid)
        return

    try:
        decoded_token = AccessToken(token)
        user = await User.objects.aget(id=decoded_token["user_id"]) 

        if not user:
            print("Invalid user")
            await sio.disconnect(sid)
            return

        print(f"User {user.username} connected with socket ID {sid}")
        await sio.emit("auth_success", {"message": f"Welcome {user.username}!"}, room=sid)

    except User.DoesNotExist:
        print("User not found")
        await sio.disconnect(sid)

    except Exception as e:
        print(f"Authentication error: {e}")
        await sio.disconnect(sid)


@sio.event
async def create_room(sid,data):
        try:
            user=data["users"]
            is_group_or_not=data["is_group"]
            group_name=data["group_name"]
            if group_name:
                chat_room_created = await Chat.objects.acreate(name=group_name,is_group=is_group_or_not)
            else:
                user1_details=await User.objects.aget(id=user[0])
                user2_details=await User.objects.aget(id=user[1])
                room_name='-'.join([user1_details.username,user2_details.username])
                chat_room_created = await Chat.objects.acreate(name=room_name,is_group=is_group_or_not)
            

            for users in user:
                user_instance = await User.objects.aget(id=users)  
                await chat_room_created.participants.aadd(user_instance) 

        except Exception as innerException:
            await chat_room_created.adelete()
            print("inner exception  occured")
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


async def store_message(sid, data):
    try:
        room = data["room"]
        message = data["message"]
        sender = sid
        await sync_to_async(Message.objects.create, thread_sensitive=True)(
            room=room, message=message, sender=sender
        )
    except Exception as e:
        print(e)


@sio.event
async def send_message(sid, data):
    room = data["room"]
    message = data["message"]
    print(f"{message} sent by {sid} in room {room}")
    await store_message(sid, data)

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
