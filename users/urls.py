from django.urls import path, include
from . import views
# from .views import SkillViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import SimpleRouter, DefaultRouter

router = SimpleRouter() #for modelviewset
router.register(r'message', views.MessageViewSet, basename='message')

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('skills/', views.SkillsListCreateAPIView.as_view(), name='skills_list_craeate'),
    path('skills/<int:pk>/',views.SkillsDetailAPIView.as_view(), name='skill_detail'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.ProfileView.as_view(), name='profile'),
    path('swap-request/', views.SwapRequestAPIView.as_view(), name='swap_request'),
    path('my-swaps/', views.MySwapRequestView.as_view(), name='my-swaps'),
    path('my-swaps/<str:pk>/', views.RespondToSwapRequestView.as_view(), name='respond-swap'),
    path('notifications/', views.UserNotificationListView.as_view(), name='user-notifications'),
    path('notifications/<str:pk>/',views.MarkNotificationReadView.as_view(), name='mark-notification-read'),
    path('my-swaps/<str:pk>/counter/', views.CounterOfferView.as_view(), name='counter-offer'),
    path('my-swaps/<str:pk>/counter/respond/', views.RespondToCounterOfferView.as_view(), name='counter-offer-response'),
    path('ratings/', views.RatingCreateView.as_view(), name='rating-create'),
    path('', include(router.urls)),
]