
from django.contrib import admin
from .models import RepairRequest, RepairComment, RepairMedia

class RepairMediaInline(admin.TabularInline):
    model = RepairMedia
    extra = 0

class RepairCommentInline(admin.TabularInline):
    model = RepairComment
    extra = 0

class RepairRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'technician', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'device_type')
    search_fields = ('title', 'description', 'student__email', 'technician__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [RepairMediaInline, RepairCommentInline]

admin.site.register(RepairRequest, RepairRequestAdmin)
admin.site.register(RepairComment)
admin.site.register(RepairMedia)
