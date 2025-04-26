from django_filters import rest_framework as filters
from .models import CustomUser, Skill

class SkillFilter(filters.FilterSet):
    name_contains = filters.CharFilter(field_name="name", lookup_expr="icontains")
    class Meta:
        model = Skill
        fields = ['name_contains']

