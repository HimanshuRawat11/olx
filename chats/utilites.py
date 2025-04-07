from rest_framework_simplejwt.tokens import AccessToken
from olx.settings import sio
from account.models import User


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