from unittest.mock import MagicMock
from src.agents import _dynamic_k, _format_sources, classify_intent


def _make_doc(doc_name, page=None):
    doc = MagicMock()
    doc.metadata = {"doc_name": doc_name}
    if page is not None:
        doc.metadata["page"] = page
    return doc


# ── _dynamic_k ────────────────────────────────────────────────────────────────

class TestDynamicK:
    def test_short_question_gives_k3(self):
        assert _dynamic_k("What is total sales?") == 3

    def test_medium_question_gives_k5(self):
        q = "What are the top five sub-categories by total profit margin in 2017?"
        assert _dynamic_k(q) == 5

    def test_long_question_gives_k8(self):
        assert _dynamic_k(" ".join(["word"] * 25)) == 8

    def test_compare_keyword_gives_k8(self):
        assert _dynamic_k("Compare Technology and Furniture sales") == 8

    def test_vs_keyword_gives_k8(self):
        assert _dynamic_k("Technology vs Furniture profit margin") == 8

    def test_summarize_keyword_gives_k8(self):
        assert _dynamic_k("Summarize all customer feedback") == 8

    def test_across_keyword_gives_k8(self):
        assert _dynamic_k("Sales trends across all regions") == 8


# ── _format_sources ───────────────────────────────────────────────────────────

class TestFormatSources:
    def test_pdf_single_page_is_1_indexed(self):
        docs = [_make_doc("report.pdf", page=2)]
        assert _format_sources(docs) == ["report.pdf (p. 3)"]

    def test_pdf_multiple_pages_sorted(self):
        docs = [_make_doc("report.pdf", page=4), _make_doc("report.pdf", page=1)]
        assert _format_sources(docs) == ["report.pdf (p. 2, 5)"]

    def test_duplicate_page_deduplicated(self):
        docs = [_make_doc("report.pdf", page=2), _make_doc("report.pdf", page=2)]
        assert _format_sources(docs) == ["report.pdf (p. 3)"]

    def test_txt_has_no_page_number(self):
        docs = [_make_doc("notes.txt")]
        assert _format_sources(docs) == ["notes.txt"]

    def test_docx_has_no_page_number(self):
        docs = [_make_doc("memo.docx")]
        assert _format_sources(docs) == ["memo.docx"]

    def test_mixed_pdf_and_txt(self):
        docs = [_make_doc("report.pdf", page=0), _make_doc("notes.txt")]
        result = _format_sources(docs)
        assert "report.pdf (p. 1)" in result
        assert "notes.txt" in result

    def test_empty_context_returns_empty_list(self):
        assert _format_sources([]) == []

    def test_multiple_docs_each_get_own_entry(self):
        docs = [_make_doc("a.pdf", page=0), _make_doc("b.pdf", page=2)]
        result = _format_sources(docs)
        assert len(result) == 2


# ── classify_intent ───────────────────────────────────────────────────────────

class TestClassifyIntent:
    def _mock_llm(self, response_text):
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(content=response_text)
        return llm

    def test_structured_response(self):
        assert classify_intent("What is total sales?", self._mock_llm("structured")) == "structured"

    def test_document_response(self):
        assert classify_intent("What did the board say?", self._mock_llm("document")) == "document"

    def test_defaults_to_document_on_unknown_response(self):
        assert classify_intent("some question", self._mock_llm("unclear")) == "document"

    def test_case_insensitive_structured(self):
        assert classify_intent("question", self._mock_llm("  STRUCTURED  ")) == "structured"

    def test_llm_is_called_once(self):
        llm = self._mock_llm("structured")
        classify_intent("What is profit?", llm)
        llm.invoke.assert_called_once()
