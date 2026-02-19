from django.contrib import admin

# Register your models here.

from .models import Questions
admin.site.register(Questions)
# admin.ModelAdmin.readonly_fields.index.__annotations__.clear