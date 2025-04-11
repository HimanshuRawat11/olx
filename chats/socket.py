from olx.settings import sio
from asgiref.sync import sync_to_async
from account.models import User
from .models import Message,Chat,GroupAdmin
from .utilites import authenticate_user
from django.db.models import Count
from datetime import datetime
from .utilites import create_room_or_add,delete_room_for_user

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
        last_msg = await Message.objects.filter(chat=chat).values('id','text', 'timestamp').order_by('timestamp').exclude(hidden_for=user).alast()

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
            is_room_created=await create_room_or_add(data)
            print(is_room_created)
            if is_room_created:
                await sio.emit("room_created",{"message":"The room was created and user is in the room now"},to=sid)
        except Exception as e:
            print(f"exception  occured :{e}")

@sio.event
async def entering_room(sid,data):
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
        # print(chat_room.name)
        await sio.enter_room(sid,chat_room.name)
        
        await sio.emit("room_message_display",{"data":messages},to=sid)
        return "Joined room"
    except Exception as e:
        print(f"Error occured{e}")


@sio.event
async def add_to_group(sid,data):
    try:
        session_details=await sio.get_session(sid)
        user_adding=await User.objects.aget(id=session_details["id"])
        user_to_add=await User.objects.aget(id=data["user_id"])
        group_chat=await Chat.objects.aget(id=data["room_id"])

        try:
            if await group_chat.participants.filter(id=user_to_add.id).aexists():
               return "user is already in the group"
            if await GroupAdmin.objects.aget(chat=group_chat,admin=user_adding):
                if await group_chat.hidden_for.filter(id=user_to_add.id).aexists():
                    await group_chat.hidden_for.aremove(user_to_add.id)
                    return "User was added back to the group"
                await group_chat.participants.aadd(user_to_add)    
                return "New user was added "
            await sio.emit("NotAdmin",{"message":"Only an admin can add other person in te group"},to=sid)     
            return "Only Admin can perform this Action of adding user to the group"
        
        except User.DoesNotExist as e:
            print(f"The user doesnt exist witht this id {e}")
        except Exception as e:
            print(f"Error occured while adding the user in the group")
    except Exception as e:
        print(f"Exception occured Some value was not provided{e.with_traceback}")



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
        room_is_deleted=await delete_room_for_user(session_detail,data)

        if room_is_deleted:
            await sio.emit("room_deleted",{"message":"The room was deleted"},to=sid)
            return "Done"
        await sio.emit("room_deleted",{"message":"The room was not  deleted"},to=sid)
        return "The room was not deleted"
    except Exception as e:
        print(f"Error Occured insufficient data :{e.with_traceback}")




@sio.event
async def exit_room(sid,data):
    room=await Chat.objects.aget(id=data["room_id"])
    await sio.leave_room(sid,room.name)
    return "leaving room"


async def store_message(sid, data,session_detail):
    try:
        room=await Chat.objects.aget(id=data["room_id"])
        user=await User.objects.aget(id=session_detail["id"])

        message_created=await Message.objects.acreate(chat=room,sender=user, text=data["message"])
        if message_created:
            return message_created
        return None
    except Exception as e:
        print(e)



@sio.event
async def send_message(sid, data):
    session_detail= await sio.get_session(sid)
    message = data["message"]
    print(data)
    room=await Chat.objects.aget(id=data["room_id"])
    print(f"{message}  in room {room.name}")
    message_stored=await store_message(sid, data,session_detail)
    if message_stored:
        members_in_room=await get_room_members(sid,data)
        for member in members_in_room:
            user_session_detail=await sio.get_session(member)
            user=await User.objects.aget(id=user_session_detail["id"])
            if not message_stored.sender==user:
                message_stored.is_read=True
                await message_stored.asave()
                print("Message sent and read by the user")
                return
        print("Message sent")
        return
    
    await sio.emit('get_message', {"message": message}, room=room)



async def get_room_members(sid, data):
    room=await Chat.objects.aget(id=data["room_id"])
    members =  sio.manager.rooms.get('/', {}).get(room.name, set()) 
    members_list = list(members)
    return members_list

@sio.event
def disconnect(sid):
    print("Disconnected")
 