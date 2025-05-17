# users/middleware.py

from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.db import close_old_connections

User = get_user_model()

@database_sync_to_async
def get_user(token):
    try:
        access_token = AccessToken(token)
        user = User.objects.get(id=access_token['user_id'])
        return user
    except Exception:
        return None

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope["headers"])
        token = None

        # Normalize headers (case-insensitive)
        for header_name, value in headers.items():
            if header_name.lower() == b'authorization':
                auth_header = value.decode()
                if auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                break  # No need to keep looping once we find it

        scope["user"] = await get_user(token)
        return await super().__call__(scope, receive, send)
