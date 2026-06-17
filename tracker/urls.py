from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("category/<int:cat_id>/", views.category_detail, name="category_detail"),
    path("log/add/", views.log_add, name="log_add"),
    path("log/<int:log_id>/update/", views.log_update, name="log_update"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("settings/", views.settings_view, name="settings"),
    path("settings/category/add/", views.category_add, name="category_add"),
    path("settings/category/<int:cat_id>/delete/", views.category_delete, name="category_delete"),
    path("settings/exercise/add/", views.exercise_add, name="exercise_add"),
    path("settings/exercise/<int:ex_id>/delete/", views.exercise_delete, name="exercise_delete"),
    path("settings/theme/", views.set_theme, name="set_theme"),
    path("settings/banner/", views.set_banner, name="set_banner"),
    path("settings/banner/remove/", views.banner_remove, name="banner_remove"),
    path("settings/quote/", views.set_quote, name="set_quote"),
    path("settings/category/<int:cat_id>/edit/", views.category_edit, name="category_edit"),
    path("settings/exercise/<int:ex_id>/edit/", views.exercise_edit, name="exercise_edit"),
    path("settings/category/reorder/", views.category_reorder, name="category_reorder"),
    path("settings/exercise/reorder/", views.exercise_reorder, name="exercise_reorder"),
    path("settings/export/", views.export_settings, name="export_settings"),
    path("settings/import/", views.import_settings, name="import_settings"),
    path("logs/export/", views.export_logs, name="export_logs"),
    path("logs/import/", views.import_logs, name="import_logs"),
    path("sw.js", views.service_worker, name="service_worker"),
    path("api/sync/", views.api_sync, name="api_sync"),
]
