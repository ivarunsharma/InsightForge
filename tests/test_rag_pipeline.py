from unittest.mock import MagicMock, patch
from src.rag_pipeline import build_rag_chain, CONTEXTUALIZE_Q_PROMPT, QA_PROMPT


# ── build_rag_chain ───────────────────────────────────────────────────────────

class TestBuildRagChain:
    def _mock_vectorstore(self):
        vs = MagicMock()
        vs.as_retriever.return_value = MagicMock()
        return vs

    def test_returns_a_chain(self):
        vs = self._mock_vectorstore()
        with patch("src.rag_pipeline.get_llm", return_value=MagicMock()):
            chain = build_rag_chain(vs)
            assert chain is not None

    def test_default_k_is_5(self):
        vs = self._mock_vectorstore()
        with patch("src.rag_pipeline.get_llm", return_value=MagicMock()):
            build_rag_chain(vs)
            vs.as_retriever.assert_called_once_with(search_kwargs={"k": 5})

    def test_custom_k_is_passed_to_retriever(self):
        vs = self._mock_vectorstore()
        with patch("src.rag_pipeline.get_llm", return_value=MagicMock()):
            build_rag_chain(vs, k=8)
            vs.as_retriever.assert_called_once_with(search_kwargs={"k": 8})

    def test_k3_is_passed_to_retriever(self):
        vs = self._mock_vectorstore()
        with patch("src.rag_pipeline.get_llm", return_value=MagicMock()):
            build_rag_chain(vs, k=3)
            vs.as_retriever.assert_called_once_with(search_kwargs={"k": 3})


# ── Prompt structure ──────────────────────────────────────────────────────────

class TestPrompts:
    def test_contextualize_prompt_has_required_variables(self):
        assert "chat_history" in CONTEXTUALIZE_Q_PROMPT.input_variables
        assert "input" in CONTEXTUALIZE_Q_PROMPT.input_variables

    def test_qa_prompt_has_required_variables(self):
        assert "context" in QA_PROMPT.input_variables
        assert "input" in QA_PROMPT.input_variables
        assert "chat_history" in QA_PROMPT.input_variables
