import pandas as pd
from ml.pipeline import generate_insights_for_window


def test_pipeline_outputs_required_types():
    events = pd.DataFrame([
        {"user_id": 1, "event_type": "feature_use", "timestamp": "2026-01-01", "metadata": {"feature": "export"}},
        {"user_id": 1, "event_type": "feature_use", "timestamp": "2026-01-02", "metadata": {"feature": "export"}},
        {"user_id": 1, "event_type": "feature_use", "timestamp": "2026-01-03", "metadata": {"feature": "export"}},
        {"user_id": 2, "event_type": "login", "timestamp": "2026-01-01", "metadata": {}},
        {"user_id": 2, "event_type": "login", "timestamp": "2026-01-02", "metadata": {}},
        {"user_id": 2, "event_type": "login", "timestamp": "2026-01-03", "metadata": {}},
        {"user_id": 2, "event_type": "login", "timestamp": "2026-01-04", "metadata": {}},
        {"user_id": 2, "event_type": "login", "timestamp": "2026-01-10", "metadata": {}},
    ])
    feedback = pd.DataFrame([
        {"user_id": 3, "text": "I love this product", "rating": 1, "timestamp": "2026-01-02"},
    ])
    users = pd.DataFrame([
        {"user_id": 1, "plan": "free", "country": "US", "cohort_label": None},
        {"user_id": 2, "plan": "pro", "country": "US", "cohort_label": None},
        {"user_id": 3, "plan": "free", "country": "US", "cohort_label": None},
    ])

    insights = generate_insights_for_window(events, feedback, users)
    types = {i["type"] for i in insights}

    assert "silent_churn_risk" in types
    assert "feature_misuse" in types
    assert "sentiment_mismatch" in types
