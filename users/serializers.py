from rest_framework import serializers
from .models import CustomUser, Skill, SwapRequest, Notification, Message
from users import models
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    # username = serializers.CharField(max_length=100)
    get_average_rating = serializers.SerializerMethodField()
    get_ratings_count = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'bio', 'skills', 'average_rating', 'ratings_count']

    def get_average_rating(self, obj):
        return obj.average_rating()
    
    def get_ratings_count(self, obj):
        return obj.ratings_count()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password']


    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username = validated_data['username'],
            password = validated_data['password'],
            email = validated_data['email']
        )
        return user

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields =  ['username', 'email', 'id']
    
class SkillSerializer(serializers.ModelSerializer):
    # user = CustomUserSerializer(read_only=True) 
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), default=serializers.CurrentUserDefault())
    # created_by = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Skill
        # fields = '__all__'
        fields = ['id', 'name', 'description' ,'created', 'user']


class SwapRespondSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'sender', 'created_at', 'receiver', 'sender_skill', 'receiver_skill', 'status']
        model = SwapRequest
        read_only_fields = ['sender', 'created_at', 'receiver', 'sender_skill', 'receiver_skill']
    def update(self, instance, validated_data):
        old_status = instance.status #Get current status of the Swap from the DB
        new_status = validated_data.get('status', old_status) #Checks if user is trying to change status, defaults to current status if not
        allowed_transitions = { 
            #Defines what transition are allowed, once accepted or rejected it cannot be changed anymore
            'pending': ['accepted', 'rejected'],
            'rejected' : [],
            'accepted' : []
        }
        if new_status != old_status and new_status not in allowed_transitions.get(old_status, []):
            raise serializers.ValidationError(f"Cannot change status from '{old_status}' to '{new_status}'")
        else:
            pass
        return super().update(instance, validated_data)

   
class SwapRequestSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'sender', 'created_at', 'receiver', 'sender_skill', 'receiver_skill', 'status']
        model = SwapRequest
        read_only_fields = ['sender', 'status', 'created_at','id']

    def __init__(self, *args, **kwargs): #making each field to contain only the selected user skills
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        user = request.user if request else None
        if user:
            # Set sender and receiver querysets
            # self.fields['receiver'].queryset = CustomUser.objects.exclude(id=user.id)
            self.fields['sender_skill'].queryset = Skill.objects.filter(user=user)

            # Safely access incoming data
            receiver_id = request.data.get('receiver')
            print(receiver_id)
            if not receiver_id:
                counter_to_id = request.parser_context['kwargs'].get('pk')
                try:
                    from users.models import SwapRequest
                    original_request =SwapRequest.objects.get(pk=counter_to_id)
                    receiver_id = original_request.sender.id
                except Exception:
                    receiver_id =None
            if receiver_id:
                try:
                    self.fields['receiver_skill'].queryset = Skill.objects.filter(user_id=str(receiver_id))
                except (ValueError, TypeError):
                    self.fields['receiver_skill'].queryset = Skill.objects.none()
            else:
                self.fields['receiver_skill'].queryset = Skill.objects.none()
        else:
            self.fields['receiver_skill'].queryset = Skill.objects.none()
        

    def validate(self, attrs):
        """
        Ensure receiver_skill belongs to the selected receiver.
        """
        receiver = attrs.get('receiver')
        receiver_skill = attrs.get('receiver_skill')

        if receiver and receiver_skill:
            if receiver_skill.user != receiver:
                raise serializers.ValidationError("receiver skill must belong to the selected receiver.")

        return attrs
    
class CounterOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwapRequest
        fields = ['sender_skill', 'receiver_skill']
        # sender and receiver are inferred; status is auto
        extra_kwargs = {
            'sender_skill': {'required': True},
            'receiver_skill': {'required': True}
        }

    def validate(self, attrs):
        request = self.context['request']
        original_request = self.context.get('original_request')

        sender = request.user
        receiver = original_request.sender

        sender_skill = attrs.get('sender_skill')
        receiver_skill = attrs.get('receiver_skill')

        # Validate skill ownership
        if sender_skill.user != sender:
            raise serializers.ValidationError("Selected sender_skill does not belong to you.")

        if receiver_skill.user != receiver:
            raise serializers.ValidationError("Selected receiver_skill does not belong to the original sender.")

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        original_request = self.context.get('original_request')

        return SwapRequest.objects.create(
            sender=request.user,
            receiver=original_request.sender,
            sender_skill=validated_data['sender_skill'],
            receiver_skill=validated_data['receiver_skill'],
            status='pending',
            counter_to=original_request
        )

    #Note that when countering offers sender becomes receiver and vise versa so the skill ids should also change respectively
    
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'recipient', 'message', 'created_at', 'is_read']
        read_only_fields = ['id', 'recipient', 'message', 'created_at']
        model = Notification

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')
    receiver = serializers.ReadOnlyField(source='receiver.username')

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'swap_request', 'content', 'timestamp']
        read_only_fields = ['sender', 'timestamp', 'receiver', 'id']

class RatingSerializer(serializers.ModelSerializer):
#Goal: Ensure users can only rate after a completed swap and can’t rate the same trade multiple times.
    class Meta:
        model = models.Rating
        fields = ['id', 'rater', 'ratee', 'swap', 'rating', 'created_at']
        read_only_fields = ['id', 'rater']

        #Get logged in user to be the rater and the swap
        def validate(self, data):
            swap = data['swap']
            print(f"swap: {swap}")
            request_user = self.context['request'].user
        #Check if swap has been completed ie accepted
            if swap.status != 'accepted':
                raise serializers.ValidationError("You can only rate swaps that have been accepted")

        #Check if swap has been rated before
            if models.Rating.objects.filter(swap=swap, rater=request_user).exists():
                raise serializers.ValidationError ("This swap already has a rating")
            
        #Ensure users only rate swap they are part of
            if request_user not in(swap.sender, swap.receiver):
                raise serializers.ValidationError("You can only rate swaps that you are part of")
        
        
        def create(self, validated_data):
            user = self.context['request'].user
            swap = validated_data['swap']
            validated_data['rater'] = user
            print(user.id)

        # Automatically determine the ratee (opposite party in swap)
            validated_data['ratee'] = swap.receiver if swap.sender == user else swap.sender
            return super().create(validated_data)