
from rest_framework import serializers
from .models import AcademicQuestion, AcademicQuestionMedia, AcademicAnswer


class AcademicQuestionMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicQuestionMedia
        fields = ['id', 'question', 'file', 'file_type', 'uploaded_at']
        read_only_fields = ['uploaded_at']
    
    def validate_file(self, value):
        # File size validation (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        return value


class AcademicAnswerSerializer(serializers.ModelSerializer):
    teacher_name = serializers.ReadOnlyField(source='teacher.full_name')
    
    class Meta:
        model = AcademicAnswer
        fields = ['id', 'question', 'teacher', 'teacher_name', 'answer_text', 
                 'attachment', 'created_at', 'is_accepted']
        read_only_fields = ['teacher', 'created_at', 'is_accepted']
    
    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class AcademicQuestionSerializer(serializers.ModelSerializer):
    media = AcademicQuestionMediaSerializer(many=True, read_only=True)
    answers = AcademicAnswerSerializer(many=True, read_only=True)
    student_name = serializers.ReadOnlyField(source='student.full_name')
    teacher_name = serializers.ReadOnlyField(source='teacher.full_name')
    
    class Meta:
        model = AcademicQuestion
        fields = [
            'id', 'title', 'description', 'student', 'student_name', 'teacher', 
            'teacher_name', 'subject', 'status', 'session_fee', 'created_at', 
            'updated_at', 'media', 'answers'
        ]
        read_only_fields = ['student', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)
