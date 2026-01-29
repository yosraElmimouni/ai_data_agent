import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_read_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "AI Data Agent API is running"})

    @patch("backend.main.AIAgent")
    def test_ask_question_success(self, mock_agent_class):
        # Mock de l'instance de l'agent
        mock_agent_instance = mock_agent_class.return_value
        mock_agent_instance.question.return_value = "Réponse de test"
        
        payload = {
            "question": "Quelle est la liste des clients ?",
            "api_key": "test_key"
        }
        
        response = self.client.post("/ask", json=payload)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "Réponse de test"})
        mock_agent_instance.question.assert_called_once()

    @patch("backend.main.AIAgent")
    def test_ask_question_error(self, mock_agent_class):
        # Simulation d'une erreur interne
        mock_agent_instance = mock_agent_class.return_value
        mock_agent_instance.question.side_effect = Exception("Erreur interne")
        
        payload = {
            "question": "Question ?",
            "api_key": "test_key"
        }
        
        response = self.client.post("/ask", json=payload)
        
        self.assertEqual(response.status_code, 500)
        self.assertIn("Erreur interne", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
