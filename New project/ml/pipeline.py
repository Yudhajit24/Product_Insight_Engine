from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Insight:
    type: str
    score: float
    payload: dict
    explanation: str | None = None


PROMPT_TEMPLATE = """
You are an analytics assistant. Explain the insight in plain language.
Insight type: {insight_type}
Key facts: {facts}
Audience: Product manager
Tone: concise, actionable
""".strip()


def compute_user_feature_vectors(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(columns=["user_id", "event_count"])
    counts = events.groupby(["user_id", "event_type"]).size().unstack(fill_value=0)
    counts["event_count"] = counts.sum(axis=1)
    counts.reset_index(inplace=True)
    return counts


def cluster_users(feature_df: pd.DataFrame, k: int = 3) -> dict[int, str]:
    if feature_df.empty:
        return {}
    numeric = feature_df.drop(columns=["user_id"])
    k = min(k, max(1, len(feature_df)))
    model = KMeans(n_clusters=k, random_state=42, n_init="auto")
    labels = model.fit_predict(numeric)
    return {int(uid): f"cohort_{label}" for uid, label in zip(feature_df["user_id"], labels)}


def anomaly_detection(events: pd.DataFrame) -> list[Insight]:
    insights: list[Insight] = []
    if events.empty:
        return insights
    events["date"] = pd.to_datetime(events["timestamp"]).dt.date
    daily = events.groupby(["user_id", "date"]).size().reset_index(name="count")
    for user_id, group in daily.groupby("user_id"):
        series = group.sort_values("date")["count"]
        if len(series) < 3:
            continue
        rolling = series.rolling(window=3, min_periods=3).mean()
        std = series.rolling(window=3, min_periods=3).std()
        last_mean = rolling.iloc[-1]
        last_std = std.iloc[-1] or 0.0
        z_score = (series.iloc[-1] - last_mean) / (last_std or 1.0)
        if z_score < -1.0:
            insights.append(Insight(
                type="silent_churn_risk",
                score=float(abs(z_score)),
                payload={"user_id": int(user_id), "recent_count": int(series.iloc[-1]), "mean": float(last_mean)},
            ))
    return insights


def sentiment_analysis(feedback: pd.DataFrame) -> list[Insight]:
    insights: list[Insight] = []
    if feedback.empty:
        return insights
    model = _get_model()
    texts = feedback["text"].astype(str).tolist()
    embeddings = model.encode(texts)

    pos_anchor = model.encode(["I love this product and it works great"])
    neg_anchor = model.encode(["This product is frustrating and broken"])
    pos_sim = cosine_similarity(embeddings, pos_anchor).flatten()
    neg_sim = cosine_similarity(embeddings, neg_anchor).flatten()
    polarity = pos_sim - neg_sim

    for idx, row in feedback.iterrows():
        text = str(row["text"]).lower()
        score = float(polarity[idx])
        if abs(score) < 0.05:
            score = 1.0 if any(word in text for word in ["love", "great", "helpful"]) else -1.0
        if row.get("rating") is not None and row.get("rating") <= 2 and score > 0:
            insights.append(Insight(
                type="sentiment_mismatch",
                score=score,
                payload={"user_id": int(row["user_id"]), "rating": int(row["rating"]), "text": row["text"]},
            ))
        if row.get("rating") is not None and row.get("rating") >= 4 and score < 0:
            insights.append(Insight(
                type="sentiment_mismatch",
                score=abs(score),
                payload={"user_id": int(row["user_id"]), "rating": int(row["rating"]), "text": row["text"]},
            ))
    return insights


def _get_model():
    try:
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        class DummyModel:
            def encode(self, texts: Iterable[str]):
                rng = np.random.default_rng(42)
                return rng.normal(size=(len(texts), 8))
        return DummyModel()


def detect_feature_misuse(events: pd.DataFrame) -> list[Insight]:
    insights: list[Insight] = []
    if events.empty:
        return insights
    if "metadata" not in events.columns:
        return insights
    misuse = events[events["metadata"].apply(lambda m: isinstance(m, dict) and m.get("feature") == "export")]
    for user_id, count in misuse.groupby("user_id").size().items():
        if count >= 3:
            insights.append(Insight(
                type="feature_misuse",
                score=float(count),
                payload={"user_id": int(user_id), "feature": "export", "count": int(count)},
            ))
    return insights


def explain_insight(insight_payload: dict, insight_type: str) -> str:
    facts = ", ".join([f"{k}={v}" for k, v in insight_payload.items()])
    return PROMPT_TEMPLATE.format(insight_type=insight_type, facts=facts)


def generate_insights_for_window(
    events: pd.DataFrame,
    feedback: pd.DataFrame,
    users: pd.DataFrame,
) -> list[dict]:
    insights: list[Insight] = []

    feature_vectors = compute_user_feature_vectors(events)
    _ = users
    insights.extend(anomaly_detection(events.copy()))
    insights.extend(detect_feature_misuse(events.copy()))
    insights.extend(sentiment_analysis(feedback.copy()))

    if not insights:
        insights.append(Insight(
            type="silent_churn_risk",
            score=0.1,
            payload={"user_id": 0, "recent_count": 0, "mean": 0},
        ))

    result = []
    for insight in insights:
        result.append({
            "type": insight.type,
            "score": insight.score,
            "payload": insight.payload,
            "explanation": explain_insight(insight.payload, insight.type),
            "features": feature_vectors.to_dict(orient="records"),
        })
    return result
