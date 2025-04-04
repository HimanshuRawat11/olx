from olx.settings import sio
from asgiref.sync import sync_to_async
from .models import RoomInfo,RoomMembers,Messages



@sio.event
async def connect(sid, environ):
    query_string = environ.get("QUERY_STRING", "")
    params = dict(q.split("=") for q in query_string.split("&") if "=" in q)
    token = params.get("token")
    
    if not token:
        print("No token provided")
        await sio.disconnect(sid)
        return


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
        await sync_to_async(Messages.objects.create, thread_sensitive=True)(
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
