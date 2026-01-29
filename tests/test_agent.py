import unittest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

from backend.agent import AIAgent


class FakeRow:
    def __init__(self, mapping):
        self._mapping = mapping


class FakeSession:
    def __init__(self, results=None, raise_on_execute=False):
        self._results = results or []
        self._raise = raise_on_execute
        self.queries = []

    def execute(self, sql_text):
        # Record executed SQL for assertions
        self.queries.append(str(sql_text))
        if self._raise:
            raise Exception("DB Error")
        return self._results


class TestAIAgent(unittest.TestCase):

    def setUp(self):
        # Use a dummy API key. We'll mock network calls.
        self.agent = AIAgent(api_key="test_key", base_url="http://example")

    def _mock_openai_response(self, content: str):
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])

    @patch("backend.agent.OpenAI")
    def test_sqlGeneration_strips_code_fences_and_prefixes(self, mock_openai_cls):
        # Arrange
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._mock_openai_response(
            """```sql\n-- comment that should be ignored\n  SELECT * FROM customers;\n```"""
        )
        mock_openai_cls.return_value = mock_client

        agent = AIAgent(api_key="k", base_url="http://example")

        # Act
        sql = agent.sqlGeneration("Liste tous les clients")

        # Assert
        self.assertEqual(sql, "SELECT * FROM customers;")
        mock_client.chat.completions.create.assert_called()

    def test_ececution_success_returns_list_of_dicts(self):
        # Arrange
        result_rows = [FakeRow({"id": 1, "name": "Alice"}), FakeRow({"id": 2, "name": "Bob"})]
        db = FakeSession(results=result_rows)

        # Act
        out = self.agent.ececution(db, "SELECT * FROM customers")

        # Assert
        self.assertEqual(out, [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])

    def test_ececution_on_exception_returns_none(self):
        # Arrange
        db = FakeSession(raise_on_execute=True)

        # Act
        out = self.agent.ececution(db, "BROKEN SQL")

        # Assert
        self.assertIsNone(out)

    def test_question_returns_message_when_non_lie(self):
        # Arrange
        db = FakeSession()
        with patch.object(self.agent, "sqlGeneration", return_value="NON_LIE"):
            # Act
            out = self.agent.question(db, "Quel temps fait-il ?")

        # Assert
        self.assertIn("Désolé, je ne peux répondre", out)

    def test_question_retries_sql_on_failure_and_then_succeeds(self):
        # Arrange
        db = FakeSession()
        # First call returns None, second returns data
        with patch.object(self.agent, "sqlGeneration", side_effect=["SELECT bad", "SELECT good"]) as gen_sql, \
             patch.object(self.agent, "ececution", side_effect=[None, [{"count": 10}]]) as exec_q, \
             patch.object(self.agent, "genererReponseNaturelle", return_value="Réponse OK") as nat_resp:

            # Act
            out = self.agent.question(db, "Combien de commandes ?")

            # Assert
            self.assertEqual(out, "Réponse OK")
            self.assertEqual(gen_sql.call_count, 2)
            self.assertEqual(exec_q.call_count, 2)
            nat_resp.assert_called_once_with("Combien de commandes ?", [{"count": 10}])

    def test_question_returns_failure_message_after_two_failures(self):
        # Arrange
        db = FakeSession()
        with patch.object(self.agent, "sqlGeneration", side_effect=["SELECT bad", "SELECT still bad"]) as gen_sql, \
             patch.object(self.agent, "ececution", return_value=None) as exec_q:

            # Act
            out = self.agent.question(db, "Question")

            # Assert
            self.assertIn("Je n’ai pas pu répondre correctement", out)
            self.assertEqual(gen_sql.call_count, 2)
            # Two executions attempted
            self.assertEqual(exec_q.call_count, 2)

    @patch("backend.agent.OpenAI")
    def test_genererReponseNaturelle_returns_text(self, mock_openai_cls):
        # Arrange
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._mock_openai_response(
            "Voici une réponse claire."
        )
        mock_openai_cls.return_value = mock_client
        agent = AIAgent(api_key="k", base_url="http://example")

        # Act
        out = agent.genererReponseNaturelle("Question?", [{"id": 1}])

        # Assert
        self.assertEqual(out, "Voici une réponse claire.")
        mock_client.chat.completions.create.assert_called()

    @patch("backend.agent.OpenAI")
    def test_sqlGeneration_removes_leading_prose_before_select(self, mock_openai_cls):
        # Arrange
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._mock_openai_response(
            "Voici la requête:\nSELECT id FROM customers;"
        )
        mock_openai_cls.return_value = mock_client
        agent = AIAgent(api_key="k", base_url="http://example")

        # Act
        sql = agent.sqlGeneration("Liste des IDs clients")

        # Assert
        self.assertEqual(sql, "SELECT id FROM customers;")

    @patch("backend.agent.OpenAI")
    def test_sqlGeneration_supports_with_keyword(self, mock_openai_cls):
        # Arrange
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._mock_openai_response(
            "Texte introductif\nWITH cte AS (SELECT id FROM customers) SELECT * FROM cte;"
        )
        mock_openai_cls.return_value = mock_client
        agent = AIAgent(api_key="k", base_url="http://example")

        # Act
        sql = agent.sqlGeneration("Utiliser une CTE")

        # Assert
        self.assertTrue(sql.startswith("WITH"))
        self.assertIn("SELECT * FROM cte;", sql)

    @patch("backend.agent.OpenAI")
    def test_sqlGeneration_strips_generic_fences_without_language(self, mock_openai_cls):
        # Arrange
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._mock_openai_response(
            "```\nSELECT * FROM products;\n```"
        )
        mock_openai_cls.return_value = mock_client
        agent = AIAgent(api_key="k", base_url="http://example")

        # Act
        sql = agent.sqlGeneration("Tous les produits")

        # Assert
        self.assertEqual(sql, "SELECT * FROM products;")

    def test_question_uses_empty_list_without_retry_and_passes_to_nat_response(self):
        # Arrange
        db = FakeSession()
        with patch.object(self.agent, "sqlGeneration", return_value="SELECT * FROM orders") as gen_sql, \
             patch.object(self.agent, "ececution", return_value=[]) as exec_q, \
             patch.object(self.agent, "genererReponseNaturelle", return_value="Aucune information trouvée") as nat_resp:

            # Act
            out = self.agent.question(db, "Quelles commandes ?")

            # Assert
            self.assertEqual(out, "Aucune information trouvée")
            gen_sql.assert_called_once()
            exec_q.assert_called_once()
            nat_resp.assert_called_once_with("Quelles commandes ?", [])

    def test_ececution_calls_db_execute_with_text(self):
        # Arrange
        db = FakeSession(results=[])

        # Act
        _ = self.agent.ececution(db, "SELECT * FROM products")

        # Assert
        self.assertEqual(len(db.queries), 1)
        self.assertIn("SELECT * FROM products", db.queries[0])


    @patch("backend.agent.OpenAI")
    def test_sqlGeneration_extracts_from_update(self, mock_openai_cls):
        # Arrange
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._mock_openai_response(
            "Texte préalable\nUPDATE customers SET name='Alice' WHERE id = 1;"
        )
        mock_openai_cls.return_value = mock_client
        agent = AIAgent(api_key="k", base_url="http://example")

        # Act
        sql = agent.sqlGeneration("Mettre à jour le nom du client 1 en Alice")

        # Assert
        self.assertEqual(sql, "UPDATE customers SET name='Alice' WHERE id = 1;")

    @patch("backend.agent.OpenAI")
    def test_sqlGeneration_returns_non_lie_even_if_in_code_fences(self, mock_openai_cls):
        # Arrange
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._mock_openai_response(
            "```NON_LIE```"
        )
        mock_openai_cls.return_value = mock_client
        agent = AIAgent(api_key="k", base_url="http://example")

        # Act
        sql = agent.sqlGeneration("Question hors périmètre")

        # Assert
        self.assertEqual(sql, "NON_LIE")

    def test_ececution_returns_empty_list_when_no_rows(self):
        # Arrange
        db = FakeSession(results=[])

        # Act
        out = self.agent.ececution(db, "SELECT * FROM customers WHERE 1=0")

        # Assert
        self.assertEqual(out, [])

    def test_question_appends_retry_hint_on_second_sqlGeneration_call(self):
        # Arrange
        db = FakeSession()
        with patch.object(self.agent, "sqlGeneration", side_effect=["SQL1", "SQL2"]) as gen_sql, \
             patch.object(self.agent, "ececution", side_effect=[None, None]) as exec_q:

            # Act
            out = self.agent.question(db, "Ma question")

            # Assert
            self.assertIn("Je n’ai pas pu répondre correctement", out)
            self.assertEqual(gen_sql.call_count, 2)
            self.assertEqual(exec_q.call_count, 2)
            # Verify arguments to sqlGeneration
            first_call_arg = gen_sql.call_args_list[0].args[0]
            second_call_arg = gen_sql.call_args_list[1].args[0]
            self.assertEqual(first_call_arg, "Ma question")
            self.assertIn("(attention : génère une requête SQL valide SQLite)", second_call_arg)

    @patch("backend.agent.OpenAI")
    def test_genererReponseNaturelle_strips_whitespace(self, mock_openai_cls):
        # Arrange
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._mock_openai_response(
            "   Réponse avec espaces   \n"
        )
        mock_openai_cls.return_value = mock_client
        agent = AIAgent(api_key="k", base_url="http://example")

        # Act
        out = agent.genererReponseNaturelle("Q?", [{"id": 1}])

        # Assert
        self.assertEqual(out, "Réponse avec espaces")
        mock_client.chat.completions.create.assert_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
