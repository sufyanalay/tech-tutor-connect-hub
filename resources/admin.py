
from django.contrib import admin
from .models import Resource, ResourceCategory

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'resource_type', 'uploaded_by', 'created_at')
    list_filter = ('resource_type', 'category', 'created_at')
    search_fields = ('title', 'description', 'uploaded_by__email')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceCategory)
