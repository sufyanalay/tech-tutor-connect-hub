
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AcademicQuestionViewSet, AcademicQuestionMediaViewSet, AcademicAnswerViewSet

router = DefaultRouter()
router.register('questions', AcademicQuestionViewSet, basename='academic-question')
router.register('media', AcademicQuestionMediaViewSet, basename='academic-media')
router.register('answers', AcademicAnswerViewSet, basename='academic-answer')

urlpatterns = [
    path('', include(router.urls)),
]
