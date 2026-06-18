# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A personal gym workout tracker — Django 5.2 server-rendered monolith, SQLite, PWA-capable. Single user, no auth. Accessed via Tailscale (`https://*.ts.net`), which is why `CSRF_TRUSTED_ORIGINS` lists that domain.

## Commands

```powershell
# Run the dev server
D:\Gym\.venv\Scripts\python.exe manage.py runserver

# Apply migrations
D:\Gym\.venv\Scripts\python.exe manage.py migrate

# Make new migrations after model changes
D:\Gym\.venv\Scripts\python.exe manage.py makemigrations

# Check for config issues
D:\Gym\.venv\Scripts\python.exe manage.py check

# Django shell
D:\Gym\.venv\Scripts\python.exe manage.py shell
```

## File Structure

```
D:\Gym\
├── gym_tracker/          # Django project config
│   ├── settings.py       # CSRF_TRUSTED_ORIGINS = ["https://*.ts.net"]
│   └── urls.py           # includes("tracker.urls") at root
├── tracker/              # The one app
│   ├── models.py         # Category, Exercise, WorkoutLog, UserPreference
│   ├── views.py          # All views (no class-based views)
│   ├── urls.py           # All URL routes
│   ├── forms.py          # WorkoutLogForm, CategoryForm, ExerciseForm, BannerForm
│   ├── defaults.py       # DEFAULT_CATEGORIES list + seed/reset helpers
│   └── migrations/       # 0001–0005 (0005 seeds default data)
├── templates/            # All HTML at top level (not inside app)
│   ├── base.html         # Nav, Alpine.js CDN, theme script
│   ├── home.html         # Category grid + banner/quote
│   ├── category.html     # Exercise list + log forms (branches strength/cardio)
│   ├── dashboard.html    # Analytics — Chart.js charts + recent logs table
│   └── settings.html     # All settings — 9 collapsible sections
├── static/
│   ├── css/main.css      # All styles — 11 enkodi theme tokens
│   └── js/
│       ├── app.js        # Online/offline detection, IndexedDB queue, SW registration
│       └── sw.js         # Service worker — network-first pages, cache-first static
└── media/                # Uploaded banner/category images
```

## Architecture

### Models (`tracker/models.py`)

- **`Category`** — `name`, `kind` (strength|cardio), `image`, `color`, `order`, `is_active`. Soft-deleted via `is_active=False`. `Meta.ordering = ["order", "name"]`.
- **`Exercise`** — FK to Category, `name`, `order`, `is_active`. Soft-deleted. `Meta.ordering = ["order", "name"]`.
- **`WorkoutLog`** — FK to Exercise, `date`, `weight`/`weight_unit` (kg/lb/bodyweight), `reps`, `sets`, `distance`/`distance_unit` (km/mi), `duration` (minutes), `notes`. Strength logs use weight/reps/sets; cardio logs use distance/distance_unit/duration.
- **`UserPreference`** — singleton (pk always forced to 1). `theme`, `banner` (ImageField), `quote`. Access via `UserPreference.get()` classmethod. Never query directly.

### Cardio vs Strength

A category's `kind` field controls the entire UI branch:
- **Strength**: log Weight + Unit + Reps + Sets. Header shows `ExerciseName - weight unit`. Auto-defaults: last logged values or 5kg/8reps/4sets.
- **Cardio**: log Distance + Unit (km/mi) + Minutes. Header shows distance. Auto-computes speed (km/hr or mile/hr). Both `category.html` and `dashboard.html` branch on `log.exercise.category.kind == "cardio"`.

### Theming

11 enkodi themes via `data-theme` on `<html id="html-root">`. CSS custom properties: `--text-primary`, `--text-secondary`, `--text-muted`, `--accent`, `--card-bg`, `--surface-border`, `--card-radius`. Default theme: `cyber`.

**Critical timing**: the theme-applying inline `<script>` is in `base.html` near `</body>`, **after** `{% block content %}`. Any JS that reads CSS vars (e.g. Chart.js axis colours) must run inside `window.addEventListener('load', ...)` so the theme is applied first.

Theme is stored in both `localStorage` (applied instantly on load) and `UserPreference.theme` (persisted to DB via `set_theme` view).

### PWA / Service Worker

- SW registered at `/sw.js` (served by `service_worker` view with `Service-Worker-Allowed: /` header) with `{ scope: '/' }` so it covers the entire app.
- **Do not** serve it from `/static/js/sw.js` — that would give it scope `/static/js/` and break offline navigation.
- SW strategy: network-first for HTML pages, cache-first for `/static/` assets, skips non-GET and `/admin/`.
- `app.js` has an IndexedDB offline log queue (`pending_logs` store) with `syncPendingLogs()` → `POST /api/sync/`.

### Settings Page

`templates/settings.html` has 9 collapsible sections using Alpine.js `x-data="{ open: false }"` with `@click="open = !open"` on `<h2>`. After any save action, the view redirects with `?saved=<key>` and the relevant section auto-opens (`x-data="{ open: {% if saved == 'key' %}true{% else %}false{% endif %} }"`).

Settings sections: Theme, Banner Cover, Motivation Quote, Data/Backup, Add Category, Categories (drag-reorder), Add Exercise, Exercises (drag-reorder grouped by category), Reset/Danger Zone.

### Drag-to-Reorder (SortableJS 1.15.2)

- Categories: `#category-sortable` → POST `category_reorder` with `{ order: [ids] }`.
- Exercises: multiple `.exercise-sortable` divs (one per category group) → POST `exercise_reorder`.
- **Critical**: exercises queryset in `settings_view` must be ordered `category__order, category__name, order, name` so `{% regroup exercises by category %}` produces one consecutive group per category. Using the model default ordering (`order, name`) interleaves exercises across categories and breaks grouping.

### CSV Export / Import

- **Export Settings** (`GET /settings/export/`): downloads `gymtracker_settings.csv` with `record_type` column — one `preference` row (theme, quote), one `category` row per Category, one `exercise` row per Exercise.
- **Import Settings** (`POST /settings/import/`): upserts categories/exercises, restores theme+quote. Decoded with `utf-8-sig` (strips Excel BOM).
- **Export Logs** (`GET /logs/export/`): downloads `gymtracker_logs.csv` — all `WorkoutLog` rows ordered by date.
- **Import Logs** (`POST /logs/import/`): auto-creates missing categories/exercises by name, then creates logs. Tolerates blank/invalid rows.

### Default Data (`tracker/defaults.py`)

`DEFAULT_CATEGORIES` is the single source of truth for the 7 default categories and their exercises (Chest → 8 exercises, Shoulders → 5, Arms → 9, Core & Back → 6, Legs → 5, Cardio → 1, Calisthenics → 1).

Two functions:
- `seed_defaults(Category, Exercise)` — idempotent, additive. Used by migration 0005 on fresh installs. Never deletes.
- `reset_to_defaults(Category, Exercise, WorkoutLog)` — destructive factory reset. Deletes all logs + categories + exercises, then recreates exactly the defaults in order. Theme/quote/banner untouched.

### Danger Zone (Settings)

- **Reset to Default Settings** → calls `reset_to_defaults()`. Wipes everything (logs, categories, exercises) and recreates only the 7 defaults in canonical order.
- **Clear All Logs** → `WorkoutLog.objects.all().delete()`. Categories/exercises untouched.
- **Hide/Unhide category** → toggles `is_active`. Hidden categories show "(hidden)" + Unhide button in Settings.
- **Remove/Restore exercise** → same soft-delete pattern.

## Key Design Decisions

- **No class-based views** — every view is a plain function in `tracker/views.py`.
- **No Django forms for rendering** — templates hand-craft all `<input>` elements; `WorkoutLogForm` is only used for validation/save.
- **`settings_view` passes `saved = request.GET.get("saved", "")` to the template** so save actions can auto-open the relevant section and show a "✓ Saved" banner.
- **`category_detail` view** computes `is_cardio = cat.kind == "cardio"` and passes it to `category.html` as a single flag — templates branch on it for both the log UI and the display headers.
- **Speed is computed in the view** (not the template): `speed = round(float(distance) / (duration / 60.0), 1)` for cardio logs.
- **`{% regroup %}` requires consecutive ordering** — always supply `order_by("category__order", "category__name", "order", "name")` when querying exercises for the Settings exercises list.
- **Analytics chart colours** must be read inside `window.addEventListener('load', ...)` because the theme script in `base.html` runs after `{% block content %}`.

## Migrations History

| # | What |
|---|------|
| 0001 | Initial schema (Category, Exercise, WorkoutLog, UserPreference) |
| 0002 | Add `UserPreference.banner` (ImageField) |
| 0003 | Add `UserPreference.quote` |
| 0004 | Add `Category.kind`, `WorkoutLog.distance`, `distance_unit`, `duration` |
| 0005 | Data migration — seeds DEFAULT_CATEGORIES via `seed_defaults()` |

After any model change: `makemigrations` then `migrate`. Always run `manage.py check` before committing.
