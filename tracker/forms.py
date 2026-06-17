from django import forms
from .models import WorkoutLog, Category, Exercise, UserPreference


class WorkoutLogForm(forms.ModelForm):
    class Meta:
        model = WorkoutLog
        fields = ["exercise", "date", "weight", "weight_unit", "reps", "sets", "distance", "distance_unit", "duration", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "kind", "image", "color"]
        widgets = {
            "color": forms.TextInput(attrs={"type": "color"}),
        }


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["category", "name"]


class BannerForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ["banner"]
