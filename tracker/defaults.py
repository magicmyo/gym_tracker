# Canonical default categories & exercises.
# Used by the seed migration AND the "Reset to default" action so they never drift.

DEFAULT_CATEGORIES = [
    ("Chest", "strength", [
        "Decline Chest Press", "Decline Squeeze Press", "Chest Press", "Squeeze Press",
        "Incline Chest Press", "Incline Squeeze Press", "Flat Chest Fly", "Chest Press Machine",
    ]),
    ("Shoulders", "strength", [
        "Lateral Raises", "Front Raises", "Rear Delt Fly", "Shoulder Press", "Shoulder Press Machine",
    ]),
    ("Arms", "strength", [
        "Bicep Curl", "Hammer Curl", "Concentration Curl", "Triceps Kickback", "Overhead Extension",
        "Palms-Up Wrist Curl", "Palms-Down Wrist Curl", "Preacher Curl Machine", "Seated Dip Machine",
    ]),
    ("Core & Back", "strength", [
        "Decline Sit Ups", "Decline Sit Ups 1 Leg", "Leg Raise", "Back Extension Bench",
        "Lat Pulldowns", "Seated Cable Row",
    ]),
    ("Legs", "strength", [
        "Dumbbells Lunges", "Goblet Squats", "Sumo Squats", "Calf Raise", "Leg Press Machine",
    ]),
    ("Cardio", "cardio", ["Running"]),
    ("Calisthenics", "strength", ["Pull-ups"]),
]


def seed_defaults(Category, Exercise):
    """Idempotently ensure every default category & exercise exists and is active.
    Non-destructive: never deletes; keeps custom items and all logs.
    `order` is set only on creation so a user's manual arrangement is preserved.
    Category/Exercise are passed in as parameters so this works with both real
    Django models and the historical models inside a data migration.
    """
    for cat_order, (cname, kind, exercises) in enumerate(DEFAULT_CATEGORIES):
        cat, created = Category.objects.get_or_create(
            name=cname,
            defaults={"kind": kind, "order": cat_order, "is_active": True},
        )
        if not created and not cat.is_active:
            cat.is_active = True
            cat.save()
        for ex_order, ename in enumerate(exercises):
            ex, ex_created = Exercise.objects.get_or_create(
                category=cat,
                name=ename,
                defaults={"order": ex_order, "is_active": True},
            )
            if not ex_created and not ex.is_active:
                ex.is_active = True
                ex.save()
