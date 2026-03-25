import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient) -> None:
        assert client.get("/health").status_code == 200

    def test_health_response_shape(self, client: TestClient) -> None:
        data = client.get("/health").json()
        assert data["status"] == "ok"


class TestAnalyzeEndpoint:
    def test_submit_valid_url(self, client: TestClient) -> None:
        mock_task = MagicMock()
        mock_task.id = "test-job-id-123"
        with patch("app.api.routes.analyze.analysis_tasks.run_analysis") as mock:
            mock.delay.return_value = mock_task
            response = client.post("/api/v1/analyze", json={"url": "https://example.com/article"})
        assert response.status_code == 200
        assert response.json()["job_id"] == "test-job-id-123"

    def test_submit_invalid_url(self, client: TestClient) -> None:
        assert client.post("/api/v1/analyze", json={"url": "not-a-url"}).status_code == 422

    def test_submit_missing_url(self, client: TestClient) -> None:
        assert client.post("/api/v1/analyze", json={}).status_code == 422

    def test_get_result_pending(self, client: TestClient) -> None:
        mock_task = MagicMock()
        mock_task.state = "PENDING"
        with patch("app.api.routes.analyze.analysis_tasks.run_analysis") as mock:
            mock.AsyncResult.return_value = mock_task
            response = client.get("/api/v1/result/some-job-id")
        assert response.json()["status"] == "pending"
