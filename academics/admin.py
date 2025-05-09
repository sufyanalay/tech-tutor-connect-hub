
from django.contrib import admin
from .models import AcademicQuestion, AcademicQuestionMedia, AcademicAnswer

class AcademicMediaInline(admin.TabularInline):
    model = AcademicQuestionMedia
    extra = 0

class AcademicAnswerInline(admin.TabularInline):
    model = AcademicAnswer
    extra = 0

class AcademicQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'teacher', 'subject', 'status', 'created_at')
    list_filter = ('status', 'subject', 'created_at')
    search_fields = ('title', 'description', 'student__email', 'teacher__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [AcademicMediaInline, AcademicAnswerInline]

admin.site.register(AcademicQuestion, AcademicQuestionAdmin)
admin.site.register(AcademicQuestionMedia)
admin.site.register(AcademicAnswer)
