import csv
import io
import json
import os
from datetime import date as today_date
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum
from django.db.models.functions import TruncWeek
from datetime import timedelta
from django.conf import settings as django_settings

from .models import Category, Exercise, WorkoutLog, UserPreference
from .forms import WorkoutLogForm, CategoryForm, ExerciseForm, BannerForm


# ── Home ──────────────────────────────────────────────────────────────────────

def home(request):
    categories = Category.objects.filter(is_active=True)
    pref = UserPreference.get()
    return render(request, "home.html", {
        "categories": categories,
        "pref": pref,
        "theme": pref.theme,
    })


# ── Category detail ───────────────────────────────────────────────────────────

def category_detail(request, cat_id):
    cat = get_object_or_404(Category, pk=cat_id, is_active=True)
    exercises = cat.exercises.filter(is_active=True)
    today = today_date.today()
    pref = UserPreference.get()
    is_cardio = cat.kind == "cardio"

    ex_data = []
    for ex in exercises:
        latest = ex.logs.filter(date=today).first() or ex.logs.first()
        speed = None
        if is_cardio and latest and latest.distance and latest.duration:
            try:
                speed = round(float(latest.distance) / (latest.duration / 60.0), 1)
            except ZeroDivisionError:
                speed = None
        ex_data.append({"exercise": ex, "latest": latest, "speed": speed})

    return render(request, "category.html", {
        "cat": cat,
        "ex_data": ex_data,
        "is_cardio": is_cardio,
        "today": today.isoformat(),
        "theme": pref.theme,
    })


# ── Workout log add / update ──────────────────────────────────────────────────

@require_POST
def log_add(request):
    form = WorkoutLogForm(request.POST)
    if form.is_valid():
        form.save()
        ex = form.instance.exercise
        return redirect("category_detail", cat_id=ex.category.id)
    return redirect("home")


@require_POST
def log_update(request, log_id):
    log = get_object_or_404(WorkoutLog, pk=log_id)
    form = WorkoutLogForm(request.POST, instance=log)
    if form.is_valid():
        form.save()
    return redirect("category_detail", cat_id=log.exercise.category.id)


# ── Dashboard ─────────────────────────────────────────────────────────────────

def dashboard(request):
    pref = UserPreference.get()

    total_logs = WorkoutLog.objects.count()
    total_sets = WorkoutLog.objects.aggregate(s=Sum("sets"))["s"] or 0
    active_days = WorkoutLog.objects.values("date").distinct().count()

    eight_weeks_ago = today_date.today() - timedelta(weeks=8)
    weekly = (
        WorkoutLog.objects
        .filter(date__gte=eight_weeks_ago)
        .annotate(week=TruncWeek("date"))
        .values("week")
        .annotate(count=Count("id"))
        .order_by("week")
    )
    weekly_labels = [str(w["week"])[:10] for w in weekly]
    weekly_data = [w["count"] for w in weekly]

    top_ex = (
        Exercise.objects
        .annotate(log_count=Count("logs"))
        .filter(log_count__gt=0)
        .order_by("-log_count")
        .first()
    )
    progress_labels, progress_data, progress_name = [], [], ""
    if top_ex:
        progress_name = top_ex.name
        logs = top_ex.logs.filter(weight__isnull=False).order_by("date")[:20]
        progress_labels = [str(l.date) for l in logs]
        progress_data = [float(l.weight) for l in logs]

    recent = WorkoutLog.objects.select_related("exercise__category").order_by("-date", "-created_at")[:10]

    return render(request, "dashboard.html", {
        "total_logs": total_logs,
        "total_sets": total_sets,
        "active_days": active_days,
        "weekly_labels": json.dumps(weekly_labels),
        "weekly_data": json.dumps(weekly_data),
        "progress_name": progress_name,
        "progress_labels": json.dumps(progress_labels),
        "progress_data": json.dumps(progress_data),
        "recent": recent,
        "theme": pref.theme,
    })


# ── Settings ──────────────────────────────────────────────────────────────────

def settings_view(request):
    pref = UserPreference.get()
    categories = Category.objects.all()
    exercises = Exercise.objects.select_related("category").all()
    return render(request, "settings.html", {
        "pref": pref,
        "categories": categories,
        "exercises": exercises,
        "theme": pref.theme,
        "theme_choices": UserPreference._meta.get_field("theme").choices,
        "saved": request.GET.get("saved", ""),
    })


@require_POST
def category_add(request):
    form = CategoryForm(request.POST, request.FILES)
    if form.is_valid():
        cat = form.save(commit=False)
        cat.order = Category.objects.count()
        cat.save()
    return redirect("settings")


@require_POST
def category_delete(request, cat_id):
    cat = get_object_or_404(Category, pk=cat_id)
    cat.is_active = False
    cat.save()
    return redirect("settings")


@require_POST
def exercise_add(request):
    form = ExerciseForm(request.POST)
    if form.is_valid():
        ex = form.save(commit=False)
        ex.order = Exercise.objects.filter(category=ex.category).count()
        ex.save()
    return redirect("settings")


@require_POST
def exercise_delete(request, ex_id):
    ex = get_object_or_404(Exercise, pk=ex_id)
    ex.is_active = False
    ex.save()
    return redirect("settings")


@require_POST
def set_theme(request):
    theme = request.POST.get("theme", "cyber")
    valid_keys = [k for k, _ in UserPreference._meta.get_field("theme").choices]
    if theme in valid_keys:
        pref = UserPreference.get()
        pref.theme = theme
        pref.save()
    return redirect("settings")


@require_POST
def set_banner(request):
    pref = UserPreference.get()
    form = BannerForm(request.POST, request.FILES, instance=pref)
    if form.is_valid():
        form.save()
    return redirect("settings")


@require_POST
def banner_remove(request):
    pref = UserPreference.get()
    if pref.banner:
        pref.banner.delete(save=False)
    pref.banner = None
    pref.save()
    return redirect("settings")


@require_POST
def set_quote(request):
    pref = UserPreference.get()
    pref.quote = request.POST.get("quote", "").strip()[:255]
    pref.save()
    return redirect("/settings/?saved=quote")


@require_POST
def category_edit(request, cat_id):
    cat = get_object_or_404(Category, pk=cat_id)
    form = CategoryForm(request.POST, request.FILES, instance=cat)
    if form.is_valid():
        form.save()
    return redirect("settings")


@require_POST
def exercise_edit(request, ex_id):
    ex = get_object_or_404(Exercise, pk=ex_id)
    form = ExerciseForm(request.POST, instance=ex)
    if form.is_valid():
        form.save()
    return redirect("settings")


@require_POST
def category_reorder(request):
    try:
        ids = json.loads(request.body).get("order", [])
    except (ValueError, TypeError):
        return JsonResponse({"error": "bad request"}, status=400)
    for index, cid in enumerate(ids):
        Category.objects.filter(pk=cid).update(order=index)
    return JsonResponse({"ok": True})


@require_POST
def exercise_reorder(request):
    try:
        ids = json.loads(request.body).get("order", [])
    except (ValueError, TypeError):
        return JsonResponse({"error": "bad request"}, status=400)
    for index, eid in enumerate(ids):
        Exercise.objects.filter(pk=eid).update(order=index)
    return JsonResponse({"ok": True})


# ── Offline sync API ──────────────────────────────────────────────────────────

@csrf_exempt
def api_sync(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            logs = data.get("logs", [])
            created = 0
            for entry in logs:
                ex = Exercise.objects.filter(pk=entry.get("exercise")).first()
                if ex:
                    WorkoutLog.objects.create(
                        exercise=ex,
                        date=entry.get("date"),
                        weight=entry.get("weight") or None,
                        weight_unit=entry.get("weight_unit", "kg"),
                        reps=entry.get("reps") or None,
                        sets=entry.get("sets") or None,
                        distance=entry.get("distance") or None,
                        distance_unit=entry.get("distance_unit", "km"),
                        duration=entry.get("duration") or None,
                    )
                    created += 1
            return JsonResponse({"synced": created})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "POST only"}, status=405)


# ── Service worker (served from root so scope covers entire app) ──────────────

def service_worker(request):
    sw_path = os.path.join(django_settings.BASE_DIR, 'static', 'js', 'sw.js')
    with open(sw_path, 'rb') as f:
        content = f.read()
    response = HttpResponse(content, content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    return response


# ── CSV export / import ───────────────────────────────────────────────────────

def export_settings(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="gymtracker_settings.csv"'
    writer = csv.writer(response)
    writer.writerow(["record_type", "name", "kind", "color", "order", "category", "theme", "quote"])
    pref = UserPreference.get()
    writer.writerow(["preference", "", "", "", "", "", pref.theme, pref.quote])
    for cat in Category.objects.all():
        writer.writerow(["category", cat.name, cat.kind, cat.color, cat.order, "", "", ""])
    for ex in Exercise.objects.select_related("category").all():
        writer.writerow(["exercise", ex.name, "", "", ex.order, ex.category.name, "", ""])
    return response


@require_POST
def import_settings(request):
    f = request.FILES.get("file")
    if not f:
        return redirect("settings")
    text = f.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    cats, exs, pref_row = [], [], None
    for row in reader:
        rt = (row.get("record_type") or "").strip()
        if rt == "category":
            cats.append(row)
        elif rt == "exercise":
            exs.append(row)
        elif rt == "preference":
            pref_row = row

    for row in cats:
        name = (row.get("name") or "").strip()
        if not name:
            continue
        cat, _ = Category.objects.get_or_create(name=name)
        cat.kind = (row.get("kind") or "strength").strip() or "strength"
        if (row.get("color") or "").strip():
            cat.color = row["color"].strip()
        try:
            cat.order = int(row.get("order") or 0)
        except (TypeError, ValueError):
            pass
        cat.is_active = True
        cat.save()

    for row in exs:
        name = (row.get("name") or "").strip()
        cat_name = (row.get("category") or "").strip()
        if not name or not cat_name:
            continue
        cat, _ = Category.objects.get_or_create(name=cat_name)
        ex, _ = Exercise.objects.get_or_create(category=cat, name=name)
        try:
            ex.order = int(row.get("order") or 0)
        except (TypeError, ValueError):
            pass
        ex.is_active = True
        ex.save()

    if pref_row:
        pref = UserPreference.get()
        theme = (pref_row.get("theme") or "").strip()
        valid = [k for k, _ in UserPreference._meta.get_field("theme").choices]
        if theme in valid:
            pref.theme = theme
        pref.quote = (pref_row.get("quote") or "").strip()[:255]
        pref.save()

    return redirect("settings")


def export_logs(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="gymtracker_logs.csv"'
    writer = csv.writer(response)
    writer.writerow(["date", "category", "exercise", "weight", "weight_unit",
                     "reps", "sets", "distance", "distance_unit", "duration", "notes"])
    logs = WorkoutLog.objects.select_related("exercise__category").order_by("date", "id")
    for log in logs:
        writer.writerow([
            log.date.isoformat(),
            log.exercise.category.name,
            log.exercise.name,
            log.weight if log.weight is not None else "",
            log.weight_unit,
            log.reps if log.reps is not None else "",
            log.sets if log.sets is not None else "",
            log.distance if log.distance is not None else "",
            log.distance_unit,
            log.duration if log.duration is not None else "",
            log.notes or "",
        ])
    return response


@require_POST
def import_logs(request):
    f = request.FILES.get("file")
    if not f:
        return redirect("settings")
    text = f.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    def num(v):
        v = (v or "").strip()
        return v or None

    def unit(v, default):
        return default if v is None else v.strip()

    for row in reader:
        ex_name = (row.get("exercise") or "").strip()
        date_str = (row.get("date") or "").strip()
        if not ex_name or not date_str:
            continue
        cat_name = (row.get("category") or "").strip() or "Imported"
        try:
            log_date = today_date.fromisoformat(date_str)
        except ValueError:
            continue
        cat, _ = Category.objects.get_or_create(name=cat_name)
        ex, _ = Exercise.objects.get_or_create(category=cat, name=ex_name)
        try:
            WorkoutLog.objects.create(
                exercise=ex,
                date=log_date,
                weight=num(row.get("weight")),
                weight_unit=unit(row.get("weight_unit"), "kg"),
                reps=num(row.get("reps")),
                sets=num(row.get("sets")),
                distance=num(row.get("distance")),
                distance_unit=unit(row.get("distance_unit"), "km"),
                duration=num(row.get("duration")),
                notes=(row.get("notes") or "").strip(),
            )
        except Exception:
            continue

    return redirect("settings")
