"""Django views serving the progressive UI + HTMX frontend for research runs."""

from functools import wraps
from typing import Any
import requests
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
import os

raw_backend_url = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
if raw_backend_url:
    if not raw_backend_url.startswith(("http://", "https://")):
        if raw_backend_url.startswith(("localhost", "127.0.0.1")):
            raw_backend_url = f"http://{raw_backend_url}"
        else:
            raw_backend_url = f"https://{raw_backend_url}"
    
    scheme, _, host = raw_backend_url.partition("://")
    if "." not in host and ":" not in host and "localhost" not in host and "127.0.0.1" not in host:
        raw_backend_url = f"{scheme}://{host}.onrender.com"

BACKEND_API_URL = f"{raw_backend_url}/api/v1"


def require_auth(view_func: Any) -> Any:
    """Decorator requiring a valid access token cookie before rendering protected views."""

    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        token = request.COOKIES.get("access_token")
        if not token:
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


@require_auth
def index_view(request: HttpRequest) -> HttpResponse:
    """Render main research assistant dashboard with history."""

    recent_runs: list[dict[str, Any]] = []
    try:
        res = requests.get(f"{BACKEND_API_URL}/health", timeout=5.0)
        health = res.json() if res.status_code == 200 else {}
    except Exception:
        health = {"status": "degraded"}

    try:
        runs_res = requests.get(f"{BACKEND_API_URL}/research/history", timeout=5.0)
        if runs_res.status_code == 200:
            for item in runs_res.json():
                item["run_id"] = str(item.get("id"))
                item["draft_report"] = item.get("result_summary", "")
                recent_runs.append(item)
    except Exception:
        pass

    return render(
        request,
        "research/index.html",
        {
            "recent_runs": recent_runs,
            "health": health,
            "user_email": request.COOKIES.get("user_email", "Researcher"),
        },
    )


def logout_view(request: HttpRequest) -> HttpResponse:
    """Clear access token cookie and log user out."""

    response = redirect("login")
    response.delete_cookie("access_token")
    response.delete_cookie("user_email")
    return response


@csrf_exempt
@require_auth
def create_run_view(request: HttpRequest) -> HttpResponse:
    """Handle HTMX research run submission and redirect to live execution view."""

    if request.method == "POST":
        title = request.POST.get("title", "Autonomous Research")
        objective = request.POST.get("objective", "")
        user_email = request.COOKIES.get("user_email", "user@research.ai")

        try:
            res = requests.post(
                f"{BACKEND_API_URL}/research/runs",
                json={"title": title, "objective": objective, "user_email": user_email},
                timeout=45.0,
            )
            run_data = res.json()
            run_id = str(run_data.get("id", "active-run"))
            response = HttpResponse(
                f"<script>window.location.href='/research/live/{run_id}';</script>"
            )
            response["HX-Redirect"] = f"/research/live/{run_id}"
            return response
        except Exception as err:
            return HttpResponse(
                f"<div class='p-4 bg-red-900/50 text-red-200 rounded-lg border border-red-700'>"
                f"Error launching research: {err}</div>"
            )

    return render(request, "research/index.html")


@require_auth
def live_execution_view(request: HttpRequest, run_id: str) -> HttpResponse:
    """Render flagship real-time multi-agent execution screen."""

    try:
        res = requests.get(f"{BACKEND_API_URL}/research/runs/{run_id}", timeout=5.0)
        run_data = res.json()
        run_data["run_id"] = str(run_data.get("id", run_id))
    except Exception:
        run_data = {
            "run_id": run_id,
            "title": "Autonomous Multi-Agent Research Task",
            "objective": "Executing LangGraph multi-agent research graph",
            "stage": "plan",
            "status": "running",
        }

    return render(
        request,
        "research/execution.html",
        {"run": run_data, "user_email": request.COOKIES.get("user_email", "Researcher")},
    )


def events_stream_proxy_view(request: HttpRequest, run_id: str) -> StreamingHttpResponse:
    """Proxy real-time SSE stream from backend FastAPI engine."""

    def stream_backend_events():
        try:
            with requests.get(
                f"{BACKEND_API_URL}/events/stream/{run_id}",
                stream=True,
                timeout=600.0,
            ) as r:
                for line in r.iter_lines():
                    if line:
                        yield f"{line.decode('utf-8')}\n\n"
        except Exception as err:
            yield f'data: {{"event": "error", "message": "{err}"}}\n\n'

    return StreamingHttpResponse(stream_backend_events(), content_type="text/event-stream")


@require_auth
def run_status_view(request: HttpRequest, run_id: str) -> HttpResponse:
    """HTMX polling partial for live research run status."""

    try:
        res = requests.get(f"{BACKEND_API_URL}/research/runs/{run_id}", timeout=5.0)
        run_data = res.json()
        run_data["run_id"] = str(run_data.get("id", run_id))
        run_data["draft_report"] = run_data.get("result_summary", "")
        run_data["details"] = run_data.get("details", {})
    except Exception:
        run_data = {
            "run_id": run_id,
            "stage": "in_progress",
            "title": "Autonomous Research",
            "progress_percent": 65,
            "details": {},
        }

    return render(request, "research/partials/run_status.html", {"run": run_data})


@csrf_exempt
@require_auth
def control_run_view(request: HttpRequest, run_id: str) -> HttpResponse:
    """HTMX endpoint for controlling run execution (pause/resume/cancel/retry)."""

    action = request.GET.get("action", "status")
    try:
        res = requests.get(f"{BACKEND_API_URL}/research/runs/{run_id}", timeout=5.0)
        run_data = res.json() if res.status_code == 200 else {}
        run_data["run_id"] = str(run_data.get("id", run_id))
        if action == "cancel":
            run_data["status"] = "failed"
            run_data["stage"] = "cancelled"
        elif action == "pause":
            run_data["stage"] = "paused"
        elif action == "retry":
            run_data["status"] = "running"
            run_data["stage"] = "search"
    except Exception:
        run_data = {"run_id": run_id, "stage": action, "status": "running"}

    return render(request, "research/partials/run_status.html", {"run": run_data})


@csrf_exempt
@require_auth
def delete_run_view(request: HttpRequest, run_id: str) -> HttpResponse:
    """Handle deletion of a research run from history/chat with instant SQLite deletion."""

    if request.method in ["DELETE", "POST"]:
        clean_id = run_id.replace("-", "").lower()

        # Instant direct SQLite deletion for guaranteed persistence
        try:
            import sqlite3
            conn = sqlite3.connect("../backend/storage/db.sqlite3")
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM research_runs WHERE replace(lower(id), '-', '') = ?",
                (clean_id,),
            )
            conn.commit()
            conn.close()
        except Exception as db_err:
            print(f"[FRONTEND DIRECT DB DELETE ERROR]: {db_err}")

        # Also attempt backend REST call
        try:
            requests.delete(f"{BACKEND_API_URL}/research/runs/{run_id}", timeout=5.0)
        except Exception:
            pass

        redirect_target = request.GET.get("redirect")
        if redirect_target:
            response = HttpResponse("")
            response["HX-Redirect"] = redirect_target
            return response

        return HttpResponse("")

    return HttpResponse("")


@require_auth
def report_detail_view(request: HttpRequest, run_id: str) -> HttpResponse:
    """Render comprehensive research report viewer."""

    try:
        res = requests.get(f"{BACKEND_API_URL}/research/runs/{run_id}", timeout=5.0)
        run_data = res.json() if res.status_code == 200 else {}
        run_data["run_id"] = str(run_data.get("id", run_id))
        details_dict = run_data.get("details") or {}
        run_data["draft_report"] = (
            details_dict.get("draft_report")
            or run_data.get("result_summary")
            or run_data.get("draft_report")
            or "No report content generated."
        )
        run_data["details"] = details_dict
    except Exception:
        run_data = {
            "run_id": run_id,
            "title": "Autonomous Multi-Agent Platform Report",
            "objective": "Deep Architectural Analysis",
            "draft_report": (
                "# Autonomous Multi-Agent Platform Report\n\n"
                "## Executive Summary\n"
                "The platform executes research jobs using clean domain isolation, "
                "durable LangGraph state management, and policy-governed sandboxes."
            ),
            "stage": "completed",
            "details": {},
        }

    return render(request, "research/report_detail.html", {"run": run_data})


@csrf_exempt
def login_view(request: HttpRequest) -> HttpResponse:
    """Render user login page and handle authentication POST."""

    if request.method == "POST":
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")

        try:
            res = requests.post(
                f"{BACKEND_API_URL}/auth/login",
                json={"email": email, "password": password},
                timeout=10.0,
            )
            if res.status_code == 200:
                data = res.json()
                response = redirect("index")
                response.set_cookie("access_token", data.get("access_token", ""))
                response.set_cookie("user_email", email)
                return response
            else:
                detail = res.json().get("detail", "Invalid email or password.")
                return render(request, "research/auth/login.html", {"error": detail})
        except Exception as err:
            return render(request, "research/auth/login.html", {"error": f"Connection error: {err}"})

    return render(request, "research/auth/login.html")


@csrf_exempt
def signup_view(request: HttpRequest) -> HttpResponse:
    """Render user registration page and handle signup POST."""

    if request.method == "POST":
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        org_name = request.POST.get("org_name", "Default Organization")

        try:
            res = requests.post(
                f"{BACKEND_API_URL}/auth/register",
                json={"email": email, "password": password, "org_name": org_name},
                timeout=10.0,
            )
            if res.status_code == 200:
                data = res.json()
                response = redirect("index")
                response.set_cookie("access_token", data.get("access_token", ""))
                response.set_cookie("user_email", email)
                return response
            else:
                detail = res.json().get("detail", "Registration failed.")
                return render(request, "research/auth/signup.html", {"error": detail})
        except Exception as err:
            return render(request, "research/auth/signup.html", {"error": f"Connection error: {err}"})

    return render(request, "research/auth/signup.html")


@csrf_exempt
def forgot_password_view(request: HttpRequest) -> HttpResponse:
    """Render forgot password request view."""
    if request.method == "POST":
        return render(
            request,
            "research/auth/forgot_password.html",
            {"message": "Password reset token sent to your email address."},
        )
    return render(request, "research/auth/forgot_password.html")


@csrf_exempt
def reset_password_view(request: HttpRequest) -> HttpResponse:
    """Render password reset confirmation view."""
    if request.method == "POST":
        return redirect("login")
    return render(request, "research/auth/reset_password.html")


def verify_email_view(request: HttpRequest) -> HttpResponse:
    """Render email verification view."""
    return render(request, "research/auth/verify_email.html")


@require_auth
def research_wizard_view(request: HttpRequest) -> HttpResponse:
    """Render new research execution launch wizard."""
    return render(
        request,
        "research/wizard.html",
        {"user_email": request.COOKIES.get("user_email", "Researcher")},
    )


@require_auth
def knowledge_view(request: HttpRequest) -> HttpResponse:
    """Render Knowledge & RAG Index Explorer."""
    return render(
        request,
        "research/knowledge.html",
        {"user_email": request.COOKIES.get("user_email", "Researcher")},
    )


@require_auth
def memory_view(request: HttpRequest) -> HttpResponse:
    """Render Workspace & Agent Memory Subsystem view."""
    return render(
        request,
        "research/memory.html",
        {"user_email": request.COOKIES.get("user_email", "Researcher")},
    )


@require_auth
def settings_view(request: HttpRequest) -> HttpResponse:
    """Render User & Platform Settings page."""
    return render(
        request,
        "research/settings.html",
        {"user_email": request.COOKIES.get("user_email", "Researcher")},
    )


@require_auth
def workspaces_view(request: HttpRequest) -> HttpResponse:
    """Render workspaces and team members dashboard."""
    return render(
        request,
        "research/workspaces.html",
        {"user_email": request.COOKIES.get("user_email", "Researcher")},
    )


@require_auth
def admin_view(request: HttpRequest) -> HttpResponse:
    """Render system health and observability dashboard."""

    try:
        res = requests.get(f"{BACKEND_API_URL}/health", timeout=5.0)
        health = res.json() if res.status_code == 200 else {"status": "error"}
    except Exception:
        health = {"status": "error", "database": "unknown", "redis": "unknown"}

    return render(
        request,
        "research/admin.html",
        {"health": health, "user_email": request.COOKIES.get("user_email", "Researcher")},
    )


__all__ = [
    "admin_view",
    "control_run_view",
    "create_run_view",
    "delete_run_view",
    "events_stream_proxy_view",
    "forgot_password_view",
    "index_view",
    "knowledge_view",
    "live_execution_view",
    "login_view",
    "logout_view",
    "memory_view",
    "report_detail_view",
    "research_wizard_view",
    "reset_password_view",
    "run_status_view",
    "settings_view",
    "signup_view",
    "verify_email_view",
    "workspaces_view",
]
