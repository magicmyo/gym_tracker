from django.contrib import admin
from .models import Category, Exercise, WorkoutLog, UserPreference

admin.site.register(Category)
admin.site.register(Exercise)
admin.site.register(WorkoutLog)
admin.site.register(UserPreference)
