import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app  # À adapter selon ta structure

client = TestClient(app)


class TestOnboardingStart:
    """Tests pour l'endpoint POST /onboarding/start"""

    @patch("app.db.session_store.create_session")
    @patch("app.services.onboarding_planner.first_question")
    def test_start_success(self, mock_first_question, mock_create_session):
        # Setup mocks
        mock_create_session.return_value = {"session_id": "sess_123", "user_id": "user_1"}
        mock_first_question.return_value = {
            "slot": "name",
            "text": "Quel est votre nom?",
            "type": "text"
        }

        # Appel
        response = client.post("/onboarding/start?user_id=user_1")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "sess_123"
        assert data["question"]["slot"] == "name"
        mock_create_session.assert_called_once_with("user_1")

    @patch("app.db.session_store.create_session")
    def test_start_invalid_user(self, mock_create_session):
        # Setup: simulate error
        mock_create_session.side_effect = ValueError("User ID invalide")

        # Appel
        response = client.post("/onboarding/start?user_id=invalid")

        # Assertions
        assert response.status_code == 400
        assert "User ID invalide" in response.json()["detail"]

    def test_start_missing_user_id(self):
        # Appel sans user_id
        response = client.post("/onboarding/start")

        # Assertions
        assert response.status_code == 422  # Validation error


class TestOnboardingNext:
    """Tests pour l'endpoint GET /onboarding/next"""

    @patch("app.db.session_store.get_session")
    @patch("app.services.onboarding_planner.next_required_slot")
    @patch("app.services.onboarding_planner.question_for_slot")
    def test_next_with_required_slot(self, mock_question_for_slot, mock_next_required_slot, mock_get_session):
        # Setup mocks
        mock_get_session.return_value = {
            "session_id": "sess_123",
            "slots": {"name": "John"},
            "asked_ai_count": 0
        }
        mock_next_required_slot.return_value = "age"
        mock_question_for_slot.return_value = {
            "slot": "age",
            "text": "Quel est votre âge?",
            "type": "number"
        }

        # Appel
        response = client.get("/onboarding/next?session_id=sess_123")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["finished"] is False
        assert data["question"]["slot"] == "age"

    @patch("app.db.session_store.get_session")
    @patch("app.services.onboarding_planner.next_required_slot")
    @patch("app.ai.onboarding_ai.suggest_followup")
    def test_next_with_ai_followup(self, mock_suggest_followup, mock_next_required_slot, mock_get_session):
        # Setup mocks
        session = {
            "session_id": "sess_123",
            "slots": {"name": "John", "age": 30},
            "asked_ai_count": 0
        }
        mock_get_session.return_value = session
        mock_next_required_slot.return_value = None
        mock_suggest_followup.return_value = {
            "slot": "goals",
            "text": "Quels sont vos objectifs?",
            "type": "text"
        }

        # Appel
        response = client.get("/onboarding/next?session_id=sess_123")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["finished"] is False
        assert "goals" in data["question"]["slot"]
        assert session["asked_ai_count"] == 1

    @patch("app.db.session_store.get_session")
    @patch("app.services.onboarding_planner.next_required_slot")
    @patch("app.ai.onboarding_ai.suggest_followup")
    def test_next_completed(self, mock_suggest_followup, mock_next_required_slot, mock_get_session):
        # Setup mocks: aucun slot requis, aucune question IA
        mock_get_session.return_value = {
            "session_id": "sess_123",
            "slots": {"name": "John", "age": 30},
            "asked_ai_count": 0
        }
        mock_next_required_slot.return_value = None
        mock_suggest_followup.return_value = None

        # Appel
        response = client.get("/onboarding/next?session_id=sess_123")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["finished"] is True
        assert "profile_preview" in data
        assert data["profile_preview"]["name"] == "John"

    @patch("app.db.session_store.get_session")
    def test_next_unknown_session(self, mock_get_session):
        # Setup: session inexistante
        mock_get_session.return_value = None

        # Appel
        response = client.get("/onboarding/next?session_id=invalid_sess")

        # Assertions
        assert response.status_code == 404
        assert "Session inconnue" in response.json()["detail"]


class TestOnboardingEnd:
    """Tests pour l'endpoint POST /onboarding/end"""

    @patch("app.db.session_store.get_session")
    def test_end_success(self, mock_get_session):
        # Setup mocks
        session = {
            "session_id": "sess_123",
            "slots": {"name": "John", "height_cm": 180, "weight_kg": 75},
            "state": "IN_PROGRESS"
        }
        mock_get_session.return_value = session

        # Appel
        response = client.post("/onboarding/end?session_id=sess_123")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["session_id"] == "sess_123"
        assert "profile" in data
        assert data["profile"]["name"] == "John"
        assert session["state"] == "COMPLETED"

    @patch("app.db.session_store.get_session")
    def test_end_calcul_bmi(self, mock_get_session):
        # Setup: vérifier le calcul IMC
        session = {
            "session_id": "sess_123",
            "slots": {"name": "John", "height_cm": 180, "weight_kg": 75}
        }
        mock_get_session.return_value = session

        # Appel
        response = client.post("/onboarding/end?session_id=sess_123")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        expected_bmi = round(75 / ((180 / 100) ** 2), 1)
        assert data["profile"]["bmi"] == expected_bmi

    @patch("app.db.session_store.get_session")
    def test_end_bmi_invalid_data(self, mock_get_session):
        # Setup: données invalides pour IMC
        session = {
            "session_id": "sess_123",
            "slots": {"name": "John", "height_cm": "abc", "weight_kg": "xyz"}
        }
        mock_get_session.return_value = session

        # Appel
        response = client.post("/onboarding/end?session_id=sess_123")

        # Assertions: pas d'erreur, juste pas de BMI
        assert response.status_code == 200
        data = response.json()
        assert "bmi" not in data["profile"]

    @patch("app.db.session_store.get_session")
    def test_end_unknown_session(self, mock_get_session):
        # Setup: session inexistante
        mock_get_session.return_value = None

        # Appel
        response = client.post("/onboarding/end?session_id=invalid_sess")

        # Assertions
        assert response.status_code == 404
        assert "Session inconnue" in response.json()["detail"]

