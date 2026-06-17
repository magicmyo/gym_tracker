from django.db import models

WEIGHT_UNIT_CHOICES = [
    ("kg", "kg"),
    ("lb", "lb"),
    ("", "bodyweight"),
]

THEME_CHOICES = [
    ("glass",  "Glassmorphism"),
    ("neo",    "Neomorphism"),
    ("brut",   "Brutalism"),
    ("flat",   "Flat / Material"),
    ("cyber",  "Cyberpunk"),
    ("clay",   "Claymorphism"),
    ("retro",  "Retro / Y2K"),
    ("swiss",  "Swiss / International"),
    ("aurora", "Aurora"),
    ("skeu",   "Skeuomorphism"),
    ("bento",  "Bento Grid"),
]


class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    color = models.CharField(max_length=20, default="#1a1a2e")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Exercise(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="exercises")
    name = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.category.name} — {self.name}"


class WorkoutLog(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="logs")
    date = models.DateField()
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    weight_unit = models.CharField(max_length=2, choices=WEIGHT_UNIT_CHOICES, default="kg", blank=True)
    reps = models.PositiveIntegerField(blank=True, null=True)
    sets = models.PositiveIntegerField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.exercise.name} on {self.date}"


class UserPreference(models.Model):
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default="cyber")
    banner = models.ImageField(upload_to="banner/", blank=True, null=True)

    class Meta:
        verbose_name = "User Preference"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
