
from rest_framework import serializers
from .models import RepairRequest, RepairMedia, RepairComment


class RepairMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairMedia
        fields = ['id', 'repair_request', 'file', 'file_type', 'uploaded_at']
        read_only_fields = ['uploaded_at']
    
    def validate_file(self, value):
        # File size validation (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        return value


class RepairCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.full_name')
    user_role = serializers.ReadOnlyField(source='user.role')
    
    class Meta:
        model = RepairComment
        fields = ['id', 'repair_request', 'user', 'user_name', 'user_role', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RepairRequestSerializer(serializers.ModelSerializer):
    media = RepairMediaSerializer(many=True, read_only=True)
    comments = RepairCommentSerializer(many=True, read_only=True)
    student_name = serializers.ReadOnlyField(source='student.full_name')
    technician_name = serializers.ReadOnlyField(source='technician.full_name')
    
    class Meta:
        model = RepairRequest
        fields = [
            'id', 'title', 'description', 'student', 'student_name', 'technician', 
            'technician_name', 'device_type', 'device_model', 'status', 
            'estimated_cost', 'final_cost', 'created_at', 'updated_at',
            'media', 'comments'
        ]
        read_only_fields = ['student', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)
