
from rest_framework import serializers
from .models import Resource, ResourceCategory


class ResourceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceCategory
        fields = ['id', 'name', 'description']


class ResourceSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    uploaded_by_name = serializers.ReadOnlyField(source='uploaded_by.full_name')
    
    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'description', 'file', 'thumbnail', 'resource_type',
            'category', 'category_name', 'uploaded_by', 'uploaded_by_name',
            'created_at', 'updated_at', 'view_count', 'is_featured'
        ]
        read_only_fields = ['uploaded_by', 'created_at', 'updated_at', 'view_count']
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_file(self, value):
        # File size validation (100MB limit for videos, 20MB for others)
        max_size = 20 * 1024 * 1024  # 20MB default
        
        resource_type = self.initial_data.get('resource_type')
        if resource_type == 'video':
            max_size = 100 * 1024 * 1024  # 100MB for videos
        
        if value.size > max_size:
            if resource_type == 'video':
                raise serializers.ValidationError("Video size cannot exceed 100MB")
            else:
                raise serializers.ValidationError("File size cannot exceed 20MB")
        
        return value
