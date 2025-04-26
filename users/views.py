from django.shortcuts import get_object_or_404
from users.serializers import UserSerializer, RegisterSerializer, SkillSerializer
from users.models import CustomUser, Skill
from rest_framework import generics, viewsets, filters
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .filters import SkillFilter
from rest_framework.pagination import PageNumberPagination

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
    
class SkillPagination(PageNumberPagination):
    page_size = 10
class SkillsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SkillSerializer
    queryset = Skill.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SkillFilter
    pagination_class = SkillPagination
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created']

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    def perform_create(self, serializer): #Automatically assigns the logged in user as skill owner when created
        serializer.save(user=self.request.user)
    
class SkillsDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SkillSerializer
    queryset = Skill.objects.all()

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['DELETE', 'PATCH', 'PUT']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

# class SkillViewSet(viewsets.ModelViewSet):
#     serializer_class = SkillSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = SkillFilter
#     permission_classes = [IsAuthenticated]

    

#     def get_queryset(self): #Shows only skills creaated by logged in user
#         return Skill.objects.filter(user=self.request.user)
#         # return Skill.objects.all()
    
#     def perform_create(self, serializer): #Automatically assigns the logged in user as skill owner when created
#         serializer.save(user=self.request.user)
    