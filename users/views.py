
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import Profile, Rating
from .serializers import UserSerializer, UserRegistrationSerializer, ProfileSerializer, RatingSerializer, UserDashboardSerializer
from .permissions import IsOwnerOrReadOnly, IsAdminUser, IsSameUserOrReadOnly

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameUserOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'dashboard':
            return UserDashboardSerializer
        return UserSerializer
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.query_params.get('received'):
            return Rating.objects.filter(user=self.request.user)
        elif self.request.query_params.get('given'):
            return Rating.objects.filter(rated_by=self.request.user)
        elif self.request.query_params.get('user'):
            user_id = self.request.query_params.get('user')
            return Rating.objects.filter(user__id=user_id)
        
        # Admin or default case
        if self.request.user.is_staff:
            return Rating.objects.all()
        return Rating.objects.filter(user=self.request.user) | Rating.objects.filter(rated_by=self.request.user)
