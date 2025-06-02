from django.shortcuts import get_object_or_404
from users import serializers
from users.serializers import UserSerializer, RegisterSerializer, SkillSerializer, SwapRequestSerializer,NotificationSerializer, MessageSerializer
from users.models import CustomUser, Skill, SwapRequest, Notification, Message, Rating
from rest_framework import generics, viewsets, filters
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .filters import SkillFilter, StatusFilter
from rest_framework.pagination import PageNumberPagination
from django .db.models import Q
from users import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

# Create your views here.
class SkillPagination(PageNumberPagination):
    page_size = 10
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class SkillPagination(PageNumberPagination):
    page_size = 5
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
    filterset_class = StatusFilter

    def get_queryset(self):
        swaps = SwapRequest.objects.filter(receiver=self.request.user) | SwapRequest.objects.filter(sender=self.request.user)
        return swaps
    
class RespondToSwapRequestView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.SwapRespondSerializer
    queryset = SwapRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SwapRequest.objects.filter(receiver=self.request.user)

class CounterOfferView(generics.CreateAPIView):
    serializer_class = serializers.CounterOfferSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        counter_to_id = self.kwargs.get("pk")

        try:
            original_request = SwapRequest.objects.get(pk=counter_to_id)
        except SwapRequest.DoesNotExist:
            return Response({"detail": "Original swap request not found."}, status=status.HTTP_404_NOT_FOUND)

        if original_request.status != "pending":
            return Response({"detail": "Only pending requests can be countered."}, status=status.HTTP_400_BAD_REQUEST)

        if original_request.counter_to is not None:
            return Response({"detail": "You cannot counter a counter-offer."}, status=status.HTTP_400_BAD_REQUEST)

        if original_request.sender == request.user:
            return Response({"detail": "You cannot counter your own request."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save with context
        serializer = self.get_serializer(data=request.data, context={
            'request': request,
            'original_request': original_request
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Mark original as countered
        original_request.status = "countered"
        original_request.save()

        return Response({
            "message": "Counter-offer created successfully.",
            "counter_offer": serializer.data,
        }, status=status.HTTP_201_CREATED)

  
class RespondToCounterOfferView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = SwapRequest.objects.all()
    serializer_class=serializers.SwapRespondSerializer

    def patch(self, request, pk):
        #get counter offer from swapRequest objects and check if counter offer exists
        counter_offer_id = self.kwargs.get('pk')
        try:
            counter_offer = SwapRequest.objects.get(id=counter_offer_id, counter_to__isnull=False)
            print(f"coounterId:{counter_offer.id}")
        except SwapRequest.DoesNotExist:
            return Response({"detail":"Counter_offer does not esxist"}, status=status.HTTP_404_NOT_FOUND)
        #Allow only pending counter-offers to be responded to.
        original_request = counter_offer.counter_to
            #Make sure logged in user is the sender of the request
        if original_request.sender != request.user:
            return Response({"details":"You are not authorized to respond to this counter offer"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if counter_offer.status != 'pending':
            return Response({"details": "This counter-offer has already been responded to"}, status=status.HTTP_400_BAD_REQUEST)
        
        #Validate action — it must be either "accepted" or "rejected".
        action = request.data.get("action")
        if action == "accept":
            counter_offer.status = "accepted"
        elif action == "reject":
            counter_offer.status = "rejected"
        else:
            return Response({"details": "Invalid action. Must be 'accepted' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)
        #Update the counter-offer’s status accordingly.
        # counter_offer.status = action
        counter_offer.save()

        return Response({
            "message": f"Counter-offer has been {action}.",
            "counter_offer": SwapRequestSerializer(counter_offer).data
        }, status=status.HTTP_200_OK)


    
class UserNotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    ordering_fields = ['is_read']
    filterset_fields = ['is_read']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
    
class MarkNotificationReadView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient = self.request.user)
    
# class MessageViewSet(generics.ListCreateAPIView):
class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    query_set = Message.objects.all()
    pagination_class = SkillPagination

    def get_queryset(self):
        user=self.request.user
        if self.action == 'retrieve':
            return Message.objects.all()
        return Message.objects.filter(
            receiver = user 
        )| Message.objects.filter(
            sender = user)
        
    def perform_create(self, serializer, *args, **kwargs):
        swap_request = serializer.validated_data["swap_request"]
        swap_request_id = self.kwargs.get('pk')
        # Determine the receiver based on the swap request
        print(f" swapRequestID: {swap_request_id}")
        try:
            original_swap = SwapRequest.objects.get(pk=swap_request.id)
            print(f"original_swap: {original_swap}")
            print(f" swapRequestID: {swap_request_id}")

        except SwapRequest.DoesNotExist:
            return Response({"detail": "Original swap request not found."}, status=status.HTTP_404_NOT_FOUND)
        
        receiver = original_swap.receiver if original_swap.sender == self.request.user else original_swap.sender
        serializer.save(sender=self.request.user, receiver=receiver)

        
class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RatingSerializer
    permission_classes = [IsAuthenticated]
    queryset = Rating.objects.all()
    pagination_class = SkillPagination

    def get_queryset(self):
        if self.action == 'retrieve':
            return Rating.objects.all()
        return Rating.objects.filter(
            ratee = self.request.user
        )| Rating.objects.filter(
            rater = self.request.user)
    
    def perform_create(self, serializer, *args, **kwargs):
        # swap_id = self.kwargs.get('pk')
        swap_id = self.request.data.get('swap')
        print(f"swapId: {swap_id}")
        try:
            swap_to_rate= SwapRequest.objects.get(pk=swap_id)
            print(f"swap_to_rate: {swap_to_rate}")
        except SwapRequest.DoesNotExist:
            return Response({"detail": "Original swap request not found."}, status=status.HTTP_404_NOT_FOUND)
        
        ratee = swap_to_rate.receiver if swap_to_rate.sender==self.request.user else swap_to_rate.sender
        serializer.save(rater=self.request.user, ratee=ratee)



# class RatingViewSet(viewsets.ModelViewSet):
#     serializer_class = serializers.RatingSerializer
#     permission_classes = [IsAuthenticated]
#     # queryset = Rating.objects.all()

#     def get_queryset(self):
#         if self.action == 'GET':
#             return Rating.objects.all()
#         return Rating.objects.filter(
#             ratee = self.request.user 
#         )| Rating.objects.filter(
#             rater = self.request.user)
    
    # def perform_create(self, serializer, *args, **kwargs):
    #         swap = serializer.validated_data['swap']
    #         swap_id = self.kwargs.get('pk')
    #         user = serializer.context['request'].user
    #         try:
    #             swap_to_rate = SwapRequest.objects.get(pk=swap_id)
               
    #         except SwapRequest.DoesNotExist:
                
    #             return Response({"detail: Swap not found"},
    #             status=status.HTTP_404_NOT_FOUND)
            
    #         serializer.validated_data['ratee'] = swap_to_rate.receiver if swap_to_rate.sender == user else swap_to_rate.sender

    #         serializer.save(serializer.validated_data)
    #         # return super().create(serializer.validated_data)

    #         return Response({
    #         "rating": serializers.RatingSerializer.data,
    #     }, status=status.HTTP_200_OK)
        