from django.core.management.base import BaseCommand
from tracker.models import Category, Exercise

SEED = [
    {
        "name": "Chest", "color": "#1a1a2e", "order": 1,
        "exercises": ["Bench Press", "Incline Bench Press", "Decline Press",
                      "Dumbbell Flyes", "Cable Flyes", "Push-ups"],
    },
    {
        "name": "Shoulders", "color": "#16213e", "order": 2,
        "exercises": ["Overhead Press", "Lateral Raises", "Front Raises",
                      "Face Pulls", "Arnold Press", "Upright Row"],
    },
    {
        "name": "Arms", "color": "#0f3460", "order": 3,
        "exercises": ["Barbell Curl", "Hammer Curl", "Preacher Curl",
                      "Tricep Pushdown", "Skull Crushers", "Dips"],
    },
    {
        "name": "Core & Back", "color": "#1a2a1a", "order": 4,
        "exercises": ["Deadlift", "Pull-ups", "Lat Pulldown",
                      "Seated Row", "Plank", "Crunches", "Russian Twist"],
    },
    {
        "name": "Legs", "color": "#2a1a1a", "order": 5,
        "exercises": ["Squat", "Leg Press", "Lunges",
                      "Leg Curl", "Calf Raises", "Romanian Deadlift"],
    },
    {
        "name": "Calisthenics", "color": "#1a1a2e", "order": 6,
        "exercises": ["Pull-ups", "Dips", "Push-ups",
                      "Muscle-up", "Handstand Push-up", "L-sit"],
    },
    {
        "name": "Cardio", "color": "#0d2137", "order": 7,
        "exercises": ["Running", "Cycling", "Jump Rope",
                      "HIIT", "Swimming", "Rowing Machine"],
    },
]


class Command(BaseCommand):
    help = "Seed default categories and exercises"

    def handle(self, *args, **options):
        for cat_data in SEED:
            exercises = cat_data.pop("exercises")
            cat, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults=cat_data,
            )
            for i, ex_name in enumerate(exercises):
                Exercise.objects.get_or_create(
                    category=cat,
                    name=ex_name,
                    defaults={"order": i},
                )
            self.stdout.write(f"{'Created' if created else 'Exists'}: {cat.name}")
        self.stdout.write(self.style.SUCCESS("Seed complete."))
