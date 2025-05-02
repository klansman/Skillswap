from django.urls import path, include
from . import views
# from .views import SkillViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import SimpleRouter

# router = SimpleRouter() #for modelviewset
# router.register(r'skills', views.SkillViewSet, basename='skills')

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('skills/', views.SkillsListCreateAPIView.as_view(), name='skills_list_craeate'),
    path('skills/<int:pk>/',views.SkillsDetailAPIView.as_view(), name='skill_detail'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.ProfileView.as_view(), name='profile'),
    path('swap-request/', views.SwapRequestAPIView.as_view(), name='swap_request'),
    path('my-swaps/', views.MySwapRequestView.as_view(), name='my-swaps'),
    path('respond-swap/<str:pk>/', views.RespondToSwapRequestView.as_view(), name='respond-swap'),
    path('notifications/', views.UserNotificationListView.as_view(), name='user-notifications'),
    # path('', include(router.urls)),
]