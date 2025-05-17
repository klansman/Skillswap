"""
ASGI config for SKILLSWAP project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from django.urls import path
# import django
# import users.routing  # Make sure this is added

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SKILLSWAP.settings')
# django.setup()
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             users.routing.websocket_urlpatterns
#         )
#     ),
# })

import os
import django
from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SkillSwap.settings")
django.setup()  # 👈 MUST COME BEFORE anything using models/settings

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from users.middleware import JWTAuthMiddleware
import users.routing
from users.routing import websocket_urlpatterns  # Import after setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            users.routing.websocket_urlpatterns
        )
    ),
})
