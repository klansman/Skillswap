from django_filters import rest_framework as filters
from .models import CustomUser, Skill

class SkillFilter(filters.FilterSet):
    name_contains = filters.CharFilter(field_name="name", lookup_expr="icontains")
    class Meta:
        model = Skill
        fields = ['name_contains']

class StatusFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=[('pending', 'Pending'), ('accepted', 'Accepted'),('rejected', 'Rejected')], field_name="status")

