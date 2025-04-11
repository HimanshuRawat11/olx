from rest_framework_simplejwt.tokens import AccessToken
from olx.settings import sio
from account.models import User
from asgiref.sync import sync_to_async
from django.db import transaction
from .models import Chat,Message,GroupAdmin
from django.db.models import Count


async def authenticate_user(sid,environ):
    query_string = environ.get("QUERY_STRING", "")
    params = dict(q.split("=") for q in query_string.split("&") if "=" in q)
    token = params.get("token")
    if not token:
        print("No token provided")
        await sio.disconnect(sid)
        return None
    try:
        decoded_token = AccessToken(token)
        user = await User.objects.aget(id=decoded_token["user_id"]) 
        return user
    except Exception as e:
        print(f"Authentication Error:{e}")
    except User.DoesNotExist as e:
        print(f"User doesnt Exist Occured:{e}")


@sync_to_async
def create_room_or_add(data):
    with transaction.atomic():
        try:
            user_ids = data["users"]
            print(user_ids)
            is_group = data["is_group"]
            group_name = data.get("group_name", None)
            chat_room_created = None
            group_admin = None

            if is_group:
                chat_room_created = Chat.objects.create(name=group_name, is_group=True)
                group_admin = GroupAdmin.objects.create(chat=chat_room_created, admin=User.objects.get(id=user_ids[0]))
            else:
                existing_chat = (
                    Chat.objects.filter(is_group=False, participants__id__in=user_ids)
                    .annotate(user_count=Count("participants", distinct=True)).filter(user_count=2).first()
                )
                if existing_chat:
                    if existing_chat.hidden_for.filter(id=user_ids[0]).exists():
                        existing_chat.hidden_for.remove(user_ids[0])
                        print("Existing")
                        return True 
                    print("not Existing")
                    return True  
                user1 = User.objects.get(id=user_ids[0])
                user2 = User.objects.get(id=user_ids[1])
                room_name = f"{user1.username}-{user2.username}"
                chat_room_created = Chat.objects.create(name=room_name, is_group=False)

            # Add participants to new chat room
            for uid in user_ids:
                user_obj = User.objects.get(id=uid)
                chat_room_created.participants.add(user_obj)
            print("created")
            return True

        except Exception as e:
            print("Error while creating chat room:", e)
            if chat_room_created:
                chat_room_created.delete()
            if group_admin:
                group_admin.delete()
            return False
            raise e

@sync_to_async
def delete_room_for_user(session_detail,data):
    with transaction.atomic():
        try:
            room_to_be_deleted=Chat.objects.get(id=data["room_id"])
            is_deleted=None
            try:
                user=User.objects.get(id=session_detail["id"])
                if Chat.objects.filter(id=room_to_be_deleted.id,participants__id=user.id).first():
                    is_deleted=room_to_be_deleted.delete_room(user)
                if is_deleted:
                    for message in Message.objects.filter(chat__id=room_to_be_deleted.id):
                        message.hidden_for.add(user)
                    return True
                else:
                    print("room was not deleted,The user is not a part of that room")
                    return False
            except Exception as e:
                print(f"An error occured while deleting:{e.with_traceback}")
                return False
        except Exception as e:
            print(f"Error Occured insufficient data :{e.with_traceback}")
            return False