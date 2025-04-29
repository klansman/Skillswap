import json
import os
from rest_framework.serializers import ListSerializer
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SKILLSWAP.settings')
django.setup()

from users.serializers import SkillSerializer  # Import SkillSerializer
from users.models import Skill, CustomUser
from rest_framework import serializers

class SkillSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    created_by = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Skill
        fields = ['id', 'name', 'description', 'user', 'created_by']



def load_skill_data(json_file_path):
    """
    Loads skill data from a JSON file, deserializes it using SkillSerializer,
    and creates Skill objects in the database.

    Args:
        json_file_path (str): The path to the JSON file containing the data.
    """
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        print(f"Successfully loaded JSON data from {json_file_path}")
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {json_file_path}: {e}")
        return

    skill_data = [item for item in data if item['model'] == 'users.skill']
    print(f"Filtered skill_data: {skill_data}")

    serializer = ListSerializer(data=skill_data, child=SkillSerializer(many=True))
    print(f"Serializer initialized: {serializer}")

    if serializer.is_valid():
        print("Serializer is valid")
        for item in serializer.validated_data:
            validated_data = item # Change: Use the entire item 
            print(f"Validated data: {validated_data}")
            try:
                user_instance = CustomUser.objects.get(pk=validated_data['user'])
                print(f"Found user: {user_instance}")
            except CustomUser.DoesNotExist:
                print(f"Error: User with pk={validated_data['user']} does not exist.  Skipping skill.")
                continue

            try:
                skill = Skill.objects.create(
                    name=validated_data['name'],
                    description=validated_data['description'],
                    user=user_instance,
                    created_by=user_instance,
                )
                print(f"Successfully created skill: {skill}")
            except Exception as e:
                print(f"Error creating skill: {e}")
        print("Skill data loaded successfully!")
    else:
        print("Serializer is invalid. Errors: {serializer.errors}")
        print(f"Full data passed to serializer: {serializer.data}")
        return

if __name__ == "__main__":
    json_file_path = 'sample_data.json'
    load_skill_data(json_file_path)
