from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_phase7_api_success_contract(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.query_routes.run_query",
        lambda question, collection=None, section_hint=None: {  # noqa: ARG005
            "parsed_query": {"collection": "RELIANCE"},
            "plan": {"steps": []},
            "execution": {
                "documents": [{"document_id": "d1"}],
                "references": [],
            },
            "context": {
                "summary": {
                    "document_count": 1,
                    "chunk_count": 1,
                    "event_count": 0,
                    "reference_count": 0,
                    "table_count": 0,
                },
                "documents": [{"document_id": "d1"}],
                "evidence": [],
                "reference_traces": [],
                "table_evidence": [],
            },
            "answer": {
                "question": question,
                "direct_answer": "ok",
                "confidence": 0.8,
                "context_summary": "documents=1",
                "supporting_facts": [],
            },
        },
    )
    response = client.post("/query/ask", json={"question": "Why revenue changed?", "collection": "RELIANCE"})
    assert response.status_code == 200
    payload = response.json()
    assert "parsed_query" in payload
    assert "execution" in payload
    assert "answer" in payload


def test_phase7_api_missing_collection_error(monkeypatch) -> None:
    def _raise(*args, **kwargs):  # noqa: ANN002, ANN003
        raise ValueError("collection is required")

    monkeypatch.setattr("app.api.query_routes.run_query", _raise)
    response = client.post("/query/ask", json={"question": "Why revenue changed?"})
    assert response.status_code == 400
    assert response.json()["detail"]["error"]["code"] == "missing_collection"


def test_phase7_api_no_documents_error(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.query_routes.run_query",
        lambda question, collection=None, section_hint=None: {  # noqa: ARG005
            "parsed_query": {},
            "plan": {},
            "execution": {"documents": [], "references": []},
            "context": {
                "summary": {
                    "document_count": 0,
                    "chunk_count": 0,
                    "event_count": 0,
                    "reference_count": 0,
                    "table_count": 0,
                },
                "documents": [],
                "evidence": [],
                "reference_traces": [],
                "table_evidence": [],
            },
            "answer": {
                "question": question,
                "direct_answer": "none",
                "confidence": 0.1,
                "context_summary": "documents=0",
                "supporting_facts": [],
            },
        },
    )
    response = client.post("/query/ask", json={"question": "Q1 FY24 for RELIANCE"})
    assert response.status_code == 404
    assert response.json()["detail"]["error"]["code"] == "no_documents_in_time_range"


def test_phase7_api_unresolved_reference_error(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.query_routes.run_query",
        lambda question, collection=None, section_hint=None: {  # noqa: ARG005
            "parsed_query": {},
            "plan": {},
            "execution": {
                "documents": [{"document_id": "d1"}],
                "references": [{"reference_text": "Table 9", "resolved": False}],
            },
            "context": {
                "summary": {
                    "document_count": 1,
                    "chunk_count": 1,
                    "event_count": 0,
                    "reference_count": 1,
                    "table_count": 0,
                },
                "documents": [{"document_id": "d1"}],
                "evidence": [],
                "reference_traces": [],
                "table_evidence": [],
            },
            "answer": {
                "question": question,
                "direct_answer": "partial",
                "confidence": 0.3,
                "context_summary": "documents=1",
                "supporting_facts": [],
            },
        },
    )
    response = client.post(
        "/query/ask",
        json={"question": "Q1 FY24 for RELIANCE", "strict_reference_resolution": True},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["error"]["code"] == "unresolved_reference"


def test_phase7_api_unresolved_reference_allowed_in_non_strict_mode(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.query_routes.run_query",
        lambda question, collection=None, section_hint=None: {  # noqa: ARG005
            "parsed_query": {},
            "plan": {},
            "execution": {
                "documents": [{"document_id": "d1"}],
                "references": [{"reference_text": "Table 9", "resolved": False}],
            },
            "context": {
                "summary": {
                    "document_count": 1,
                    "chunk_count": 1,
                    "event_count": 0,
                    "reference_count": 1,
                    "table_count": 0,
                },
                "documents": [{"document_id": "d1"}],
                "evidence": [],
                "reference_traces": [],
                "table_evidence": [],
            },
            "answer": {
                "question": question,
                "direct_answer": "partial",
                "confidence": 0.3,
                "context_summary": "documents=1",
                "supporting_facts": [],
            },
        },
    )
    response = client.post("/query/ask", json={"question": "Q1 FY24 for RELIANCE"})
    assert response.status_code == 200
    assert "answer" in response.json()
