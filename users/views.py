from django.shortcuts import get_object_or_404
from users.serializers import UserSerializer, RegisterSerializer, SkillSerializer
from users.models import CustomUser, Skill
from rest_framework import generics, viewsets
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
    
class SkillViewSet(viewsets.ModelViewSet):
    serializer_class = SkillSerializer
    # queryset = Skill.objects.all()
    permission_classes = [IsAuthenticated]

    # def get_permissions(self):
    #     self.permission_classes = [AllowAny]
    #     if self.request.method in ['DELETE', 'PATCH', 'PUT']:
    #         self.permission_classes = [IsAuthenticated]
    #     return super().get_permissions()

    def get_queryset(self): #Shows only skills creaated by logged in user
        return Skill.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer): #Automatically assigns the logged in user as skill owner when created
        serializer.save(user=self.request.user)
    