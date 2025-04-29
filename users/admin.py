from django.contrib import admin
from .models import CustomUser, Skill, SwapRequest

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created')
    search_fields = ('name', 'user__username')
    list_filter = ('created',)
    ordering = ('-created',)

@admin.action(description="Accept selected swap requests")
def make_accepted(modeladmin, request, queryset):
    queryset.update(status='accepted')  # assuming 'accepted' is your status value

@admin.action(description="Reject selected swap requests")
def make_rejected(modeladmin, request, queryset):
    queryset.update(status='rejected')  # assuming 'rejected' is your status value

@admin.register(SwapRequest)
class SwapRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'sender_skill', 'receiver_skill', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'sender_skill__name', 'receiver_skill__name')
    ordering = ('-created_at',)
    actions = [make_accepted, make_rejected]
