from rest_framework import serializers
from .models import CustomUser, Skill, SwapRequest, Notification

class UserSerializer(serializers.ModelSerializer):
    # username = serializers.CharField(max_length=100)
    # email = serializers.EmailField(blank = True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'bio', 'skills']

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
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    # created_by = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Skill
        # fields = '__all__'
        fields = ['id', 'name', 'description' ,'created', 'user']



class SwapRequestSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'sender', 'created_at', 'receiver', 'sender_skill', 'receiver_skill', 'status']
        model = SwapRequest
        read_only_fields = ['sender', 'status', 'created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request:
            user = request.user
            # Set sender and receiver querysets
            self.fields['receiver'].queryset = CustomUser.objects.exclude(id=user.id)
            self.fields['sender_skill'].queryset = Skill.objects.filter(user=user)

            # Safely access incoming data
            receiver_id = request.data.get('receiver')
            print(receiver_id)
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
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'recipient', 'swap_request', 'message', 'created_at', 'is_read']
        model = Notification

