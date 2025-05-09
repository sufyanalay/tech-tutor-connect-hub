
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, Rating

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'phone_number', 'expertise', 'hourly_rate', 'total_earnings']
        read_only_fields = ['total_earnings']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'profile', 'date_joined']
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        
        if profile_data:
            Profile.objects.create(user=user, **profile_data)
        else:
            Profile.objects.create(user=user)
        
        return user
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        
        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        
        # Update Profile fields
        if profile_data and hasattr(instance, 'profile'):
            for attr, value in profile_data.items():
                setattr(instance.profile, attr, value)
            instance.profile.save()
        
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'role', 'password', 'password2']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        return user


class RatingSerializer(serializers.ModelSerializer):
    rated_by_name = serializers.ReadOnlyField(source='rated_by.full_name')
    user_name = serializers.ReadOnlyField(source='user.full_name')
    
    class Meta:
        model = Rating
        fields = ['id', 'user', 'user_name', 'rated_by', 'rated_by_name', 'rating', 'review', 'created_at']
        read_only_fields = ['rated_by', 'created_at']
    
    def validate(self, attrs):
        # Prevent users from rating themselves
        if self.context['request'].user == attrs['user']:
            raise serializers.ValidationError({"user": "You cannot rate yourself."})
        return attrs
    
    def create(self, validated_data):
        validated_data['rated_by'] = self.context['request'].user
        return super().create(validated_data)


class UserDashboardSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    average_rating = serializers.SerializerMethodField()
    completed_repairs = serializers.SerializerMethodField()
    completed_academic_sessions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'profile', 'average_rating', 
                 'completed_repairs', 'completed_academic_sessions']
    
    def get_average_rating(self, obj):
        ratings = obj.received_ratings.all()
        if not ratings:
            return None
        return sum(r.rating for r in ratings) / len(ratings)
    
    def get_completed_repairs(self, obj):
        from repairs.models import RepairRequest
        if obj.role == 'technician':
            return RepairRequest.objects.filter(technician=obj, status='completed').count()
        return 0
    
    def get_completed_academic_sessions(self, obj):
        from academics.models import AcademicQuestion
        if obj.role == 'teacher':
            return AcademicQuestion.objects.filter(teacher=obj, status='answered').count()
        return 0
