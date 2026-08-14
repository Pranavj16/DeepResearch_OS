import time
from django.test import Client, TestCase
try:
    import jwt
except ImportError:
    jwt = None


class FrontendViewsTestCase(TestCase):
    """Test suite covering template rendering for all platform views."""

    def setUp(self) -> None:
        self.client = Client()
        if jwt is not None:
            token = jwt.encode(
                {
                    "sub": "test.researcher@company.com",
                    "email": "test.researcher@company.com",
                    "exp": int(time.time()) + 7200,
                },
                "django-insecure-test-key-2026-minimum-32-chars-long",
                algorithm="HS256",
            )
        else:
            token = "mock_test_token"
        self.client.cookies["access_token"] = token
        self.client.cookies["user_email"] = "test.researcher@company.com"

    def test_dashboard_index_view(self) -> None:
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Autonomous Deep Research')

    def test_research_wizard_view(self) -> None:
        response = self.client.get('/research/new')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Launch Autonomous Goal')

    def test_live_execution_view(self) -> None:
        response = self.client.get('/research/live/sample-run-123')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '8 Specialist Agents')

    def test_events_stream_proxy_view(self) -> None:
        response = self.client.get('/api/v1/events/stream/sample-run-123')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')

    def test_report_detail_view(self) -> None:
        response = self.client.get('/report/sample-run-123')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Report')

    def test_login_view(self) -> None:
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')

    def test_signup_view(self) -> None:
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')

    def test_forgot_password_view(self) -> None:
        response = self.client.get('/forgot-password')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reset Your Password')

    def test_reset_password_view(self) -> None:
        response = self.client.get('/reset-password')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Set New Password')

    def test_verify_email_view(self) -> None:
        response = self.client.get('/verify-email')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Check Your Inbox')

    def test_knowledge_view(self) -> None:
        response = self.client.get('/knowledge')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Knowledge & RAG Index Explorer')

    def test_memory_view(self) -> None:
        response = self.client.get('/memory')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Workspace & Agent Memory Subsystem')

    def test_settings_view(self) -> None:
        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Account Settings & Preferences')

    def test_workspaces_view(self) -> None:
        response = self.client.get('/workspaces')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Workspaces & Governance')

    def test_admin_view(self) -> None:
        response = self.client.get('/admin/system')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'System Health & Observability')
