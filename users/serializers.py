from rest_framework import serializers
from .models import CustomUser, Skill

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
    user = CustomUserSerializer(read_only=True) 
    class Meta:
        model = Skill
        # fields = '__all__'
        fields = ['id', 'name', 'description', 'created', 'user']