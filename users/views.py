from django.shortcuts import get_object_or_404
from users import serializers
from users.serializers import UserSerializer, RegisterSerializer, SkillSerializer, SwapRequestSerializer,NotificationSerializer
from users.models import CustomUser, Skill, SwapRequest, Notification
from rest_framework import generics, viewsets, filters
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .filters import SkillFilter
from rest_framework.pagination import PageNumberPagination
from django .db.models import Q
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
    
class SwapRequestAPIView(generics.ListCreateAPIView):
    serializer_class = SwapRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SwapRequest.objects.filter(receiver=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class MySwapRequestView(generics.ListAPIView):
    serializer_class = SwapRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        swaps = SwapRequest.objects.filter(receiver=self.request.user) | SwapRequest.objects.filter(sender=self.request.user)
        return swaps
    
class RespondToSwapRequestView(generics.RetrieveUpdateAPIView):
    serializer_class = SwapRequestSerializer
    queryset = SwapRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SwapRequest.objects.filter(receiver=self.request.user)
    
    def perform_update(self, serializer):
        instance = serializer.instance
        new_status = self.request.data.get('status')

        if instance.status != 'pending':
            raise serializers.ValidationError("You can only respond to pending swap requests.")

        if new_status not in ['accepted', 'declined']:
            raise serializers.ValidationError("Status must be 'accepted' or 'declined'.")

        serializer.save(status=new_status)
        return super().perform_update(serializer)
    
  
class UserNotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
    
class MarkNotificationReadView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient = self.request.user)
    





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
    