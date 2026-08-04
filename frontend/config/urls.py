"""URL configuration for Django frontend application."""

from django.contrib import admin
from django.urls import path

from research.views import (
    admin_view,
    control_run_view,
    create_run_view,
    delete_run_view,
    events_stream_proxy_view,
    forgot_password_view,
    index_view,
    knowledge_view,
    live_execution_view,
    login_view,
    logout_view,
    memory_view,
    report_detail_view,
    research_wizard_view,
    reset_password_view,
    run_status_view,
    settings_view,
    signup_view,
    verify_email_view,
    workspaces_view,
)

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', index_view, name='index'),
    path('research/new', research_wizard_view, name='research_wizard'),
    path('research/create', create_run_view, name='create_run'),
    path('research/live/<str:run_id>', live_execution_view, name='live_execution'),
    path('research/status/<str:run_id>', run_status_view, name='run_status'),
    path('research/control/<str:run_id>', control_run_view, name='control_run'),
    path('research/delete/<str:run_id>', delete_run_view, name='delete_run'),
    path('api/v1/events/stream/<str:run_id>', events_stream_proxy_view, name='events_stream_proxy'),
    path('report/<str:run_id>', report_detail_view, name='report_detail'),
    path('knowledge', knowledge_view, name='knowledge'),
    path('memory', memory_view, name='memory'),
    path('settings', settings_view, name='settings'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('signup', signup_view, name='signup'),
    path('forgot-password', forgot_password_view, name='forgot_password'),
    path('reset-password', reset_password_view, name='reset_password'),
    path('verify-email', verify_email_view, name='verify_email'),
    path('workspaces', workspaces_view, name='workspaces'),
    path('admin/system', admin_view, name='admin_system'),
]
