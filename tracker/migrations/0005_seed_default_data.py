from django.db import migrations


def forwards(apps, schema_editor):
    from tracker.defaults import seed_defaults
    Category = apps.get_model("tracker", "Category")
    Exercise = apps.get_model("tracker", "Exercise")
    seed_defaults(Category, Exercise)


def backwards(apps, schema_editor):
    # Non-destructive seed — nothing to undo.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("tracker", "0004_category_kind_workoutlog_distance_and_more"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
