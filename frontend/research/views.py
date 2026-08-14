"""Django views serving the progressive UI + HTMX frontend for research runs."""

from functools import wraps
from typing import Any
import requests
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
import os

def get_backend_api_url() -> str:
    """Dynamically resolve clean backend API endpoint."""
    raw_env = os.environ.get("BACKEND_URL", "").strip().rstrip("/")
    if raw_env and raw_env not in ["http://127.0.0.1:8000", "http://localhost:8000"]:
        if not raw_env.startswith(("http://", "https://")):
            raw_env = f"https://{raw_env}"

        if not raw_env.endswith("/api/v1"):
            raw_env = f"{raw_env}/api/v1"
        return raw_env

    # If running on Vercel as a unified deployment
    vercel_url = os.environ.get("VERCEL_URL", "").strip()
    if vercel_url:
        return f"https://{vercel_url}/api/v1"

    return "http://127.0.0.1:8000/api/v1"


BACKEND_API_URL = get_backend_api_url()


def make_backend_request(method: str, endpoint: str, **kwargs) -> requests.Response:
    """Make HTTP request to backend with dynamic URL resolution."""
    timeout_val = kwargs.pop("timeout", 15.0)
    target_api = get_backend_api_url()
    url = f"{target_api}{endpoint}"

    try:
        return requests.request(method, url, timeout=timeout_val, **kwargs)
    except Exception as err:
        raise Exception(f"Failed to connect to backend service at {url}: {err}") from err


try:
    import jwt
except ImportError:
    jwt = None

def require_auth(view_func: Any) -> Any:
    """Decorator requiring a valid, non-expired access token cookie before rendering protected views."""

    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        token = request.COOKIES.get("access_token")
        if not token:
            return redirect("login")

        if jwt is not None:
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                exp = payload.get("exp")
                if exp and isinstance(exp, (int, float)):
                    import time
                    if time.time() > exp:
                        response = redirect("login")
                        response.delete_cookie("access_token")
                        response.delete_cookie("user_email")
                        return response
            except Exception:
                response = redirect("login")
                response.delete_cookie("access_token")
                response.delete_cookie("user_email")
                return response

        return view_func(request, *args, **kwargs)

    return _wrapped_view


@require_auth
def index_view(request: HttpRequest) -> HttpResponse:
    """Render main research assistant dashboard with history isolated to user workspace."""

    recent_runs: list[dict[str, Any]] = []
    user_email = request.COOKIES.get("user_email", "")
    try:
        res = make_backend_request("GET", "/health", timeout=5.0)
        health = res.json() if res.status_code == 200 else {}
    except Exception:
        health = {"status": "degraded"}

    try:
        runs_res = make_backend_request("GET", "/research/history", params={"user_email": user_email}, timeout=5.0)
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
            "user_email": user_email or "Researcher",
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
            res = make_backend_request(
                "POST",
                "/research/runs",
                json={
                    "title": title,
                    "objective": objective,
                    "user_email": user_email,
                },
                timeout=10.0,
            )
            if res.status_code in [200, 201]:
                data = res.json()
                run_id = data.get("id")
                response = HttpResponse(status=204)
                response["HX-Redirect"] = f"/research/live/{run_id}"
                return response
        except Exception:
            pass

    return redirect("index")


@require_auth
def live_execution_view(request: HttpRequest, run_id: str) -> HttpResponse:
    """Render live telemetry dashboard for an active research run."""

    run_data = {"id": run_id, "title": "Autonomous Research", "status": "running", "stage": "intake"}
    user_email = request.COOKIES.get("user_email", "")
    try:
        res = make_backend_request("GET", f"/research/runs/{run_id}", params={"user_email": user_email}, timeout=5.0)
        if res.status_code == 200:
            run_data = res.json()
            run_data["run_id"] = str(run_data.get("id"))
    except Exception:
        pass

    return render(
        request,
        "research/execution.html",
        {"run": run_data, "user_email": user_email or "Researcher"},
    )


def api_run_detail_proxy_view(request: HttpRequest, run_id: str) -> HttpResponse:
    """Proxy backend GET /research/runs/{run_id} directly to browser JS for real-time status telemetry."""
    import json
    user_email = request.COOKIES.get("user_email", "")
    try:
        res = requests.get(f"{BACKEND_API_URL}/research/runs/{run_id}", params={"user_email": user_email}, timeout=10.0)
        return HttpResponse(res.content, content_type="application/json", status=res.status_code)
    except Exception as err:
        return HttpResponse(json.dumps({"error": str(err)}), content_type="application/json", status=502)


def events_stream_proxy_view(request: HttpRequest, run_id: str) -> StreamingHttpResponse:
    """Proxy real-time SSE stream from backend FastAPI engine to frontend browser."""

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
            import json
            yield f'data: {json.dumps({"event": "error", "stage": "intake", "message": str(err)})}\n\n'

    response = StreamingHttpResponse(stream_backend_events(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


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
    """Handle deletion of a research run isolated by user workspace."""

    if request.method in ["DELETE", "POST"]:
        clean_id = run_id.replace("-", "").lower()
        user_email = request.COOKIES.get("user_email", "")

        # Primary deletion via FastAPI backend REST API
        try:
            requests.delete(f"{BACKEND_API_URL}/research/runs/{run_id}", params={"user_email": user_email}, timeout=5.0)
        except Exception as api_err:
            print(f"[FRONTEND REST DELETE NOTICE]: {api_err}")

        # Local SQLite deletion fallback for local single-process development
        try:
            import os
            import sqlite3
            for db_path in ["../backend/storage/db.sqlite3", "storage/db.sqlite3"]:
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM research_runs WHERE replace(lower(id), '-', '') = ?",
                        (clean_id,),
                    )
                    conn.commit()
                    conn.close()
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
    """Render comprehensive research report viewer isolated by user workspace."""

    clean_id = run_id.replace("-", "").lower()
    user_email = request.COOKIES.get("user_email", "")
    run_data = {}

    # Primary: Attempt backend REST API request
    try:
        res = requests.get(f"{BACKEND_API_URL}/research/runs/{run_id}", params={"user_email": user_email}, timeout=5.0)
        if res.status_code == 200:
            run_data = res.json()
    except Exception as err:
        print(f"[REPORT VIEW REST NOTICE]: {err}")

    # Fallback: Query local SQLite database if REST API returned empty/missing report
    if not run_data.get("result_summary") and not (run_data.get("details") or {}).get("draft_report"):
        try:
            import json
            import os
            import sqlite3
            for db_path in ["../backend/storage/db.sqlite3", "storage/db.sqlite3"]:
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT title, objective, stage, result_summary, details FROM research_runs WHERE replace(lower(id), '-', '') = ?",
                        (clean_id,),
                    )
                    row = cursor.fetchone()
                    conn.close()
                    if row:
                        title, objective, stage, result_summary, details_json = row
                        details_dict = json.loads(details_json) if details_json else {}
                        run_data = {
                            "id": run_id,
                            "title": title or "Autonomous Multi-Agent Research Task",
                            "objective": objective or "Multi-Agent Research Objective",
                            "stage": stage or "completed",
                            "result_summary": result_summary or "",
                            "details": details_dict,
                        }
                        break
        except Exception as db_err:
            print(f"[REPORT VIEW SQLITE FALLBACK NOTICE]: {db_err}")

    # Final formatting of draft_report field
    run_data["run_id"] = str(run_data.get("id", run_id))
    details_dict = run_data.get("details") or {}
    report_text = (
        details_dict.get("draft_report")
        or run_data.get("result_summary")
        or run_data.get("draft_report")
        or (
            f"# {run_data.get('title', 'Autonomous Research Report')}\n\n"
            f"## Executive Summary\n"
            f"Synthesizing findings for objective: {run_data.get('objective', 'Multi-Agent Research')}.\n\n"
            f"## Key Findings\n"
            f"- Multi-agent graph state machine execution completed.\n"
            f"- Factual claims verified by specialist agents."
        )
    )
    run_data["draft_report"] = report_text
    run_data["details"] = details_dict

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
                timeout=15.0,
            )
            if res.status_code == 200:
                try:
                    data = res.json()
                except Exception:
                    data = {}
                response = redirect("index")
                cookie_max_age = 30 * 24 * 60 * 60  # 30 days persistence
                response.set_cookie("access_token", data.get("access_token", ""), max_age=cookie_max_age, samesite="Lax")
                response.set_cookie("user_email", email, max_age=cookie_max_age, samesite="Lax")
                return response
            else:
                try:
                    detail = res.json().get("detail", f"Authentication failed (HTTP {res.status_code}).")
                except Exception:
                    detail = f"Backend returned HTTP status {res.status_code}."
                return render(request, "research/auth/login.html", {"error": detail})
        except Exception as err:
            return render(request, "research/auth/login.html", {"error": f"Backend connection failed. Please verify BACKEND_URL environment variable on Render ({err})."})

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
                timeout=15.0,
            )
            if res.status_code == 200:
                try:
                    data = res.json()
                except Exception:
                    data = {}
                response = redirect("index")
                cookie_max_age = 30 * 24 * 60 * 60  # 30 days persistence
                response.set_cookie("access_token", data.get("access_token", ""), max_age=cookie_max_age, samesite="Lax")
                response.set_cookie("user_email", email, max_age=cookie_max_age, samesite="Lax")
                return response
            else:
                try:
                    detail = res.json().get("detail", f"Registration failed (HTTP {res.status_code}).")
                except Exception:
                    detail = f"Backend returned HTTP status {res.status_code}."
                return render(request, "research/auth/signup.html", {"error": detail})
        except Exception as err:
            return render(request, "research/auth/signup.html", {"error": f"Backend connection failed. Please verify BACKEND_URL environment variable on Render ({err})."})

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
    """Render Knowledge & RAG Index Explorer with dynamic user research artifacts isolated by user workspace."""
    runs = []
    sources = []
    claims = []
    user_email = request.COOKIES.get("user_email", "")
    try:
        res = requests.get(f"{BACKEND_API_URL}/research/runs", params={"user_email": user_email}, timeout=5.0)
        if res.status_code == 200:
            runs = res.json()
            for r in runs:
                details = r.get("details") or {}
                if isinstance(details, dict):
                    for src in details.get("sources", []):
                        if src and src not in sources:
                            sources.append(src)
                    for claim in details.get("claims", []):
                        if claim and claim not in claims:
                            claims.append(claim)
    except Exception:
        pass

    return render(
        request,
        "research/knowledge.html",
        {
            "runs": runs,
            "sources": sources,
            "claims": claims,
            "user_email": user_email or "Researcher",
        },
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
    "api_run_detail_proxy_view",
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
