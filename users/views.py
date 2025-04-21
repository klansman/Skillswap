from django.shortcuts import get_object_or_404
from users.serializers import UserSerializer, RegisterSerializer
from users.models import CustomUser
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

# Create your views here.
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = CustomUser.objects.all()

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    